# Community Research

External community protocol research and SDK documentation that informed this project's
reverse-engineering effort. These are snapshots taken on 2026-02-25 from public GitHub
repositories.

> **Note:** Our own protocol documentation in [protocols/](../protocols/) and
> [features/](../features/) now supersedes most of this material with more comprehensive
> and verified findings. These sources are preserved for historical reference and
> attribution.

## Sources

### [i-soxi-protocol/](i-soxi-protocol/) — Even G2 Protocol Documentation

Independent BLE protocol reverse engineering by i-soxi. Original per-topic docs
(ble-uuids, packet-structure, services, teleprompter) have been fully incorporated
into our comprehensive protocol documentation. The [README](i-soxi-protocol/README.md)
is preserved for attribution with pointers to canonical docs.

**Superseded by:** [protocols/packet-structure.md](../protocols/packet-structure.md),
[protocols/ble-uuids.md](../protocols/ble-uuids.md),
[protocols/services.md](../protocols/services.md),
[features/teleprompter.md](../features/teleprompter.md)

### [nickustinov-g2-notes/](nickustinov-g2-notes/) — Even G2 Development Notes

Comprehensive EvenHub SDK documentation by nickustinov. Key files:
- [G2.md](nickustinov-g2-notes/G2.md) — Master reference (1166 lines): SDK init, display
  system, container model, input events, page lifecycle, audio, error codes, UI patterns
- [display.md](nickustinov-g2-notes/display.md) — Display canvas and container details (343 lines)
- [page-lifecycle.md](nickustinov-g2-notes/page-lifecycle.md) — Page create/rebuild/shutdown lifecycle
- [packaging.md](nickustinov-g2-notes/packaging.md) — App packaging and deployment
- [input-events.md](nickustinov-g2-notes/input-events.md) — Touch/gesture event types
- [error-codes.md](nickustinov-g2-notes/error-codes.md) — SDK error code catalog
- [simulator.md](nickustinov-g2-notes/simulator.md) — Browser-based simulator
- [architecture.md](nickustinov-g2-notes/architecture.md) — SDK architecture overview
- [ui-patterns.md](nickustinov-g2-notes/ui-patterns.md) — Common UI patterns
- [browser-ui.md](nickustinov-g2-notes/browser-ui.md) — Browser UI component library
- [device-apis.md](nickustinov-g2-notes/device-apis.md) — Device info and storage APIs

**Superseded by:** [features/eventhub.md](../features/eventhub.md),
[features/display-pipeline.md](../features/display-pipeline.md),
[features/display-viewport.md](../features/display-viewport.md),
[features/gestures.md](../features/gestures.md)

## Third-Party SDKs

These npm packages in `third_party/` provide the JavaScript/TypeScript SDK layer for
EvenHub app development:

| Package | Description |
|---------|-------------|
| `even_hub_sdk-0.0.7/` | Official Even Realities EvenHub SDK (v0.0.7) |
| `even-better-sdk/` | Opinionated wrapper by @jappyjan: page composition, partial text updates, logging |
| `even-realities-ui/` | Foundation UI components by @jappyjan: buttons, icons, tokens, typography |

## Community Apps

See [community-apps.md](../community-apps.md) for the catalog of 24 open-source
EvenHub apps from the community.
