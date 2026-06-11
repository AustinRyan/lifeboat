---
product: "Garnix"
tagline: "Hosted CI and caching for Nix projects — flake checks, multi-arch builds, deploy previews"
status: sinking
announced: "2026-05-28"
deadline: "2026-07-15"
sourceUrl: "https://discourse.nixos.org/t/garnix-is-shutting-down-not-oc/77895"
alternatives:
  - name: "nixbuild.net"
    url: "https://nixbuild.net"
    pitch: "Pay-per-use remote Nix builders that plug into your existing workflow — least migration effort if you mainly need build horsepower and a cache."
  - name: "Hercules CI"
    url: "https://hercules-ci.com"
    pitch: "Purpose-built Nix CI: an agent runs in your own infrastructure, understands flakes natively, and gives per-attribute build status like Garnix did."
  - name: "Buildbot-nix"
    url: "https://github.com/nix-community/buildbot-nix"
    pitch: "Free, community-maintained, self-hosted. The most popular DIY route in the Nix community — more ops work, zero vendor risk."
  - name: "Self-hosted Garnix"
    url: "https://github.com/garnix-io"
    pitch: "The Garnix codebase is being open-sourced as part of the wind-down. Keeps your exact setup, but you become the operator."
---

## What happened

The Garnix team [announced on May 28, 2026](https://discourse.nixos.org/t/garnix-is-shutting-down-not-oc/77895)
that they are joining Shopify and the hosted garnix.io service will shut down on
**July 15, 2026**. On that date, user data and build artifacts are deleted. The
announcement was discussed on
[Hacker News](https://news.ycombinator.com/item?id=48309371). As a parting
gift, the team is open-sourcing the Garnix codebase under the
[garnix-io GitHub organization](https://github.com/garnix-io), and community
members (including Numtide) have discussed maintaining it for self-hosting.

## Do this before July 15, 2026

1. **Download any build artifacts you still need.** Artifacts and user data are
   deleted on shutdown day; there is no grace period after July 15.
2. **Inventory which repos use Garnix** — search your GitHub org for
   `garnix.yaml` and check repository webhooks/checks for the Garnix app.
3. **Stand up replacement CI before removing Garnix**, so default-branch
   protection rules that require its checks don't lock your merges.
4. **Remove the Garnix GitHub App** from your org once the replacement is green,
   and update any README badges.

## Migrating your CI

If you just want hosted CI with a Nix-aware cache, GitHub Actions plus Cachix
covers most Garnix setups. A minimal replacement for `garnix.yaml`'s default
flake checks:

```yaml
name: nix-ci
on: [push, pull_request]
jobs:
  flake-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cachix/install-nix-action@v31
      - uses: cachix/cachix-action@v15
        with:
          name: your-cache        # create at cachix.org
          authToken: ${{ secrets.CACHIX_AUTH_TOKEN }}
      - run: nix flake check -L
      - run: nix build -L
```

For multi-arch (aarch64) builds — one of Garnix's best features — add a matrix
with `runs-on: ubuntu-24.04-arm`, or point your builds at
[nixbuild.net](https://nixbuild.net)'s remote builders, which handle
architecture targeting without self-managed runners. If you relied on Garnix's
per-attribute status checks, [Hercules CI](https://hercules-ci.com) is the
closest behavioral match.
