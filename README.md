[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/homehub?utm_medium=integration&utm_source=button&utm_campaign=homehub)

# HomeHub on Railway

One-click Railway template for [HomeHub](https://github.com/surajverma/homehub) **v0.7.0**, a private family hub: shared notes, shopping list, chores, calendar and reminders, expenses with budgets, recipes, expiry tracker, shared files and more.

- **Image:** `ghcr.io/surajverma/homehub:0.7.0@sha256:c16dc026f72509dfa8ceb7c754c7963dde9cea9ee2c11bc0058ebd9647a3af01` (official, pinned by version and digest), plus a small start wrapper in [`railway/`](railway/).
- **Services:** one (`HomeHub`), built from this repo. Health check `/healthz`.
- **Storage:** one Railway volume at `/data` holding the SQLite database, secret key, uploads, PDFs, downloaded media and `config.yml`.
- **Security:** upstream has no user accounts. The template generates a site password and an admin password on deploy and writes them in before the port opens; the service refuses to start without them. Login attempts are rate-limited per visitor (real client IP behind Railway's proxy), and the session cookie is `Secure`.
- **Size:** fits Railway's Free plan (0.5 GB RAM / 1 vCPU): about 90 MB idle, about 215 MB peak while extracting audio from a download.

## Variables

| Variable | Default | What it does |
|---|---|---|
| `HOMEHUB_SITE_PASSWORD` | `${{secret(24)}}` | Password for the whole site, asked once per browser. |
| `HOMEHUB_ADMIN_PASSWORD` | `${{secret(24)}}` | Unlocks the Administrator user (settings, budgets, backups, API tokens). |
| `HOMEHUB_FAMILY_MEMBERS` | `Mom,Dad` | Comma-separated names for the user switcher. |
| `HOMEHUB_INSTANCE_NAME` | `Our Home Hub` | Name in the sidebar and browser tab. |
| `TZ` | `UTC` | Time zone for "today", due dates and recurring items. |
| `PORT` | `8080` | Port gunicorn listens on. |

These are written into `/data/config.yml` (and the admin password hash into the database) on every start. All other HomeHub settings live in `/data/config.yml`: `railway ssh`, then `vi /data/config.yml`; HomeHub reloads it on the next page load.

## After deploy

1. Copy `HOMEHUB_SITE_PASSWORD` from the service's Variables tab, open the Railway URL and log in.
2. Pick your name in the user switcher. Picking **Administrator** asks for `HOMEHUB_ADMIN_PASSWORD`.
3. Change `HOMEHUB_FAMILY_MEMBERS` to your family's names and redeploy.

## Notes

- The media downloader runs yt-dlp from Railway's servers. YouTube and Vimeo ask datacenter addresses to sign in and refuse; many other sites work.
- Backups (Administrator, then Manage backups, or `flask backup` over `railway ssh`) are written to the volume. Download them for an off-site copy.

## Updates

New HomeHub releases come as a version bump of the `FROM` line in this repo, with an entry in [`CHANGELOG.md`](CHANGELOG.md). Railway then shows "update available" on your service; read the changelog and apply it when you're ready. Your data stays on the volume.

## Overview

The marketplace overview is in [`overview.md`](overview.md).

## Licence

HomeHub is MIT-licensed by its authors. This wrapper is MIT too.
