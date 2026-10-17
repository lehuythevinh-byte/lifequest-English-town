# LIFEQUEST AI V11.6 — English Town

**Full source package** prepared from the supplied file `LIFEQUEST_AI_V11_6_CLEAN_UI_BEAUTIFUL_MINIMAP(1).html`.
Play a 2D English-learning town with Phaser, NPC conversations, RPG missions, learning tools, economy and an updated minimap.

## Source structure

```text
LIFEQUEST_AI_V11_6_FULL_SOURCE/
├── index.html                 # Web entry point
├── src/
│   ├── css/styles.css        # Complete extracted CSS
│   └── js/
│       ├── config.js         # Public browser config — NO private API keys
│       └── app.js            # Complete extracted JavaScript from V11.6
├── backend/server.py         # NEW optional Python local server / Gemini proxy
├── original/
│   └── LIFEQUEST_AI_V11_6_original.html  # Exact supplied original backup
├── .env.example              # Sample local server variables, NO key
├── .gitignore
├── .nojekyll                 # GitHub Pages support
├── requirements.txt         # No 3rd-party Python packages required
└── README.md
```

**Note about provenance:** The user's supplied V11.6 was a *single-file HTML project*: it did not include a separate Python application, downloaded sprites, or a React/Vite project. The HTML, CSS and JS in `index.html` and `src/` are extracted from that file **without modifying their logic**. `backend/server.py` is an **optional new helper**, not part of the original game source. `original/` contains the unmodified source for comparison.

## Quick start — for other people cloning

```bash
git clone https://github.com/lehuythevinh-byte/lifequest-English-town.git
cd lifequest-English-town
python backend/server.py
```

Open **http://127.0.0.1:8000** in your browser. Python 3.10 or newer is recommended. Alternatively, for non-AI features, you can serve the files using `python -m http.server 8000` in the project root. Opening `index.html` directly may also work, but using the local server is more reliable.

**Internet connection required:** the game currently loads **Phaser 4.2.1 via CDN**; the package contains all author-written HTML/CSS/JS, but not a vendored Phaser library. The game generates its world art in code (there were no separately provided image/sound assets to bundle).

## Optional: Gemini AI through the local Python proxy

1. Copy `.env.example` to `.env`.
2. Set `GEMINI_API_KEY=YOUR_OWN_KEY` in `.env` (local file only).
3. Run `python backend/server.py` and open http://127.0.0.1:8000.
4. The browser sends Gemini requests to `POST /api/gemini`; the local server forwards them with the API key, without publishing it in your HTML/JS.

`.env` is ignored by Git. Do **not** put real Gemini keys in `src/js/config.js`, local browser storage when using a public computer, or Git commits. If a key was previously published, revoke/rotate it.

## Deploy to GitHub Pages (static game)

Push all extracted project files, with **`index.html` at the root**. In **Settings → Pages**, select **Deploy from a branch → main → / (root)**. Example URL: https://lehuythevinh-byte.github.io/lifequest-English-town/ .

GitHub Pages **cannot execute Python** and **does not provide `/api/gemini`**. The game and local non-AI learning features are static; AI requests require a separately hosted server or provider. For public deployment, use a production backend with user auth/rate limits. The supplied Python helper is bound to localhost intentionally and must not be publicly exposed as-is.

## How to update an existing repository safely

Clone the repository first; **do not run `git init` inside your Windows home folder**. Copy **the contents** of this package into the cloned repository, then:

```bash
git status
git add index.html src backend original README.md requirements.txt .env.example .gitignore .nojekyll
git commit -m "Publish LIFEQUEST AI V11.6 full source"
git push origin main
```

## Security / attribution

The distributed JavaScript contains no embedded personal Gemini key. All game logic and graphics remain in `src/js/app.js`. This package does not assign a new redistribution license; if you want others to reuse/modify the code beyond cloning for personal use, choose a LICENSE (for example MIT) for your GitHub repository.
