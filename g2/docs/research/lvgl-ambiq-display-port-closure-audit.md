# LVGL Ambiq display-port closure audit

## Result

The retained G2 `lv_ambiq_display.c` translation unit is no longer a
third-party functional gap. Its complete linked executable surface is seven
functions / 638 stock bytes, and all seven functions are already compiled from
reviewed OpenCFW source and reached through generated, non-linking `B.W`
redirects.

The retained source path anchors five functions directly. The installed
display-synchronization callback is instead closed by its unique stored Thumb
pointer and registration topology, while the 12-byte port initializer is
closed by adjacency and its two source links. Treating only direct `__FILE__`
anchors as the port would therefore undercount a known closed surface.

| Stock entry | Bytes | Stock SHA-256 | OpenCFW source entry |
|---:|---:|---|---|
| `0x0047366C` | 136 | `ed721fed382d…` | `open_cfw_lv_buffer_sync` |
| `0x004736F4` | 142 | `366105e7228b…` | `open_cfw_lv_display_sync` |
| `0x00473782` | 156 | `d0f3a63dee7b…` | `open_cfw_lv_display_setup` |
| `0x0047381E` | 76 | `364966c0adae…` | `open_cfw_lv_display_lock` |
| `0x0047386A` | 62 | `3855e4bb9e42…` | `open_cfw_lv_display_unlock` |
| `0x004738A8` | 54 | `bba889445f51…` | `open_cfw_lv_display_lock_initialize` |
| `0x00473928` | 12 | `2f750e3edcff…` | `open_cfw_lv_display_port_initialize` |

The four source files and their build-report identities are pinned as part of
the audit. Existing host substitution tests cover null/error and successful
paths, exact call order and arguments, mutex task/IRQ behavior, callback
registration, buffer geometry, diagnostics, and guard bytes. This audit adds
an aggregate ownership invariant rather than duplicating those behavioral
fixtures.

## Input boundary

There is no retained third-party Ambiq input-port translation unit. The only
path under `third_party\lvgl_v9.3\lvgl_ambiq_porting` is
`lv_ambiq_display.c`. The relevant retained input manager is
`platform\input\service_input_manager.c`, which is a first-party platform
boundary. Official LVGL input-device core files remain ordinary upstream core
and must not be confused with a board input port.

Consequently “Ambiq display/input ports remain” was an incorrect aggregate
description:

- the display port's linked functionality is 100% source-owned;
- no separate third-party input-port artifact is linked; and
- input transport/policy and the display manager are first-party recovery
  work, outside third-party utility closure.

## Provenance limit

The original `lv_ambiq_display.c` source, version label, and producing private
commit remain unavailable. The path is not part of official LVGL or the exact
public Ambiq draw-backend subtree, and no occurrence was found in the checked
public Ambiq history used by the repository audits. The correct provenance
record is therefore:

- origin: private Ambiq/Even LVGL integration glue;
- version: unknown / not independently versioned;
- historical generating commit: `null`; and
- functional status: independently source-owned, not opaque.

An exact private commit would improve historical attribution but would not
unlock additional linked display-port behavior. Remaining practical work is
target display/DMA/mutex concurrency validation and first-party input/display-
manager recovery.

## Reproduction

```sh
make lvgl-display-port-closure
```

The analyzer authenticates the official image and 64-shard Ghidra corpus,
fails closed on any path, function, source hash, stock span, or redirect
change, and performs no signing, flashing, erase, or hardware operation.
