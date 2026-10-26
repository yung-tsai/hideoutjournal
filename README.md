# Hideout: test build for Vercel

Two files: `index.html` (the whole app) and `vercel.json` (allows the microphone, and stops browsers caching an old build).

## Deploy (pick one)
- **Drag and drop:** zip this folder's contents, then in Vercel choose Add New → Project and deploy the folder. Or use the Vercel CLI from this folder: `npx vercel` (first time) and `npx vercel --prod` after.
- **GitHub:** put both files at the root of a repo, import the repo in Vercel, no build settings needed (Framework: Other).

## Try the mic
Open the site on your phone over https (Vercel gives you that), tap the field at the bottom, then the mic. Allow microphone access when asked.
- Works in Chrome, Edge and Safari (including iPhone). Not Firefox.
- Words should appear as you speak; tap Done when you finish.

## Notes for this test build
- Entries live in this browser only, separate from the claude.ai preview.
- Reflections use the on-device rules, not Claude (that needs the backend).
- Every van upgrade is unlocked (testing switch); it gets turned off before anyone else uses the app.
