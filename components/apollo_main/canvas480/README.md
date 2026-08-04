# G2 576x480 virtual-canvas patch

This component layers `g2flash-canvas480.patch` over the exact stock G2 `2.2.6.10` Apollo image and the existing `g2flash` CFW patch set at commit `d5eb48dd9dcda4cc630458ec365bc546036678c2`. It does not replace or omit the current `img576`, `imgz`, `rle`, XOR-delta, stereo, gesture, and other upstream changes. The source patch advances the negotiated marker to `EVENCFW/4 img576 imgz rle xordelta stereo canvas480`. It intentionally advertises only extensions actually present in that pinned upstream source.

## Geometry and safety boundary

Recovered stock code configures the LVGL display, flush rectangle, and backing allocation as 576x288. Changing those fixed values to 576x480 would make stock scanout read beyond its proven buffer and is therefore not supported by this patch. Instead, mode 10 allocates a 576x480 packed 4bpp virtual canvas (138,240 bytes), copies one clamped 576x288 viewport into the unchanged stock display buffer, and lets the phone pan that viewport from row 0 through row 192. This exposes every one of the 480 virtual rows through the requested up/down nudge behavior without claiming that the optical scanout itself has become 480 pixels tall.

The keyframe is decoded into a fresh allocation and swapped only after complete zlib/RLE validation. Pan is accepted only by the image container that seeded the canvas, invalid coordinates and geometry are rejected, release frees the allocation, and a malformed frame preserves the previous canvas. SybilSight sends mode 10 only after the authenticated settings response explicitly advertises `canvas480`; stock and older CFW stay on their existing image path. Host encoding also caps the complete private payload below the proven 576x288 reconstruction allocation.

## Private mode-10 wire contract

- Keyframe: `[10][0][viewportY LE16][576 LE16][480 LE16][zlib(rle(packed4bpp))]`
- Pan: `[10][1][viewportY LE16]`
- Release: `[10][2]`

`viewportY` is inclusive in `0...192`. Packed pixels are top-down, high nibble first, with a 288-byte row stride. A pan retransmits no pixels.

## Reproducible local build

The builder verifies the exact stock SHA-256 and pinned `g2flash` commit, clones that local checkout into a temporary directory, applies this reviewed source patch, invokes upstream's compiler-backed patch generator, replays the generated patch list, and writes a hash manifest. It never downloads or flashes firmware and refuses to overwrite artifacts unless `--force` is supplied.

```sh
python3 openCFW/components/apollo_main/canvas480/build_stock_canvas480.py \
  --g2flash /path/to/g2flash \
  --stock firmware/ota/2026-07-22/g2-2.2.6.10-e28738432d7b612d625331b00383149b.bin \
  --output /safe/review/location/g2-2.2.6.10-sybilsight-canvas480.bin
```

Review the generated firmware, replayable patch JSON, and manifest before using the repository's existing recovery-aware flashing workflow. This component does not flash a device.

The versioned SybilSight CFW `2.2.6.12` release is defined separately at `../../../releases/g2-2.2.6.12`. That release uses this component unchanged, then assigns the distinct CFW release identity while retaining `2.2.6.10` as its authenticated vendor base.

## SybilSight host API

`SybilSightBluetoothSDK.virtualCanvas480Available` exposes negotiation. `displayVirtualCanvas480(base64ImageData:viewportY:)` installs the 480-line image, `setVirtualCanvas480Viewport(_:)` pans it, and `releaseVirtualCanvas480()` frees it. These calls deliberately do not reuse the stock 0...12 optical screen-height setting.

## Provenance and license

The patch modifies GPL-3.0-only `jimrandomh/g2flash` sources and is distributed under GPL-3.0-only under the same upstream terms. The complete GPL text is already retained at `../ring_gesture/LICENSE`. No vendor firmware bytes are included in this component.
