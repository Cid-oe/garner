import { tokenize, expandQuery } from './text.js';
import { blockReason } from './policy.js';

const K1 = 1.2;
const B = 0.75;

// Vendor/platform words. An item named after a platform the task and repo never
// mention (e.g. "azure-eventhub-java" for a plain Java task) is usually noise.
const PLATFORMS = new Set(
  ('azure aws gcp google firebase supabase vercel netlify heroku cloudflare odoo drupal wordpress shopify salesforce ' +
    'hubspot notion slack discord stripe twilio sendgrid jira linear zapier airtable figma odata sap oracle databricks ' +
    'snowflake unity unreal godot roblox minecraft telegram whatsapp').split(' '),
);
const PLATFORM_PENALTY = 0.4;
const NAME_BONUS = 2;

// Field weights: a hit in the name counts more than one in the body excerpt.
function docTokens(item) {
  const name = tokenize(item.name.replace(/[-_]/g, ' '));
  const desc = tokenize(item.description);
  return [...name, ...name, ...name, ...desc, ...desc, ...tokenize(item.category), ...tokenize(item.excerpt)];
}

export function createRanker(items) {
  const docs = items.map((item) => {
    const toks = docTokens(item);
    const tf = new Map();
    for (const t of toks) tf.set(t, (tf.get(t) || 0) + 1);
    const nameToks = [...new Set(tokenize(item.name.replace(/[-_]/g, ' ')))];
    const platforms = nameToks.filter((t) => PLATFORMS.has(t));
    return { item, tf, len: toks.length, set: new Set(toks), platforms, nameToks };
  });
  const df = new Map();
  for (const d of docs) for (const t of d.set) df.set(t, (df.get(t) || 0) + 1);
  const N = docs.length || 1;
  const avgLen = docs.reduce((a, d) => a + d.len, 0) / N || 1;
  const idf = (t) => Math.log(1 + (N - (df.get(t) || 0) + 0.5) / ((df.get(t) || 0) + 0.5));

  // Per-term BM25 contributions, so selection can reason about coverage.
  function contributions(doc, weighted) {
    const out = new Map();
    for (const [t, w] of weighted) {
      const f = doc.tf.get(t);
      if (!f) continue;
      out.set(t, w * idf(t) * ((f * (K1 + 1)) / (f + K1 * (1 - B + (B * doc.len) / avgLen))));
    }
    return out;
  }

  return function rank(task, { repoTerms = '' } = {}) {
    const { primary, expanded } = expandQuery(task);
    const repo = tokenize(repoTerms);
    const weighted = new Map();
    const add = (toks, w) => toks.forEach((t) => weighted.set(t, Math.max(weighted.get(t) || 0, w)));
    add(repo, 0.3);
    add(expanded, 0.5);
    add(primary, 1);
    const mentioned = new Set([...primary, ...repo]);
    const primarySet = new Set(primary);
    // Terms from the task itself (not just the repo's stack) drive coverage.
    const taskTerms = new Set([...primary, ...expanded]);

    const results = [];
    for (const d of docs) {
      const contrib = contributions(d, weighted);
      if (!contrib.size) continue;
      // Items whose name is mostly made of task words ("security-review" for a
      // security review) are what the user meant, even when the words are common.
      const hits = d.nameToks.filter((t) => primarySet.has(t));
      if (hits.length) {
        const share = hits.length / d.nameToks.length;
        for (const t of hits) contrib.set(t, contrib.get(t) + NAME_BONUS * share * idf(t));
      }
      const factor = d.platforms.some((p) => !mentioned.has(p)) ? PLATFORM_PENALTY : 1;
      if (factor !== 1) for (const [t, v] of contrib) contrib.set(t, v * factor);
      let score = 0;
      for (const v of contrib.values()) score += v;
      results.push({ item: d.item, score, contrib, set: d.set, taskTerms });
    }
    return results.sort((a, b) => b.score - a.score);
  };
}

const jaccard = (a, b) => {
  let inter = 0;
  for (const t of a) if (b.has(t)) inter++;
  return inter / (a.size + b.size - inter || 1);
};

// Once a query term is covered by a pick, further hits on it are worth this much.
const COVERED_WEIGHT = 0.35;
const POOL = 300;

// Greedy selection: each round takes the candidate that adds the most *new*
// coverage of the task, skipping blocked items, near-duplicates, and anything
// far weaker than the best match.
export function select(ranked, { skills = 6, agents = 3, policy, minRelative = 0.4, minGain = 0.4, maxOverlap = 0.55 }) {
  const quota = { skill: skills, agent: agents };
  const picked = { skill: [], agent: [] };
  const blocked = [];
  let tokens = 0;

  for (const kind of ['skill', 'agent']) {
    const pool = [];
    for (const r of ranked) {
      if (r.item.kind !== kind) continue;
      const reason = policy && blockReason(r.item, policy);
      if (reason) {
        if (blocked.length < 5) blocked.push({ name: r.item.name, kind, reason });
        continue;
      }
      pool.push({ ...r, taken: false });
      if (pool.length >= POOL) break;
    }
    if (!pool.length) continue;
    const floor = pool[0].score * minRelative;
    const covered = new Set();
    let firstGain = 0;

    while (picked[kind].length < quota[kind]) {
      let best = null;
      let bestGain = 0;
      for (const r of pool) {
        if (r.score < floor || r.taken) continue;
        let gain = 0;
        for (const [t, v] of r.contrib) gain += covered.has(t) || !r.taskTerms.has(t) ? v * COVERED_WEIGHT : v;
        if (gain > bestGain) {
          best = r;
          bestGain = gain;
        }
      }
      // Stop instead of padding the quota with weak, off-topic matches.
      if (!best || bestGain < firstGain * minGain) break;
      best.taken = true;
      if (picked[kind].some((p) => jaccard(p.set, best.set) > maxOverlap)) continue;
      if (policy && tokens + best.item.descTokens > policy.maxTokens) continue;
      tokens += best.item.descTokens;
      firstGain ||= bestGain;
      for (const t of best.contrib.keys()) covered.add(t);
      picked[kind].push(best);
    }
  }

  const strip = ({ item, score }) => ({ ...item, score: Number(score.toFixed(2)) });
  return { skills: picked.skill.map(strip), agents: picked.agent.map(strip), blocked, tokens };
}
