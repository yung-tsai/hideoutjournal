# Hideout Journal

A calm journaling web app. The default backdrop is **the stream**: a 3D golden-hour valley (three.js) shown as a postcard on a white page. The original early-90s Amiga-style pixel-art river camp with a retro van is still there as a choice in Settings > Scene. You write (or talk), save the entry, and it shows up in Journal (formerly Memories), Patterns (mood over time) and Tasks. Everything runs in the browser; entries live in localStorage under `talio-home-v1` (the old working name was Talio). There is no backend yet.

The owner is Kyoto88. They are a designer, not an engineer: explain choices in plain words, show screenshots of visual changes, and ask before big design decisions. **Ask permission before implementing, writing code, or doing work that uses credits; answer questions without starting to build.** They like a minimal, icon-led, calm UI.

## Deploy

- GitHub `yung-tsai/hideoutjournal` → Vercel. Pushing to `main` redeploys automatically.
- Vercel serves the committed `index.html` as a static file (no build step on Vercel). **Always run `python3 build.py` and commit the new `index.html` with your source changes.**
- `vercel.json` sets `Permissions-Policy: microphone=(self)` (live voice needs it) and `Cache-Control: no-cache`.

## Build

```
pip install pillow            # once
python3 build.py              # → index.html (~12.8 MB, all art and sound inlined) + a node --check of the classic script
```

`build.py` runs `src/assemble.py`, which writes `build/fragment.html` and then runs each pass over it, in this order:

theme → journal → burn → bundle → sound → van → safety → patterns → field → write → card → voice → tasks → stream3d

- `assemble.py` combines the base app (`assets/talio-home-v6-3d.html`, the older UI) with the 2D scene engine (`src/scene2d.js`) and inlines the art.
- Each pass is a Python script `python3 src/<pass>.py in out` that patches the HTML with `rep(a, b, n=1)`. `rep` **asserts the exact number of matches** and exits on a mismatch, so an earlier pass changing a string breaks a later pass loudly. That's on purpose. When you change a pass, keep later passes' anchors intact, or update them.
- Later passes patch the output of earlier ones, so the newest behaviour of a feature is often in a later file (the writing card: write.py then card.py; voice: voice.py replaces LiveTranscriber; the stream: stream3d.py is last).
- New work: edit the pass that owns the feature, or add a new pass at the end of the list in `assemble.py`. Keep the docstring at the top of each pass describing what it changes and why.

### The stream (3D)

- `src/stream3d.js` is the three.js scene module. `src/stream3d.py` (the last pass) injects it with an import map (three@0.160.0 from jsDelivr) and adds: Settings > Scene (The stream / River camp), the Postcard frame switch, the light UI over the postcard, the logo (`assets/logo/hideout_logo.png`), the plain on/off volume icon, the header layout, and the Memories → Journal rename. `body[data-scene]` (stream|camp) and `body[data-frame]` (postcard|full) drive it. The 2D camp stops drawing while the stream shows.
- The scene was designed in the standalone page `prototypes/stream.html` (it has its own simple UI and runs on its own). To change the scene, edit that page, check it, then regenerate the module with `tools/make_stream_module.py` (fix its paths first; it was written for the original workspace). Or edit `src/stream3d.js` directly.
- Trees are cut-outs: 8 photos each of 7 trees (8 rows; row 7 is free) packed into one image inside the module, all baked by `tools/bake_trees.html` (`?from=4` bakes only the Poly Haven rows). Row 0 Poly Haven's Jacaranda; rows 1–3 oak, poplar, willow grown in code; rows 4–6 Poly Haven's Island Tree 01, Island Tree 02 and Tree Small 02 (all CC0). Rows 4–6 had their leaves shifted from Poly Haven's olive towards the scene's greens after baking (bark untouched). Per-row size and base are the `KW`/`KB`/`SCALE` values in the tree shader.
- Bank stones are real 3D meshes: Poly Haven's Rock Moss Set 01 and 02 (CC0), shrunk with `tools/shrink_rocks.mjs` (about 130 KB each) and embedded in the module as GLB. They're lit with the land's own lighting and show in the water's reflection.
- The water renders a real reflection pass every frame.
- Hard-won lessons: keep the camera completely still (any bob makes the grass shimmer); multisampled render targets made the screen black on the owner's machine, so don't use them; quality adjusts once at load, never repeatedly (that caused flashing); only golden hour is used for now (the day and night palettes are in the code but switched off).
- New models: Poly Haven is free (CC0). Download glTF at 1k, then shrink and bake to cut-outs, or load as GLB if it's light enough.

