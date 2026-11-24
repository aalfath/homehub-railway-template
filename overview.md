# Deploy and Host HomeHub on Railway

HomeHub is a lightweight, open-source family hub (MIT). One web app holds the household's shared notes, shopping list, chores, calendar and reminders, expense tracker with budgets, recipe book, expiry tracker, shared file cloud, "who's home" board, PDF compressor and media downloader. It installs as a PWA on phones and runs on minimal hardware.

## About Hosting HomeHub

HomeHub is a single Python (Flask and gunicorn) service with an SQLite database, so hosting it means one container, one persistent volume and a settings file. Upstream has no user accounts: anyone who can open the URL can use it unless a site password is set. This template builds HomeHub v0.7.0 from the official image (pinned by digest), keeps the database, uploads, PDFs, media and `config.yml` on a Railway volume, and generates the site password and admin password on deploy before the public URL opens. It refuses to start without them. It runs comfortably on Railway's Free plan (about 90 MB idle, under 220 MB while converting media).

## Common Use Cases

* A private shared shopping list, chore tracker and notice board for the whole family, on every phone
* Tracking household spending with monthly budgets, recurring bills and CSV import and export
* Shared reminders that sync into phone calendars, plus recipes, expiry dates and family files in one place

## Dependencies for HomeHub Hosting

* One Railway service built from `aalfath/homehub-railway-template` (the official `ghcr.io/surajverma/homehub` image plus a small start script)
* One Railway volume mounted at `/data` (SQLite database, uploads, PDFs, media and `config.yml`)

### Deployment Dependencies

* HomeHub upstream: https://github.com/surajverma/homehub
* Template repository: https://github.com/aalfath/homehub-railway-template

### Implementation Details

**After deploy:** open the service's **Variables** tab and copy `HOMEHUB_SITE_PASSWORD`. Open your Railway URL and enter it once per browser. Pick who you are from the user switcher. Choosing **Administrator** asks for `HOMEHUB_ADMIN_PASSWORD`, which unlocks settings, budgets, backups and API tokens.

**Variables:**

* `HOMEHUB_SITE_PASSWORD`: generated; the password for the whole site. Change it and redeploy to rotate it.
* `HOMEHUB_ADMIN_PASSWORD`: generated; unlocks the admin user.
* `HOMEHUB_FAMILY_MEMBERS`: comma-separated names in the user switcher (default `Mom,Dad`). Edit it to your family and redeploy.
* `HOMEHUB_INSTANCE_NAME`: the name in the sidebar and browser tab.
* `TZ`: your time zone (for example `Europe/Berlin`), so "today", due dates and recurring items roll over at your midnight.

Everything else in `config.yml` (feature toggles, colours, reminder categories, calendar feed token, weather, upload limit) is yours to edit: `railway ssh`, then `vi /data/config.yml`. HomeHub reloads it on the next page load. The variables above are rewritten into the file on every start.

**Notes:** the media downloader uses yt-dlp from Railway's servers; some sites (YouTube, Vimeo) ask datacenter addresses to sign in and refuse the download, while many others work. Backups (Admin, then Manage backups) are written to the volume; download them to keep an off-site copy. Upstream intends HomeHub for a home network, so keep both passwords private.

**Updates:** new HomeHub releases arrive as a version bump in the template repo, and Railway shows "update available" on your service. Read `CHANGELOG.md` in the repo before applying. Your data stays on the volume.

## Why Deploy HomeHub on Railway?

<!-- Recommended: Keep this section as shown below -->
Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying HomeHub on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.
<!-- End recommended section -->
