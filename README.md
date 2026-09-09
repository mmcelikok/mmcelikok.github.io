# mustafamertcelikok.github.io

Personal academic website for Mustafa Mert Çelikok, built on [al-folio](https://github.com/alshedivat/al-folio) (a Jekyll starter widely used for academic homepages in the ML/RL community) and hosted on GitHub Pages.

## What's automated

- **CV** (`/cv/` page + downloadable PDF): edit [`_data/cv.yml`](_data/cv.yml). On every push to `main`, [`.github/workflows/render-cv.yml`](.github/workflows/render-cv.yml) regenerates `assets/rendercv/rendercv_output/CV.pdf` with [RenderCV](https://rendercv.com/) and commits it back. The CV page itself is rendered live from the same YAML file, so it's always in sync with the PDF.
- **Citation counts**: [`.github/workflows/update-citations.yml`](.github/workflows/update-citations.yml) runs 3x/week, pulls current citation counts from [Google Scholar](https://scholar.google.com/citations?user=_8yxhlMAAAAJ) via the `scholarly` package, and writes them to `_data/citations.yml`.
- **New publications**: [`.github/workflows/update-publications.yml`](.github/workflows/update-publications.yml) runs weekly, checks Google Scholar for papers not yet in [`_bibliography/papers.bib`](_bibliography/papers.bib), and appends a generated BibTeX entry for each new one (existing entries are never touched, so manual tweaks like `selected: true` or `abbr` are preserved). New entries are appended with a comment flagging them for review — check venue/`abbr`/`selected` fields after they land.

Both Scholar workflows key off `scholar_userid` in [`_data/socials.yml`](_data/socials.yml).

## Publishing this to GitHub Pages

1. Create a new **public** GitHub repository. For a personal user site, name it `<your-github-username>.github.io` (e.g. `mmcelikok.github.io`) — this serves the site at the root of that URL with no extra path config needed. If you use a different repo name, you'll additionally need to set `baseurl: /<repo-name>` in [`_config.yml`](_config.yml).
2. Push this folder to that repo, on the `main` branch.
3. In the repo's **Settings → Actions → General → Workflow permissions**, select **"Read and write permissions"**. This lets the CV/citations/publications workflows commit their updates back to the repo.
4. Wait for the **Deploy site** Action to finish (Settings → Actions tab). It builds the Jekyll site and pushes it to a `gh-pages` branch.
5. In **Settings → Pages**, set **Source** to **"Deploy from a branch"**, branch **`gh-pages`**, folder **`/ (root)`**.
6. Your site will be live at `https://<your-github-username>.github.io` (or `https://<your-github-username>.github.io/<repo-name>` for a project repo) within a few minutes.

## Updating content

| What                  | Where                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| CV                    | [`_data/cv.yml`](_data/cv.yml) — auto-regenerates the PDF and the `/cv/` page                                               |
| Publications          | [`_bibliography/papers.bib`](_bibliography/papers.bib) — auto-updated with new Scholar papers, or add entries by hand       |
| News / announcements  | add a file to [`_news/`](_news/)                                                                                            |
| Teaching              | [`_teachings/`](_teachings/)                                                                                                |
| Bio / contact / photo | [`_pages/about.md`](_pages/about.md) — add a real photo to `assets/img/` and uncomment the `image:` line in the frontmatter |
| Social links          | [`_data/socials.yml`](_data/socials.yml)                                                                                    |

For anything not covered above (design tweaks, dark mode, comments via Giscus, analytics, etc.), see [`docs/CUSTOMIZE.md`](docs/CUSTOMIZE.md) and [`docs/FAQ.md`](docs/FAQ.md).

## Local development

```bash
bundle install
bundle exec jekyll serve   # → http://localhost:4000/
```

To also test the CV/citations/publications scripts locally:

```bash
python3 -m pip install -r requirements.txt
python3 bin/update_scholar_citations.py
python3 bin/update_scholar_publications.py
rendercv render _data/cv.yml --settings assets/rendercv/settings.yaml
```

## Credit

Built on [al-folio](https://github.com/alshedivat/al-folio) (MIT licensed — see [`LICENSE`](LICENSE)).
