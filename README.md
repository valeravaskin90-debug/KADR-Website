# KADR Website

Official bilingual static website for KADR, a proprietary local AI engineering application for KOMPAS-3D.

This public repository contains only website HTML/CSS/JavaScript, reviewed screenshots, public documentation, a website validator and GitHub Pages deployment configuration. The KADR application source, algorithms, AI models and portable bundles are private and are not distributed here.

## Preview

```powershell
python -m http.server 8766 --directory website --bind 127.0.0.1
```

Open http://127.0.0.1:8766/ and http://127.0.0.1:8766/en/.

## Validate and update

```powershell
python tools/validate_website.py
git diff --check
git add website
git diff --cached --stat
git commit -m "Update public website"
git push origin main
```

GitHub Pages publishes only `website/`. In repository Settings → Pages select GitHub Actions. The expected project address is `https://OWNER.github.io/KADR-Website/`.

The download button remains “Coming soon” until an approved distribution channel exists. English examples describe Russian commands; full English CAD command support is not claimed.

## Rights

All rights reserved by the project owner. No MIT/Apache or other open-source license is granted to the KADR core or these website assets. KOMPAS-3D trademarks and interface elements belong to their respective owners. This project is not affiliated with ASCON.

See ASSET_PROVENANCE.md for screenshot sources and review notes.

