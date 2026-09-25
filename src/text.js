const STOP = new Set(
  ('a an and are as at be by can do for from has have how i in into is it its me my of on or our so that the their them then this to ' +
    'use used uses using want we when which will with you your any all also about add make need needs should via etc e g ie ' +
    'skill skills agent agents specialist expert help helps task tasks work working code').split(' '),
);

// Small domain synonym map so "auth" finds "authentication", "k8s" finds "kubernetes", etc.
const SYNONYMS = {
  auth: ['authentication', 'authorization', 'login', 'oauth', 'jwt', 'session'],
  login: ['auth', 'authentication'],
  test: ['testing', 'tdd', 'unit', 'e2e'],
  tests: ['testing', 'tdd'],
  k8s: ['kubernetes'],
  db: ['database', 'sql'],
  postgres: ['postgresql', 'database', 'sql'],
  perf: ['performance', 'optimization'],
  slow: ['performance', 'optimization', 'profiling'],
  ui: ['frontend', 'interface', 'design'],
  ux: ['usability', 'design', 'frontend'],
  docs: ['documentation'],
  ci: ['pipeline', 'github', 'actions', 'cicd'],
  cd: ['deployment', 'cicd'],
  deploy: ['deployment', 'release'],
  vuln: ['vulnerability', 'security'],
  secure: ['security'],
  bug: ['debugging', 'fix'],
  debug: ['debugging', 'bug'],
  refactor: ['refactoring', 'cleanup', 'tech-debt'],
  legacy: ['modernization', 'migration', 'refactoring'],
  cobol: ['mainframe', 'legacy', 'modernization'],
  mainframe: ['cobol', 'zos', 'legacy'],
  llm: ['ai', 'prompt', 'rag', 'agent'],
  rag: ['retrieval', 'embeddings', 'vector'],
  api: ['rest', 'endpoint', 'http'],
  migrate: ['migration', 'upgrade'],
};

export function stem(w) {
  if (w.length <= 4) return w;
  return w
    .replace(/(ies)$/, 'y')
    .replace(/(ing|ed|es|s)$/, '')
    .replace(/(ation)$/, 'ate');
}

export function tokenize(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[^a-z0-9+#.\s-]/g, ' ')
    .split(/[\s./-]+/)
    .filter((w) => w.length > 1 && !STOP.has(w))
    .map(stem);
}

export function expandQuery(text) {
  const base = (text || '').toLowerCase().split(/[^a-z0-9+#]+/).filter(Boolean);
  const extra = base.flatMap((w) => SYNONYMS[w] || []);
  return { primary: tokenize(text), expanded: tokenize(extra.join(' ')) };
}
