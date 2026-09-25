import fs from 'node:fs';
import path from 'node:path';

// Offensive-security and similarly sensitive content is opt-in: a team should
// decide deliberately before an agent gets an exploitation playbook.
const SENSITIVE = /\b(exploit|metasploit|penetration|pentest|red[- ]team|malware|phishing|c2|payload|privilege[- ]escalation|credential[- ]dump|keylogger|ransomware)\b/i;

export const DEFAULT_POLICY = { allow: [], deny: [], allowSensitive: false, maxTokens: 4000 };

// Project policy lives in `.garner.json` at the repo root.
export function loadPolicy(repoDir, overrides = {}) {
  let file = {};
  const p = repoDir && path.join(repoDir, '.garner.json');
  if (p && fs.existsSync(p)) file = JSON.parse(fs.readFileSync(p, 'utf8'));
  return { ...DEFAULT_POLICY, ...file, ...Object.fromEntries(Object.entries(overrides).filter(([, v]) => v !== undefined)) };
}

const matches = (patterns, item) =>
  patterns.some((pat) => {
    const re = new RegExp(`^${pat.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*')}$`, 'i');
    return re.test(item.name) || re.test(item.id);
  });

// Returns null when allowed, otherwise the reason it was blocked.
export function blockReason(item, policy) {
  if (matches(policy.allow, item)) return null;
  if (matches(policy.deny, item)) return 'denied by .garner.json';
  if (!policy.allowSensitive && (item.risk === 'offensive' || SENSITIVE.test(`${item.name} ${item.description}`))) {
    return 'sensitive (pass --allow-sensitive to include)';
  }
  return null;
}
