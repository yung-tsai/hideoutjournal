/* Shrink Poly Haven rock sets (glTF 1k) for the stream: weld, simplify to ~4% of the triangles, keep only the colour
   texture (512px WebP; the scene's own lighting ignores normal and roughness maps), quantize the vertices, and write
   one small GLB per set.
   npm i @gltf-transform/core @gltf-transform/functions @gltf-transform/extensions meshoptimizer sharp
   node tools/shrink_rocks.mjs <in.gltf> <out.glb> */
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {weld, simplify, prune, dedup, quantize, textureCompress} from '@gltf-transform/functions';
import {MeshoptSimplifier} from 'meshoptimizer';
import sharp from 'sharp';

const [src, out] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(src);
for (const m of doc.getRoot().listMaterials()) {
  m.setNormalTexture(null); m.setMetallicRoughnessTexture(null); m.setOcclusionTexture(null);
  m.setMetallicFactor(0); m.setRoughnessFactor(1);
}
await doc.transform(
  weld(),
  simplify({simplifier: MeshoptSimplifier, ratio: 0.04, error: 0.01}),
  prune(), dedup(), quantize(),
  textureCompress({encoder: sharp, targetFormat: 'webp', resize: [512, 512], quality: 80}),
);
await io.write(out, doc);
console.log(out, 'ok');
