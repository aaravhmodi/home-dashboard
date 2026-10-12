# Home dashboard

One start page for the home server (the MacBook running Ubuntu on Tailscale): every app
with a live up/down dot, server CPU, memory, disk and temperature, and links to the
monitoring tools.

It's [Homepage](https://gethomepage.dev) running in Docker, configured by the YAML files
in `config/`. It is only reachable over Tailscale:

**http://100.76.57.23**

## What's on it

- **Top:** live CPU, memory, CPU temperature, uptime and storage for the server.
- **Apps:** Internship Tracker, Study Agent (and its browser), Enerzen web and API.
- **Monitoring:** Uptime Kuma and Grafana.
- **Behind the scenes:** PostgreSQL, Redis, the Cloudflare tunnel and Prometheus.
- **Bookmarks:** GitHub repos, Tailscale, Vercel, Cloudflare, and OpenAI/xAI usage.

Each tile has a status dot (green when the app answers, with its response time) and,
underneath, its container's state, CPU and memory. Type anywhere on the page to search.

## Changing it

| To change | Edit |
|---|---|
| Tiles (add an app, rename, change a link) | `config/services.yaml` |
| The stats strip at the top | `config/widgets.yaml` |
| Bookmarks | `config/bookmarks.yaml` |
| Title, theme, columns | `config/settings.yaml` |

Then commit and run `./deploy.sh`. Homepage picks up config changes without a restart.
Icons: `mdi-<name>` from [Material Design Icons](https://pictogrammers.com/library/mdi/),
or `<app>.png` from [Dashboard Icons](https://dashboardicons.com).

## How it runs

- `compose.yaml` runs Homepage, published only on the Tailscale address
  (`100.76.57.23:80`), so nothing outside your tailnet can reach it.
- Homepage reads container status through `docker-proxy`, which allows only read-only
  container queries, so the dashboard can't start, stop or change anything.
- Uptime Kuma checks it like the other apps, and the server alerts know its containers.
