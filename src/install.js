import fs from 'node:fs';
import path from 'node:path';
import { parseFrontmatter, toFrontmatter } from './frontmatter.js';

export const LOCKFILE = '.garner.lock.json';

// Where each runtime looks for skills and subagents. Bob reads skills from
// `.bob/skills/<name>/SKILL.md`; its subagents are spawned by Bob itself, so
// agent personas are installed as skills it can activate.
export const TARGETS = {
  bob: { skills: '.bob/skills', agents: null },
  claude: { skills: '.claude/skills', agents: '.claude/agents' },
};

// Generic tool names used by many agent libraries -> Claude Code tool names.
const CLAUDE_TOOLS = {
  read_file: 'Read', write_file: 'Write', edit_file: 'Edit', glob: 'Glob', grep: 'Grep', list_dir: 'Glob',
  run_shell_command: 'Bash', shell: 'Bash', bash: 'Bash', web_fetch: 'WebFetch', web_search: 'WebSearch',
};

export const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 64) || 'unnamed';

function readLock(repo) {
  const p = path.join(repo, LOCKFILE);
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : { installed: [] };
}

function mapClaudeTools(tools) {
  if (!tools) return undefined;
  const mapped = [...new Set(tools.map((t) => (t.startsWith('mcp__') ? t : CLAUDE_TOOLS[t])).filter(Boolean))];
  // Nothing recognisable: omit the field so the agent inherits the default tool set.
  return mapped.length ? mapped : undefined;
}

function agentAsSkill(item) {
  const { body } = parseFrontmatter(fs.readFileSync(item.path, 'utf8'));
  const header = toFrontmatter({ name: slug(item.name), description: item.description });
  return `${header}\n# ${item.name}\n\nAdopt this specialist role for the current task (or hand it to a subagent).\n\n${body.trim()}\n`;
}

function agentForClaude(item) {
  const { data, body } = parseFrontmatter(fs.readFileSync(item.path, 'utf8'));
  const fm = { name: slug(item.name), description: item.description, tools: mapClaudeTools(data.tools) };
  if (['opus', 'sonnet', 'haiku', 'inherit'].includes(data.model)) fm.model = data.model;
  return `${toFrontmatter(fm)}\n${body.trim()}\n`;
}

// Installs a selection into `repo` for `target`. Paths not previously created by
// garner are never overwritten unless `force` is set.
export function install(repo, selection, { target = 'bob', force = false, task = '' } = {}) {
  const t = TARGETS[target];
  if (!t) throw new Error(`unknown target "${target}" (expected: ${Object.keys(TARGETS).join(', ')})`);
  const lock = readLock(repo);
  const owned = new Set(lock.installed.map((e) => e.path));
  const written = [];
  const skipped = [];

  const place = (rel, write) => {
    const abs = path.join(repo, rel);
    if (fs.existsSync(abs) && !owned.has(rel) && !force) {
      skipped.push({ path: rel, reason: 'exists and not managed by garner' });
      return;
    }
    fs.rmSync(abs, { recursive: true, force: true });
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    write(abs);
    written.push(rel);
  };

  for (const s of selection.skills) {
    place(path.join(t.skills, slug(s.name)), (abs) => fs.cpSync(s.dir, abs, { recursive: true }));
  }
  for (const a of selection.agents) {
    if (t.agents) {
      place(path.join(t.agents, `${slug(a.name)}.md`), (abs) => fs.writeFileSync(abs, agentForClaude(a)));
    } else {
      place(path.join(t.skills, `agent-${slug(a.name)}`), (abs) => {
        fs.mkdirSync(abs, { recursive: true });
        fs.writeFileSync(path.join(abs, 'SKILL.md'), agentAsSkill(a));
      });
    }
  }

  // A new garner replaces the previous one: drop what is no longer selected.
  const removed = [];
  for (const e of lock.installed) {
    if (written.includes(e.path)) continue;
    fs.rmSync(path.join(repo, e.path), { recursive: true, force: true });
    removed.push(e.path);
  }
  const now = new Date().toISOString();
  const next = { task, target, updatedAt: now, installed: written.map((p) => ({ path: p, target, at: now })) };
  fs.writeFileSync(path.join(repo, LOCKFILE), JSON.stringify(next, null, 2) + '\n');
  return { written, skipped, removed };
}

// Removes everything garner installed, and nothing else.
export function clean(repo) {
  const lock = readLock(repo);
  const removed = [];
  for (const e of lock.installed) {
    const abs = path.join(repo, e.path);
    if (fs.existsSync(abs)) {
      fs.rmSync(abs, { recursive: true, force: true });
      removed.push(e.path);
    }
  }
  fs.rmSync(path.join(repo, LOCKFILE), { force: true });
  return removed;
}
