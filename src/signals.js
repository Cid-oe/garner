import fs from 'node:fs';
import path from 'node:path';

const EXT_LANG = {
  '.ts': 'typescript', '.tsx': 'react typescript', '.js': 'javascript', '.jsx': 'react javascript',
  '.py': 'python', '.go': 'golang', '.rs': 'rust', '.java': 'java', '.kt': 'kotlin', '.swift': 'swift',
  '.rb': 'ruby', '.php': 'php', '.cs': 'csharp dotnet', '.cpp': 'cpp', '.c': 'c', '.scala': 'scala',
  '.cbl': 'cobol mainframe', '.cob': 'cobol mainframe', '.jcl': 'jcl mainframe', '.rpgle': 'rpg ibmi',
  '.sql': 'sql database', '.tf': 'terraform infrastructure', '.vue': 'vue', '.svelte': 'svelte',
  '.dart': 'flutter dart', '.ipynb': 'jupyter python data', '.sol': 'solidity smart-contract',
};

const MARKERS = [
  ['Dockerfile', 'docker container'],
  ['docker-compose.yml', 'docker compose'],
  ['.github/workflows', 'github actions ci'],
  ['k8s', 'kubernetes'],
  ['helm', 'kubernetes helm'],
  ['prisma', 'prisma database'],
  ['requirements.txt', 'python'],
  ['pyproject.toml', 'python'],
  ['go.mod', 'golang'],
  ['Cargo.toml', 'rust'],
  ['pom.xml', 'java maven'],
  ['build.gradle', 'java gradle'],
  ['next.config.js', 'nextjs react'],
  ['next.config.mjs', 'nextjs react'],
  ['vite.config.ts', 'vite frontend'],
  ['playwright.config.ts', 'playwright e2e testing'],
  ['.bob', 'ibm bob'],
];

const NOTABLE_DEPS = [
  'react', 'next', 'vue', 'svelte', 'angular', 'express', 'fastify', 'nestjs', 'prisma', 'drizzle', 'mongoose',
  'graphql', 'tailwindcss', 'stripe', 'supabase', 'firebase', 'openai', 'anthropic', 'langchain', 'jest', 'vitest',
  'playwright', 'cypress', 'electron', 'react-native', 'expo', 'three', 'django', 'flask', 'fastapi', 'pandas',
  'torch', 'tensorflow', 'sqlalchemy', 'pydantic', 'ibm-watsonx-ai', 'watsonx',
];

const MAX_FILES = 4000;

// Returns a short string of terms describing the repo's stack, plus the raw facts for display.
export function repoSignals(repoDir) {
  if (!repoDir || !fs.existsSync(repoDir)) return { terms: '', facts: [] };
  const facts = new Set();
  const langCounts = {};
  let seen = 0;

  const walk = (dir, depth) => {
    if (depth > 6 || seen > MAX_FILES) return;
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.name === 'node_modules' || e.name === '.git' || e.name === 'dist' || e.name === 'vendor') continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p, depth + 1);
      else if (++seen <= MAX_FILES) {
        const lang = EXT_LANG[path.extname(e.name).toLowerCase()];
        if (lang) langCounts[lang] = (langCounts[lang] || 0) + 1;
      }
    }
  };
  walk(repoDir, 0);

  // Languages that make up at least 5% of recognised files.
  const total = Object.values(langCounts).reduce((a, b) => a + b, 0) || 1;
  for (const [lang, n] of Object.entries(langCounts)) if (n / total >= 0.05) facts.add(lang);

  for (const [marker, terms] of MARKERS) if (fs.existsSync(path.join(repoDir, marker))) facts.add(terms);

  const pkgPath = path.join(repoDir, 'package.json');
  if (fs.existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });
      for (const d of deps) {
        const bare = d.replace(/^@[^/]+\//, '');
        if (NOTABLE_DEPS.includes(d) || NOTABLE_DEPS.includes(bare)) facts.add(bare);
      }
    } catch {
      /* unreadable package.json: ignore */
    }
  }

  const list = [...facts];
  return { terms: list.join(' '), facts: list };
}
