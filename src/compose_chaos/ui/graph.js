// Граф топологии compose-проекта + живые статусы узлов.
// TODO(Этап 4): заменить DEMO_ELEMENTS на GET /api/topology/{project}
// и подписаться на WebSocket /ws/runs/{run_id} для перекраски узлов:
//   зелёный — healthy, жёлтый — деградация, красный — недоступен,
//   молния (класс .attacked) — сервис под атакой.

cytoscape.use(cytoscapeDagre);

const DEMO_ELEMENTS = [
  { data: { id: 'nginx', label: 'nginx' } },
  { data: { id: 'frontend', label: 'frontend' } },
  { data: { id: 'api', label: 'api' } },
  { data: { id: 'postgres', label: 'postgres' } },
  { data: { id: 'redis', label: 'redis' } },
  { data: { id: 'worker', label: 'worker' } },
  { data: { id: 'e1', source: 'nginx', target: 'frontend' } },
  { data: { id: 'e2', source: 'frontend', target: 'api' } },
  { data: { id: 'e3', source: 'api', target: 'postgres' } },
  { data: { id: 'e4', source: 'api', target: 'redis' } },
  { data: { id: 'e5', source: 'worker', target: 'redis' } },
];

const cy = cytoscape({
  container: document.getElementById('graph'),
  elements: DEMO_ELEMENTS,
  style: [
    { selector: 'node', style: {
        'background-color': '#EFF6FF', 'border-width': 2, 'border-color': '#64748B',
        label: 'data(label)', 'text-valign': 'center', 'font-size': 12,
        shape: 'round-rectangle', padding: '8px', color: '#1F2937' } },
    { selector: 'node.attacked', style: { 'border-color': '#F59E0B', 'border-width': 3 } },
    { selector: 'node.down', style: { 'background-color': '#FEE2E2', 'border-color': '#DC2626' } },
    { selector: 'edge', style: { width: 2, 'line-color': '#94A3B8', 'target-arrow-shape': 'triangle',
        'target-arrow-color': '#94A3B8', 'curve-style': 'bezier' } },
  ],
  layout: { name: 'dagre', rankDir: 'LR', nodeSep: 40, rankSep: 70 },
  wheelSensitivity: 0.2,
});

// TODO(Этап 4): WebSocket-подписка
// const ws = new WebSocket(`ws://${location.host}/ws/runs/${runId}`);
// ws.onmessage = (msg) => { const ev = JSON.parse(msg.data); paintNode(ev); };
