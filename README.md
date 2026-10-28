# Hideout Journal

A calm journal by a stream.

- `index.html` is the whole app, built and ready to serve (Vercel deploys it on every push to `main`).
- `src/` is the source: the scenes (3D stream, 2D river camp) and the build passes.
- `assets/` holds the art, sound and scene data that the build inlines.
- `prototypes/stream.html` is the standalone 3D scene it was designed in.

Build: `pip install pillow`, then `python3 build.py`. See `CLAUDE.md` for how everything fits together.
