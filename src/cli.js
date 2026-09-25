#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { buildIndex } from './indexer.js';
import { createRanker, select } from './rank.js';
import { repoSignals } from './signals.js';
import { loadPolicy } from './policy.js';
import { install, clean, TARGETS } from './install.js';

const HELP = `garner: give your coding agent the right few skills, not all of them.

Usage:
  garner index --lib <dir> [--skills <dir>] [--agents <dir>]   Build the library index
  garner pick "<task>" [--repo .]                              Show what would be loaded
  garner install "<task>" [--repo .] [--target bob|claude]     Install the garner into a repo
  garner clean [--repo .]                                      Remove everything garner installed
  garner stats                                                 Library size and context cost

Options:
  --skills-max <n>     Skills to select (default 6)
  --agents-max <n>     Agent personas to select (default 3)
  --allow-sensitive    Allow offensive-security content
  --force              Overwrite files garner did not create
  --index <file>       Index location (default: $GARNER_INDEX or ~/.garner/index.json)
  --json               Machine-readable output
`;

const FLAGS = new Set(['json', 'force', 'allow-sensitive', 'help']);

function parseArgs(argv) {
  const args = { _: [], lib: [], skills: [], agents: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) {
      args._.push(a);
      continue;
    }
    const key = a.slice(2);
    if (FLAGS.has(key)) args[key] = true;
    else if (Array.isArray(args[key])) args[key].push(argv[++i]);
    else args[key] = argv[++i];
  }
  return args;
}

const indexPath = (args) => path.resolve(args.index || process.env.GARNER_INDEX || path.join(os.homedir(), '.garner', 'index.json'));

function loadIndex(args) {
  const p = indexPath(args);
  if (!fs.existsSync(p)) throw new Error(`no index at ${p}; run: garner index --lib <library-dir>`);
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function choose(args) {
  const task = args._.slice(1).join(' ').trim();
  if (!task) throw new Error('describe the task, e.g. garner pick "add OAuth login and tests"');
  const repo = path.resolve(args.repo || '.');
  const index = loadIndex(args);
  const signals = repoSignals(repo);
  const policy = loadPolicy(repo, { allowSensitive: args['allow-sensitive'] || undefined });
  const ranked = createRanker(index.items)(task, { repoTerms: signals.terms });
  const selection = select(ranked, {
    skills: Number(args['skills-max'] ?? 6),
    agents: Number(args['agents-max'] ?? 3),
    policy,
  });
  const libraryTokens = index.items.reduce((a, it) => a + it.descTokens, 0);
  return { task, repo, signals, selection, libraryTokens, librarySize: index.items.length };
}

function printSelection({ task, signals, selection, libraryTokens, librarySize }) {
  console.log(`Task:  ${task}`);
  if (signals.facts.length) console.log(`Stack: ${signals.facts.join(', ')}`);
  const row = (it) => `  ${it.score.toFixed(2).padStart(6)}  ${it.name.padEnd(36)} ${it.description.replace(/\s+/g, ' ').slice(0, 70)}`;
  console.log(`\nSkills (${selection.skills.length}):`);
  selection.skills.forEach((it) => console.log(row(it)));
  console.log(`\nAgents (${selection.agents.length}):`);
  selection.agents.forEach((it) => console.log(row(it)));
  if (selection.blocked.length) {
    console.log('\nBlocked by policy:');
    selection.blocked.forEach((b) => console.log(`  ${b.name}: ${b.reason}`));
  }
  const pct = libraryTokens ? (100 * (1 - selection.tokens / libraryTokens)).toFixed(1) : '0';
  console.log(`\nAlways-on context: ${selection.tokens} tokens for this garner vs ${libraryTokens.toLocaleString()} to load all ${librarySize.toLocaleString()} items (${pct}% saved)`);
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const cmd = args._[0];
  if (!cmd || args.help) return console.log(HELP);

  if (cmd === 'index') {
    if (!args.lib.length && !args.skills.length && !args.agents.length) throw new Error('pass --lib, --skills or --agents');
    const index = buildIndex({ libs: args.lib, skills: args.skills, agents: args.agents });
    const out = indexPath(args);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(index));
    const n = (k) => index.items.filter((i) => i.kind === k).length;
    console.log(`Indexed ${n('skill')} skills and ${n('agent')} agents -> ${out}`);
  } else if (cmd === 'pick') {
    const result = choose(args);
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else printSelection(result);
  } else if (cmd === 'install') {
    const result = choose(args);
    const target = args.target || 'bob';
    if (!TARGETS[target]) throw new Error(`unknown target "${target}"`);
    const report = install(result.repo, result.selection, { target, force: args.force, task: result.task });
    if (args.json) return console.log(JSON.stringify({ ...result, ...report }, null, 2));
    printSelection(result);
    console.log(`\nInstalled into ${target}:`);
    report.written.forEach((p) => console.log(`  + ${p}`));
    report.removed.forEach((p) => console.log(`  - ${p}`));
    report.skipped.forEach((s) => console.log(`  ! ${s.path} (${s.reason})`));
  } else if (cmd === 'clean') {
    const removed = clean(path.resolve(args.repo || '.'));
    console.log(removed.length ? removed.map((p) => `  - ${p}`).join('\n') : 'Nothing to clean.');
  } else if (cmd === 'stats') {
    const index = loadIndex(args);
    const sum = (k, f) => index.items.filter((i) => i.kind === k).reduce((a, i) => a + i[f], 0);
    const count = (k) => index.items.filter((i) => i.kind === k).length;
    console.log(`Skills: ${count('skill')}  (descriptions ${sum('skill', 'descTokens').toLocaleString()} tokens, bodies ${sum('skill', 'bodyTokens').toLocaleString()})`);
    console.log(`Agents: ${count('agent')}  (descriptions ${sum('agent', 'descTokens').toLocaleString()} tokens, bodies ${sum('agent', 'bodyTokens').toLocaleString()})`);
  } else {
    throw new Error(`unknown command "${cmd}"\n\n${HELP}`);
  }
}

if (import.meta.url === `file://${fs.realpathSync(process.argv[1])}`) {
  try {
    main();
  } catch (err) {
    console.error(`garner: ${err.message}`);
    process.exit(1);
  }
}
