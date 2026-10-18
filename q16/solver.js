import fs from "fs";
import { TANGRAM_CONFIG, tangramPolygons, tangramAdapter } from "./tangram_engine/games/tangram/adapter.js";
import { algValue } from "./tangram_engine/games/tangram/algebraic.js";
import { computeMatchKey } from "./tangram_engine/visual/kernel.js";

const mask = JSON.parse(fs.readFileSync("q16/target_mask.json", "utf-8"));

function isInside(bx, by) {
  const px = Math.round(bx * 32);
  const py = Math.round((18 - by) * 32);
  for (let dy = -2; dy <= 2; dy++) {
    const runs = mask[py + dy];
    if (runs && runs.some(([s, e]) => px >= s - 3 && px <= e + 3)) return true;
  }
  return false;
}

// Generate candidate poses for a piece
function getValidPoses(pieceId, fixedPieces) {
  const poses = [];
  // For small-a and small-b, steps of 4 (1/4 unit)
  // Coordinates in range [16..160]
  for (let o = 0; o < 8; o++) {
    for (let tx = 16; tx <= 160; tx += 4) {
      for (let ty = 16; ty <= 160; ty += 4) {
        const candidate = { id: pieceId, x: tx, y: ty, orientation: o, reflected: false };
        const polys = tangramPolygons({ pieces: [candidate] }, TANGRAM_CONFIG);
        const pts = polys[0].vertices.map(v => [algValue(v.x), algValue(v.y)]);
        const cx = pts.reduce((sum, p) => sum + p[0], 0) / pts.length;
        const cy = pts.reduce((sum, p) => sum + p[1], 0) / pts.length;
        
        if (isInside(cx, cy) && pts.every(([x, y]) => isInside(x, y))) {
          // Check collision with already placed pieces
          const state = { pieces: [...fixedPieces, candidate] };
          const val = tangramAdapter.validate(state, TANGRAM_CONFIG);
          if (!val.invalid) {
            poses.push(candidate);
          }
        }
      }
    }
  }
  return poses;
}

// Pre-place large-a and parallelogram
const base = [
  { id: "large-a", x: 48, y: 80, orientation: 6, reflected: false },
  { id: "parallelogram", x: 80, y: 80, orientation: 0, reflected: true }
];

console.log("Starting search with base pieces:", base);

const remaining = ["large-b", "medium", "square", "small-a", "small-b"];

let solutions = [];

function search(depth, currentPieces) {
  if (depth === remaining.length) {
    console.log("🎉 ALL 7 PIECES PLACED!");
    solutions.push([...currentPieces]);
    return true;
  }

  const pieceId = remaining[depth];
  const candidates = getValidPoses(pieceId, currentPieces);
  // console.log(`Depth ${depth} (${pieceId}): ${candidates.length} valid poses`);

  for (const c of candidates) {
    if (pieceId === "small-b") {
      const smallA = currentPieces.find(p => p.id === "small-a");
      if (smallA && (c.x < smallA.x || (c.x === smallA.x && c.y < smallA.y))) {
        continue; // Symmetry breaking
      }
    }
    const found = search(depth + 1, [...currentPieces, c]);
    if (found && solutions.length >= 1) return true;
  }
  return false;
}

search(0, base);

if (solutions.length > 0) {
  const sol = solutions[0];
  console.log("\n================ SOLUTION FOUND ================");
  console.log(JSON.stringify(sol, null, 2));

  // Compute match key
  const finalState = { pieces: sol };
  computeMatchKey(tangramAdapter, finalState, TANGRAM_CONFIG).then(key => {
    console.log("MATCH KEY:", key);
    fs.writeFileSync("q16/solution.json", JSON.stringify({ state: sol, matchKey: key }, null, 2));
  });
} else {
  console.log("No solution found.");
}

