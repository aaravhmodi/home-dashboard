# Home dashboard

One start page for the home server (the MacBook running Ubuntu on Tailscale): every app
with a live up/down dot, server CPU, memory, disk and temperature, and links to the
monitoring tools.

It's [Homepage](https://gethomepage.dev) running in Docker, configured by the YAML files
in `config/`. It is only reachable over Tailscale:

**http://100.76.57.23**
