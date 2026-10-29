# Ideas

Things set aside or not built yet, with enough detail to pick them back up.

## Van upgrades

The river camp's van could be customised, and things opened up with **days journaled** (not entry count; several entries in one day counted once, and a gap never took anything away):

- 1 day: a fresh coat of paint (Silver, Sage, Sky, Brick)
- 3 days: a spare tire on the back door
- 5 days: three more colours (Mustard, Cream, Charcoal)
- 7 days: a ladder
- 14 days: a canoe or a roof box on the roof
- 21 days: the other roof choice too
- 30 days: any colour you like (a colour picker)

Each unlock showed one quiet note after saving, and a dot on "Your van" in Settings. The paint was two-tone (white top, colour below), turned into a seven-step ramp per colour and re-lit to match each time of day.

Files and assets it used:
- `src/van.py`: the pass that added it (state `state.van`, the "Your van" page `renderCustomize()`, `applyVan()`, the unlock note `announceUnlocks()`, `VAN_TEST_ALL`, the dev "days journaled" control, backup and restore of `van`).
- `src/scene2d.js`: the `Van` module (paint ramps, the dress step that paints the van and adds the canoe, roof box, ladder and tire layers for each time of day).
- `assets/up/vanassets.json`: the van's mask, light maps and add-on layers.
- `tools/asset-scripts/` (`up_cut.py`, `up_relight.py`, `up_tune_edits.py`): the one-off scripts that made those assets.

Restore from tag `van-upgrades-v1`.

## Weather for mood

Replace the Journal's thumbnails with small animated pixel weather icons, one per mood: sun = happy, rain = sad, storm = frustrated, moon = tired, fog = anxious, and so on.
