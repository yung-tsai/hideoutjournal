# Hideout Journal

A calm journaling web app. The default backdrop is **the meadow**: a pixel-art golden-hour meadow with snowy peaks, gently animated, shown as a postcard on a white page. The early-90s Amiga-style pixel-art river camp with a retro van and **the waterfall** are the other choices in Settings > Scene. (**The stream**, a 3D three.js valley, was taken out of the list; its code is kept, switched off by `STREAM = False` in `src/stream3d.py`, so three.js isn't downloaded.) You write (or talk), save the entry, and it shows up in Journal (formerly Memories), Patterns (mood over time) and Tasks. Everything runs in the browser; entries live in localStorage under `talio-home-v1` (the old working name was Talio). There is no backend yet.

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

theme → journal → burn → bundle → sound → safety → patterns → field → write → card → voice → tasks → stream3d → postcard → meadow → waterfall → desert → refresh → nav → frames

- `refresh.py`: the light UI refresh (green tokens, red only in the logo; menu icon / wordmark from `assets/logo/hideout_wordmark_clean.svg` / volume; Journal cards with scene thumbnails; Settings Scene picker with thumbnails).
- `nav.py`: a Claude-style left sidebar (`#sb`: Home, Journal, Patterns, Tasks, the recent entries grouped This week / Last week / by month with folds in `state.meta.sbFold`, Settings at the bottom; the menu icon collapses it, `state.meta.sbOpen`). The others are full pages over the main area, with hash routes (`#/journal`, `#/patterns`, `#/tasks`, `#/settings`, `#/entry/<id>`; `route()`, `go()`): the old `#sheet` panel, re-placed, its pages reused (`sheet.dataset.card`). The scene shows only on Home (the 2D scenes pause behind a page; the sound carries on). On desktop the postcard, field and logo slide right and re-centre via `pcShift()`; on phones the sidebar fills the screen. The scene caption is hidden; the scene switcher (chevrons on hover, dots, arrow keys, swipes).
- `frames.py` (last): Settings > Frame. Rounded (default) and Postcard always; Stamp at 5 entries, Sketch line and Rubber window at 10, Riveted window at 20, Wood window and Dreamy at 50 (total entries, kept once earned: `state.meta.framesUnlocked`; a one-time note in Settings via `framesSeen`). Drawn in code: `#pcBack` (under the scene: shadows, stamp paper) and `#pcFront` (over it: bezels, rivets, sketch lines, Dreamy's dither); `pcLayout` leaves room outside the picture (`FR_T`). `FRAMES_TEST_ALL` unlocks all (off); dev hook `__frames.set(k)`, `__frames.testAll()`.

- `assemble.py` combines the base app (`assets/talio-home-v6-3d.html`, the older UI) with the 2D scene engine (`src/scene2d.js`) and inlines the art.
- Each pass is a Python script `python3 src/<pass>.py in out` that patches the HTML with `rep(a, b, n=1)`. `rep` **asserts the exact number of matches** and exits on a mismatch, so an earlier pass changing a string breaks a later pass loudly. That's on purpose. When you change a pass, keep later passes' anchors intact, or update them.
- Later passes patch the output of earlier ones, so the newest behaviour of a feature is often in a later file (the writing card: write.py then card.py; voice: voice.py replaces LiveTranscriber; the stream: stream3d.py; the camp's postcard layout: postcard.py; the meadow: meadow.py; the waterfall: waterfall.py; the desert: desert.py, which is last).
- New work: edit the pass that owns the feature, or add a new pass at the end of the list in `assemble.py`. Keep the docstring at the top of each pass describing what it changes and why.

### The meadow (2D, default)

- `src/meadow.py` (last pass) adds Settings > Scene's three choices (The meadow / River camp / The stream; `body[data-scene]` meadow|camp|stream, default meadow) and injects `src/meadow.js`. The meadow uses the camp's postcard layout from `postcard.py` (`pcOn()` covers both 2D scenes), its own caption (`MEADOW_CAP`), and the burn opens in its card on wider screens. It starts the first time it shows (`startMeadow()`) and only draws while it's showing; the camp sleeps while it shows. Dev hook: `__meadow.t(seconds)` jumps the scene's clock.
- `src/meadow.js` is generated: `tools/meadow/prep.py` + `build_page.py` from `assets/meadow/master.png` (the picture) and `clean.png` (the same scene without the foreground grass and clouds; slightly redrawn, so it's aligned tile by tile and colour-matched). Run them in a working folder outside the repo (see the docstring), then copy `meadow.js` to `src/` and build.
- What moves: the foreground grass and ferns (cut pixel-exact from the master; each column bends from its roots, tips most, snapped to 2 px, 7 fps; never whole rows shifting, which read as "scanning"); 4 clouds drifting right over the clean sky, coming back from behind the pine (the pine is its own top layer), 2–3 up at a time; colour cycling (no moving pixels) for soft bands on the meadow, the stream's glints and the waterfall; a gust every 8–15 s (the grass leans, a bright sunray band sweeps the meadow, a few golden seed specks drift); now and then a small flock (behind the pine) or a butterfly or two by the grass, one at a time. A hawk was tried and removed (it read as a drone).
- The camp's Pixel Tuner look is applied to every frame: the tune settings, 80 fixed colours, a Bayer 4×4 dither locked to the screen (so it never crawls), the camp's glow (.4) and vignette (.8). It draws a 952×536 canvas, shown nearest-neighbour.
- It adds about 6 MB to `index.html` (the page is ~20 MB).

### The waterfall (2D)

- The third choice in Settings > Scene (`body[data-scene]="waterfall"`), morning only. `src/waterfall.py` adds it the same way as the meadow (postcard layout, caption `WATERFALL_CAP`, burn in the card on wider screens, starts on first show via `startWaterfall()`). Dev hook: `__waterfall.t(seconds)`.
- `src/waterfall.js` is generated from `prototypes/waterfall/` (master.png, clean.png, `prep.py` then `build.py 6`, which writes `waterfall.js`; copy it to `src/` and build). Each step of the test page is kept there as step1–6.html.
- What moves: the ferns sway (the five rocks are a separate still layer, outlined by hand in `prep.py`'s `ROCKS`, their hidden parts filled with matching rock); both falls flow by colour cycling, only on water pixels, held steady at the lip; hard foam churns at the base with patches drifting outward; mist rises against the cliff; rings spread from the base; reflections wobble side to side (each row only borrows water from itself), strong near the fall and calm in front; the streak shimmers; a few glints; a fish jumps about once a minute or two.
- It adds about 4.8 MB (the page is ~22 MB without the stream).

### The desert (2D)

- The fourth choice in Settings > Scene (`body[data-scene]="desert"`), sunset only. `src/desert.py` adds it like the waterfall (postcard layout, caption `DESERT_CAP`, burn in the card on wider screens, `startDesert()`). Dev hook: `__desert.t(seconds)`, `__desert.tumbleweed()`.
- `src/desert.js` is generated from `prototypes/desert/` (master.png, clean.png, `prep.py` then `build.py`; copy `desert.js` to `src/` and build). The test page there has the sky saturation sliders and a TEST tumbleweed button; the app uses the sliders' starting values (blue 30%, orange 25%, clouds 25% less saturated) via `API.sky()`.
- What moves: anchored sway (the ocotillo, the hero; foreground tufts; agaves barely; flowers and midground clumps a little; low tufts in the open patch); clouds drifting behind the saguaro, windmill and peaks; a drawn 14-blade windmill fan turning slowly; the alpenglow fading toward shadow over about 3 minutes, then back; an occasional bird; a tumbleweed every 3–5 minutes. Gusts were tried and removed (they read as paper rolling).
- It adds about 10 MB (the page is ~32 MB): its sway layers carry their own weight maps. Worth slimming before more scenes go in.

### The stream (3D, switched off)

- Not offered any more (Kyoto88's call). `STREAM = False` in `src/stream3d.py` leaves its module and three.js off the page; the rest of that pass (header, logo, light postcard UI, Settings) is still in use by every scene. To bring it back: set `STREAM = True` and add its button back in `src/waterfall.py`.


- `src/stream3d.js` is the three.js scene module. `src/stream3d.py` (the last pass) injects it with an import map (three@0.160.0 from jsDelivr) and adds: Settings > Scene (The stream / River camp), the Postcard frame switch, the light UI over the postcard, the logo (`assets/logo/hideout_logo.png`), the plain on/off volume icon, the header layout, and the Memories → Journal rename. `body[data-scene]` (stream|camp) and `body[data-frame]` (postcard|full) drive it. The 2D camp stops drawing while the stream shows.
- The scene was designed in the standalone page `prototypes/stream.html` (it has its own simple UI and runs on its own). To change the scene, edit that page, check it, then regenerate the module with `tools/make_stream_module.py` (fix its paths first; it was written for the original workspace). Or edit `src/stream3d.js` directly.
- Trees are cut-outs: 8 photos each of 7 trees (8 rows; row 7 is free) packed into one image inside the module, all baked by `tools/bake_trees.html` (`?from=4` bakes only the Poly Haven rows). Row 0 Poly Haven's Jacaranda; rows 1–3 oak, poplar, willow grown in code; rows 4–6 Poly Haven's Island Tree 01, Island Tree 02 and Tree Small 02 (all CC0). Rows 4–6 had their leaves shifted from Poly Haven's olive towards the scene's greens after baking (bark untouched). Per-row size and base are the `KW`/`KB`/`SCALE` values in the tree shader.
- Bank stones are real 3D meshes: Poly Haven's Rock Moss Set 01 and 02 (CC0), shrunk with `tools/shrink_rocks.mjs` (about 130 KB each) and embedded in the module as GLB. They're lit with the land's own lighting and show in the water's reflection.
- Composition (matched to Kyoto88's reference): the sun is centred, low, just above the mountains (`el:4.5, az:0`). The river is one S-curve close to you (`SCP`, `SLN` = log(250/8)), then runs straight to the horizon right under the sun. It has to be centred from about 50 m out, because that's where the sun's mirror image lands on the water from this eye height (`EYE` = water + 3.8 m). The trees are one band across the middle distance in clumps, kept open under the sun, plus hand-placed framing groups (a larger tree on the left third, a fuller group on the right; placed by screen position `sx*.566*d`). They're backlit: deep green, no rim. Tall golden grass fills the bottom corners. Bloom only catches the sun itself (threshold .9), so the sky doesn't glow over the tree edges.
- The water renders a real reflection pass every frame. The water strip is a grid that knows its depth (`aD`) and runs in under the banks, so the real, wandering bank edge is the waterline. It's darker along the banks, where it mirrors them; the reeds and bank grass (`bankIm`) are drawn in the reflection, while the main grass isn't. The sun's glitter is a soft-edged column below the sun (widening toward you) of irregular flecks laid out by viewing angle, plus a faint, sparse shimmer elsewhere.
- Banks: within about 150 m, a fine, bumpy strip of ground (`Hb`) runs along both sides, and the coarse ground sinks under it (`bankZone`). The ground under the grass takes the grass's colours (`uGB`/`uGM`), with dark wet mud right at the waterline. `edgeX(d,side)` gives where the water actually meets the bank; reeds, edge grass, roots and stones are placed along it.
- Grass: near blades take the meadow's colours (lush by the water via `aLush`, in clumps), and the middle-distance tufts soften with distance (no yellow speckle). `gustF()` (in `GL`) rolls slow wind gusts across the grass, tufts and ground. Meadow blades are never planted in the water; seen edge-on, they read as pale streaks.
- Hard-won lessons: keep the camera completely still (any bob makes the grass shimmer); multisampled render targets made the screen black on the owner's machine, so don't use them; quality adjusts once at load, never repeatedly (that caused flashing); only golden hour is used for now (the day and night palettes are in the code but switched off).
- New models: Poly Haven is free (CC0). Download glTF at 1k, then shrink and bake to cut-outs, or load as GLB if it's light enough.

### The river camp (2D)

- As a postcard (`src/postcard.py`): the card keeps the art's 16:9 (952×536), centred between header and field; whole device pixels per art pixel when that costs ≤20% of the room, else the exact fit, always nearest-neighbour. `place()`/`extRest()`/`inRest()` fit the camp to `#stage` (the card) instead of the window, so the van pan/zoom and the van's inside stay in the card. The deckled edge is a `.pcEdge` canvas over the card (same recipe as the stream's). The burn scene uses the card on wider screens and stays full screen on phones (too small there). The caption comes from `PC_CAP` by `ST.time`.

- `src/scene2d.js` is the canvas engine: time of day, water, fire, birds, fish, stars, the squirrel (`drawSquirrel`), ferns (`drawFerns`). `Van` is now a no-op stub (the van is part of the painting).
- Writing in the van and the van's looks only apply to the camp; they're hidden while the stream shows.
- `tools/asset-scripts/` holds the one-off scripts that made the van, fern and squirrel assets. Reference only; they need original images that aren't in the repo.

## Test

- `python3 tools/test.py desk|phone '<steps json>' tag` opens index.html headless and saves screenshots to `build/shots/` (needs `pip install playwright` and `python3 -m playwright install chromium`). The 3D scene needs network access for three.js from jsDelivr.
- Dev hooks: `__talio.dev({time, sim, ai})`, `__talio.nudge('birds'|'fish'|'star'|'sq')`, `__talio.patterns()`, `__talio.state()`, `__talio.startJournal('write'|'talk')`, `__talio.openPage('settings'|'memories'|'tasks')`, `__scene3d.setTime('golden')`.
- Look at screenshots of anything visual before calling it done. Check desktop and phone widths.
- `build/` is git-ignored.

## Decisions already made (don't undo without asking)

- The meadow is the default scene (Settings > Scene: The meadow, River camp, The waterfall, The desert). The stream was removed from the list; anyone who had it saved gets the meadow. The stream is golden hour only for now, its composition following Kyoto88's reference (see the Composition note above).
- Both scenes show as a postcard on the light page by default: deckled edge, caption under it, header above, journal field below; on that page the header and field never rest away when idle. The Postcard switch off gives the old full-screen look (the camp's dark glass UI that rests when idle).
- Header: the menu icon top left (opens the sidebar), the red Hideout wordmark centred, the volume icon (on/off) far right.
- Writing happens in place: the bottom field expands into the journal card.
- Writing card: one question at a time. It opens on "How are you feeling?"; picking a mood swaps in a question for that mood (low/frustrated → "What would make today feel good?"). A small round-arrow icon shuffles questions. The question is saved with the entry (`prompt`). No placeholder text, just the cursor.
- Finish row: mic, then a split button `Save ▾` whose menu has "Reflect on it" and "Burn it". Tapping outside the card folds it back into the field (the draft is kept).
- Save catches tasks on the device (a regex in tasks.py, written for unpunctuated speech) and lists them under "Added to Tasks", each with ✕ to undo.
- Live voice uses the browser's SpeechRecognition (Chrome, Edge, Safari; not Firefox). Sessions auto-restart with a watchdog; if the browser won't restart, it says "Paused. Tap to keep listening".
- Van upgrades (paint, canoe, roof box, ladder, spare tire) were removed; the camp keeps the basic van from the painting. See IDEAS.md; restore from tag `van-upgrades-v1`.
- Data safety: "Erase all journal data" takes two taps and keeps a rescue copy. Never add a destructive action without a confirm.

## Before other people use it

- (`VAN_TEST_ALL` is gone with the van upgrades.)
- The logo is upscaled from a tiny image and looks soft; replace `assets/logo/hideout_logo.png` with a 1024px+ transparent version when there is one.

## Backlog (rough priority)

1. Stream: more places on the island (dunes, shore, woods), puffier clouds, a hero tree, turning Day/Night back on once they look right, the scene reacting to mood, maybe an in-scene editor to place trees and a pond.
2. Camp: foliage sway redo (hero ferns as sprite frames; the current row-band sway reads as "scanning").
3. Cloud transcription and real Claude reflections via a Supabase backend.
4. Letters to your future self.
5. A "let it go" paper-boat alternative to burning.
6. Export/download a backup, or email it.
