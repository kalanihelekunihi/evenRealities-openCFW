# G2 GX8002 codec-DFU recovery

## Result

The retained first-party translation unit `platform\audio\service_codec_dfu.c` is closed as a linked binary object in the official G2 2.2.6.10 OTA image. Its physical interval is `[0x00577D7C,0x0057A46C)`: 9,968 bytes with SHA-256 `7586756c943d9c607ac92eab4e075d8d0fed0cea38fcf2bb7664122d1f216a35`.

The object contains 16 linked functions. Nine are retained-path anchors and seven adjacent pathless bodies were restored from source order, exact calls, literal ownership, and the enclosing IAR object boundary. Their 9,052 concatenated body bytes hash to `e0487b9129f918d6e4a0caf95fcc1e75f8ebac23db36fce2aa3f2dfe22ded98b`. Nine owned alignment and literal-pool gaps total 916 bytes and hash to `42cffa793dfdb3987491c96e1809a1d69723d6235df129643c157fc37e4a1ffc`.

This remains clean-room behavior recovery rather than historical source recovery. Sixteen independently authored MIT C leaves now replace all 9,052 authenticated stock function bytes. They compile to 3,390 Thumb text bytes plus 24 bytes of generated alignment with 71 strict relocations. The 916 authenticated literal-pool and alignment bytes remain official data.

## Function inventory

The exact ledger is pinned in `tools/manifests/g2-service-codec-dfu-function-map.tsv`. Two public names survive as exact strings: `SVC_CodecDfu` and `SVC_CodecCheckAndUpgrade`. The fourteen internal names are conservative `semantic_*` descriptions rather than unsupported historical symbols. They cover:

- package loading, buffer release, package-version access, and firmware-header validation;
- version formatting/parsing and host-to-big-endian conversion;
- timed UART-token matching and boot-header parsing;
- two bootloader download stages and the final firmware flash; and
- the public DFU and conditional-upgrade orchestration paths.

## Package and memory contract

The package path is `/firmware/codec.bin`. Its 16-byte header begins with little-endian word `0x4B505746`, whose bytes spell `FWPK`, and carries the package version and firmware-record count. Each firmware record is 16 bytes. Type 1 selects the boot image and type 2 the main firmware image. The loader allocates and copies both images, validates their CRC-32 values, and fails closed if either required image is absent.

The recovered persistent state is:

| Address | Meaning |
| --- | --- |
| `0x20074930` | boot-image buffer pointer |
| `0x20074934` | boot-image size |
| `0x20074938` | firmware-image buffer pointer |
| `0x2007493C` | firmware-image size |
| `0x2007395C` | 32-byte boot-header scratch |
| `0x2035EE18` | 8-KiB flash-transfer scratch |
| `0x20074940` | package-version result/cache |

The boot header must be at least 32 bytes. Four 32-bit fields at offsets 8, 12, 16, and 20 are converted from host to big endian before use.

## Download and upgrade state machine

`SVC_CodecDfu` brings up the codec UART at 230,400 baud, loads the package, sends the initial `0xEF` synchronization byte, and waits for the codec's `M` handshake. It then executes the boot-header reader, first boot stage, second boot stage, and firmware flasher in order. Cleanup always tears down UART state and releases both allocated firmware buffers.

The first boot stage begins with `0x59` plus the little-endian configuration word count, transfers the configuration following the 32-byte boot header in at most 256-byte chunks, waits for `wfb` and `OK`, negotiates `GET` at 1,000,000 baud, and acknowledges with `OK`. The second stage begins with `0x53`, sends the raw little-endian checksum and image size, waits for `ready`, transfers the embedded boot image in 256-byte chunks, and accepts `O` plus `boot>`. The flash stage sends `serialdown 0 <size> 8192` and the seeded CRC-32, waits for `~sta~`, sends at most 8-KiB firmware chunks with `~fin~`/`~sta~` flow control, and finally accepts `[Result]:` / `SUCC`. Most protocol waits use 10-second timeouts; the initial flash-ready timeout is 9,000,000 ms and final-result waits are two seconds.

`SVC_CodecCheckAndUpgrade(force)` reads and logs the package version. Unless forced, it asks the adjacent codec-host object for the running version with a 200-ms timeout and returns 1 without flashing when both versions match. Otherwise it performs DFU, queries and logs the resulting version on success, and stores the package version in big-endian form at `0x20074940`. Errors remain negative and the DFU result is propagated.

## Production integration

`components/apollo_main/core_overlay/service_codec_dfu.c` implements strict FWPK loading, bounds and CRC validation, failure cleanup, both boot stages, flash flow control, unconditional DFU, and conditional version-gated upgrade. Sixteen guarded `B.W` redirects cover the exact stock entries. The reviewed Apple-clang aggregate now emits a 255,686-byte overlay and 3,779,082-byte Apollo component. The complete source package is 4,557,576 bytes with SHA-256 `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`; its flash plan contains 4,057 placed and two unresolved evidence-only regions.

The host oracle covers all sixteen selectors, valid and invalid package loading, CRC and release behavior, exact stage-1 and stage-2 wire bytes, flash commands and acknowledgements, complete orchestration and cleanup, and the same-version skip path. No image was signed or flashed.

## Ingress and false-pointer closure

An exhaustive Thumb scan finds 34 calls to exact entries: 30 intra-object and four exterior calls, all four targeting `SVC_CodecCheckAndUpgrade`. Their ordered little-endian pair digest is `e8afc1fbe6e1a10909f767cdb7768ccc2409d921faf1f162b1f587a315b741f3`. The 16 bodies contain 584 direct calls with digest `e0a20198e4441f9c07837432666ca3cdb7812c8c1a151cd360d712d4ca80272d`. No direct call or `B.W` targets a strict interior.

The all-byte four-byte-window scan finds one unaligned numeric collision at `0x00644AB7`: value `0x005797FF` normalizes into the flasher's interior. It is data, not an exact entry, aligned stored pointer, or branch target. There are no aligned stored exact-entry pointers. Treating this collision explicitly prevents unrelated bytes from becoming false ingress.

## Reproduction

Run:

```sh
make service-codec-dfu-closure
```

The analyzer authenticates the official image, all three evidence manifests, every body and owned gap, both object boundaries, the retained path and four pointer cells, two exact symbols, complete call topology, pointer-like windows, package/state literals, source and object pins, strict relocations, guarded redirects, manifest ownership, and component/package/flash-plan artifacts.

## Limitations

- The historical source-only function count is unknown because the vendor source file is unavailable; the linked 16-function callable inventory is complete.
- `semantic_*` labels are clean-room descriptions, not recovered symbols.
- Binary closure does not grant a license or justify copying vendor implementation text; the production implementation is independently authored MIT code.
- Destructive live upgrade, UART timing, codec reboot, and post-flash boot behavior are explicitly blocked: the authorized right temple is nonresponsive, the authorized left temple must remain stock, and no responsive authorized pair or golden codec/UART capture is available.