### The river camp (2D)

- `src/scene2d.js` is the canvas engine: time of day, water, fire, birds, fish, stars, the squirrel (`drawSquirrel`), ferns (`drawFerns`), and the `Van` module (paint ramps and upgrade layers).
- Writing in the van and the van's looks only apply to the camp; they're hidden while the stream shows.
- `tools/asset-scripts/` holds the one-off scripts that made the van, fern and squirrel assets. Reference only; they need original images that aren't in the repo.

## Test

- `python3 tools/test.py desk|phone '<steps json>' tag` opens index.html headless and saves screenshots to `build/shots/` (needs `pip install playwright` and `python3 -m playwright install chromium`). The 3D scene needs network access for three.js from jsDelivr.
- Dev hooks: `__talio.dev({time, sim, ai})`, `__talio.nudge('birds'|'fish'|'star'|'sq')`, `__talio.patterns()`, `__talio.state()`, `__talio.startJournal('write'|'talk')`, `__talio.openPage('settings'|'memories'|'tasks')`, `__scene3d.setTime('golden')`.
- Look at screenshots of anything visual before calling it done. Check desktop and phone widths.
- `build/` is git-ignored.

## Decisions already made (don't undo without asking)

- The stream is the default scene, framed as a postcard on white, golden hour only for now.
- Header: the logo top left; one menu in the middle (Journal, Tasks, Settings); the volume icon (on/off) far right. Logo colours: both words red, trees green, river blue.
- Writing happens in place: the bottom field expands into the journal card.
- Writing card: one question at a time. It opens on "How are you feeling?"; picking a mood swaps in a question for that mood (low/frustrated → "What would make today feel good?"). A small round-arrow icon shuffles questions. The question is saved with the entry (`prompt`). No placeholder text, just the cursor.
- Finish row: mic, then a split button `Save ▾` whose menu has "Reflect on it" and "Burn it". Tapping outside the card folds it back into the field (the draft is kept).
- Save catches tasks on the device (a regex in tasks.py, written for unpunctuated speech) and lists them under "Added to Tasks", each with ✕ to undo.
- Live voice uses the browser's SpeechRecognition (Chrome, Edge, Safari; not Firefox). Sessions auto-restart with a watchdog; if the browser won't restart, it says "Paused. Tap to keep listening".
- Van (camp scene): two-tone paint, canoe, roof box, ladder and spare tire, unlocked by days journaled. Demo entries never count.
- Data safety: "Erase all journal data" takes two taps and keeps a rescue copy. Never add a destructive action without a confirm.

## Before other people use it

- `src/van.py` has `const VAN_TEST_ALL=true;`, which unlocks every van upgrade for testing. **Set it to false** before sharing the app.
- The logo is upscaled from a tiny image and looks soft; replace `assets/logo/hideout_logo.png` with a 1024px+ transparent version when there is one.

## Backlog (rough priority)

1. Stream: more places on the island (dunes, shore, woods), puffier clouds, a hero tree, turning Day/Night back on once they look right, the scene reacting to mood, maybe an in-scene editor to place trees and a pond.
2. Camp: foliage sway redo (hero ferns as sprite frames; the current row-band sway reads as "scanning").
3. Cloud transcription and real Claude reflections via a Supabase backend.
4. Letters to your future self.
5. A "let it go" paper-boat alternative to burning.
6. Export/download a backup, or email it.
