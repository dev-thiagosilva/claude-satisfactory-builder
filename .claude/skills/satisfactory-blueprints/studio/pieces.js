// Simple shapes for Satisfactory pieces, shared by the studio (index.html) and the map (map.html).
import * as THREE from 'three';

// Geometry in Unreal local space (cm). Instance matrices convert to metres / Y-up.
export function box(sx, sy, sz, ox = 0, oy = 0, oz = 0) { const g = new THREE.BoxGeometry(sx, sy, sz); g.translate(ox, oy, oz); return g; }
export function quarterPipe(width, radius) {
  const seg = 12, th = 20, pos = [], idx = [];
  for (let i = 0; i <= seg; i++) {
    const a = (i / seg) * Math.PI / 2;
    for (const r of [radius, radius - th]) {
      const x = radius / 2 - r * Math.cos(a), z = -radius / 2 + r * Math.sin(a);
      pos.push(x, -width / 2, z, x, width / 2, z);
    }
  }
  for (let i = 0; i < seg; i++) { const b = i * 4, n = b + 4;
    idx.push(b, b + 1, n + 1, b, n + 1, n, b + 2, n + 2, n + 3, b + 2, n + 3, b + 3, b, n, n + 2, b, n + 2, b + 2, b + 1, b + 3, n + 3, b + 1, n + 3, n + 1); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  return g;
}
export function geometryFor(type, boxes) {
  const bx = boxes && boxes[type];   // [minX, minY, minZ, maxX, maxY, maxZ] cm, e.g. machine clearance
  if (bx) return { geo: box(bx[3] - bx[0], bx[4] - bx[1], bx[5] - bx[2], (bx[0] + bx[3]) / 2, (bx[1] + bx[4]) / 2, (bx[2] + bx[5]) / 2) };
  const m = type.match(/(\d+)x(\d+)/), w = m ? +m[1] * 100 : 400, h = m ? +m[2] * 100 : 400;
  if (/^QuarterPipe/.test(type)) return { geo: quarterPipe(w, h) };
  if (/PowerLine|Wire/.test(type)) return { geo: box(1, 12, 12, 0.5), stretch: true };
  if (/RailroadTrack/.test(type)) return { geo: box(1, 300, 30, 0.5), stretch: true };
  if (/PipeHyper$/.test(type)) return { geo: box(1, 120, 120, 0.5), stretch: true };
  if (/Beam|Pipeline|Conveyor|Belt/.test(type)) return { geo: box(1, 50, 50, 0.5), stretch: true };
  if (/Window|Glass/.test(type) && /Wall/.test(type)) return { geo: box(20, w, h, 0, 0, h / 2), glass: true };
  if (/Wall|Fence|Railing/.test(type)) return { geo: box(20, w, h, 0, 0, h / 2) };
  if (/Foundation|Ramp|Roof|Floor/.test(type)) return { geo: box(w, w, h), glass: /Glass/.test(type) };
  if (/Pillar/.test(type)) return { geo: box(70, 70, 100, 0, 0, 50) };
  return { geo: box(400, 400, 400, 0, 0, 200) };
}
export const SLOT = { Slot0: '#f39c3c', Slot1: '#6b7894', Slot2: '#3f8f6b', Slot16: '#d0d0d0', Concrete: '#b9b4a9' };
export const colorOf = p => p.color || (p.paint && p.paint.startsWith('#') ? p.paint : SLOT[p.paint] || '#8a8a8a');

// Unreal (cm, Z-up, left-handed) -> three.js (m, Y-up): swap Y/Z rows (a mirror, so double-sided materials).
const _m = new THREE.Matrix4();
export function matrixOf(p, out = _m) {
  const [x, y, z, w] = p.rot, s = p.scale ? [...p.scale] : [1, 1, 1];
  if (p.len) s[0] *= p.len;
  const R = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
             [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
             [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]];
  const M = R.map(r => r.map((v, j) => v * s[j] * 0.01));
  const t = p.pos.map(v => v * 0.01);
  return out.set(M[0][0], M[0][1], M[0][2], t[0], M[2][0], M[2][1], M[2][2], t[2], M[1][0], M[1][1], M[1][2], t[1], 0, 0, 0, 1);
}
