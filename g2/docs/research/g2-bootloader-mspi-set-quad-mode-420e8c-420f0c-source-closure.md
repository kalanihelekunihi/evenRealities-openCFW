# G2 bootloader MX25U25643G quad-mode source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Result

The complete authenticated 128-byte entry `[0x00420E8C,0x00420F0C)` is now
replaced by maintained clean-room C in
`components/bootloader/core_overlay/runtime_mspi_set_quad_mode_420e8c.c`.
The stock body SHA-256 is
`d3eeee3b649bcab6d485d604bb94fe739a753064b80b6918a4d5a9db616b86ef`;
the 5,706-byte source SHA-256 is
`9a94b5d2766ecbbfe5b428779dc34c7a0eb19f4b7e6eeb7edb1cededa9228833`.
Its three direct stock callers are `0x00420ACE`, `0x00420C08`, and
`0x00420F9C`. The following `[0x00420F0C,0x00420F10)` word is retained
non-executable data; the next executable entry starts at `0x00420F10`.

## Recovered behavior

The service copies the exact 24-byte initialized-SRAM quad template from
`0x20000224`, whose authenticated bytes are
`080300006b00020010000014000101010000000000000000` and whose SHA-256 is
`bae2c3ff93a23cefbdb43825a67be78b67a6ab47f090616d16a0a694b0b3d598`.
It then sets byte `+0` to turnaround `8`, halfword `+4` to QREAD4B command
`0x006C`, byte `+8` to quad device selector `0x10`, and byte `+15` to one.

A nonzero source-owned device-reconfiguration result logs line `0x5AE` with
format `0x00432E50` and returns immediately. Success calls the source-owned XIP
configuration service with one and submits retained HAL control request
`0x18` against the published handle at `0x200270DC`, passing mode byte `0x10`.
A nonzero control result logs line `0x5B5` with format `0x00433240`. Both logs
use tag `0x00433CD8`, file `0x00431540`, and retained function identity
`mx25u25643g_set_quad_mode` at `0x00433578`. The function returns no value.

## Build and routing evidence

Apple emits 152 bytes at overlay offset 14,164/runtime `0x00437BCC`, with raw
SHA-256
`c9a0245f4090f520644aa4fda29308adf089d78cafa84d959754493926a65bdd`
and relocated SHA-256
`f16e2d6db8f18731b03c5f1a335ebd5f80d9524d8b320749666c05185415eb3c`.
Its strict calls are at offsets 12/48/66 to source-owned memcpy, device
reconfiguration, and XIP configuration. Linux emits 152 bytes at offset
14,140/runtime `0x00437BB4`, with raw/final SHA-256
`9f9c7e7a37e012b4db006e45382f6d8a4a63bd6d6ee950cad2c79918b1ef7d4d` /
`9d86039bf8fe7439460b4cc015d78637343cf8ddf85632775e094cd09a1ef521`;
the strict-call offsets are 12/48/68.

The full-span stock patch is `16f09ebe` followed by 62 Thumb NOPs. Canonical
Apple/Linux overlays are 14,316/14,292 bytes and providers are
162,916/162,892 bytes. Accounting is 14,301 source-owned bytes, 15,592
generated patch bytes, 16 alignment bytes, and 133,007 retained official
bytes across 192 routed functions, 173 relocated leaves, and 190 patch sites.

Unsigned Apple/Linux packages are 4,744,494 / 4,520,480 bytes with SHA-256
`caf999acbe2b7c172da62a3fbec502f4a82b9181c9e470cb07473e4c8639234f` /
`bfde66dc0c3457995eeffe0c11b9a8aecb6b4a325407d9400171d5666ab10af2`.
The Apple flash plan has 6,542 placed regions, two unresolved address regions,
five container-only regions, and six protected regions.

## Physical-evidence boundary

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live template initialization, HAL, pinmux, MSPI, XIP, external-flash, and
cold-boot behavior cannot be validated because no authorized responsive right
G2 temple is available; the left temple must remain stock. Executable service
bodies beginning at `0x00420F10` remain software gaps. Firmware-wide
functional completeness is therefore not claimed.
