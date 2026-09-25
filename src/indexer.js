import fs from 'node:fs';
import path from 'node:path';
import { parseFrontmatter } from './frontmatter.js';

const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '__pycache__']);
const NON_AGENT_FILES = new Set(['readme.md', 'changelog.md', 'license.md', 'skill.md', 'index.md']);

// Rough token estimate: ~4 characters per token for English prose.
export const estimateTokens = (s) => Math.ceil((s || '').length / 4);

function* walk(dir) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name)) yield* walk(p);
    } else if (e.isFile()) {
      yield p;
    }
  }
}

// First chunk of the body, with markdown noise stripped, used as extra ranking text.
function summarizeBody(body) {
  return body
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[#>*_`|[\]()-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 600);
}

function entry(kind, file, text, root) {
  const { data, body } = parseFrontmatter(text);
  if (!data.name || !data.description) return null;
  const rel = path.relative(root, file);
  return {
    id: `${kind}:${data.name}`,
    kind,
    name: String(data.name),
    description: String(data.description),
    category: data.category || rel.split(path.sep)[0] || '',
    risk: data.risk || '',
    tools: Array.isArray(data.tools) ? data.tools : undefined,
    path: file,
    dir: kind === 'skill' ? path.dirname(file) : undefined,
    excerpt: summarizeBody(body),
    descTokens: estimateTokens(`${data.name}: ${data.description}`),
    bodyTokens: estimateTokens(body),
  };
}

export function scanSkills(root) {
  const out = [];
  for (const file of walk(root)) {
    if (path.basename(file) !== 'SKILL.md') continue;
    const e = entry('skill', file, fs.readFileSync(file, 'utf8'), root);
    if (e) out.push(e);
  }
  return out;
}

export function scanAgents(root) {
  const out = [];
  for (const file of walk(root)) {
    if (!file.endsWith('.md') || NON_AGENT_FILES.has(path.basename(file).toLowerCase())) continue;
    const e = entry('agent', file, fs.readFileSync(file, 'utf8'), root);
    if (e) out.push(e);
  }
  return out;
}

// A library root holds `skills/` and/or `agents/`; either may be passed directly too.
export function buildIndex({ libs = [], skills = [], agents = [] }) {
  for (const lib of libs) {
    const s = path.join(lib, 'skills');
    const a = path.join(lib, 'agents');
    if (fs.existsSync(s)) skills.push(s);
    if (fs.existsSync(a)) agents.push(a);
  }
  const items = [...skills.flatMap((d) => scanSkills(path.resolve(d))), ...agents.flatMap((d) => scanAgents(path.resolve(d)))];

  // Keep the first occurrence of each id; libraries often ship duplicates.
  const seen = new Map();
  for (const it of items) if (!seen.has(it.id)) seen.set(it.id, it);
  return { version: 1, builtAt: new Date().toISOString(), items: [...seen.values()] };
}
