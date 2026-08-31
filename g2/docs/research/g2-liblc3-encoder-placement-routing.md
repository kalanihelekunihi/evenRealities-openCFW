# G2 Apollo liblc3 encoder placement and routing boundary

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: direct-branch range is sufficient, but production placement and
routing are software-blocked

## Result

The complete admitted encoder does **not** fit in the authenticated Apollo-main
capacity currently available without moving another component. The reviewed
Apple build needs an aligned 128,752-byte load span: 43,248 bytes of text,
85,088 bytes of read-only tables, 404 bytes of `SHF_WRITE` pointer tables, and
12 bytes of leading alignment. The current canonical core ends at
`0x007ECA44`; the protected bootloader update record starts at `0x007FE000`.
That leaves 71,100 bytes and an append-only shortfall of **57,652 bytes**.
Text plus read-only tables alone overflow by 57,248 bytes, so assigning the
404-byte data section to RAM would not make the flash placement fit.

No unclassified NOP, zero, or `0xFF` run is treated as capacity. The only
additional ranges in the current config with explicit capacity contracts are
already owned by PT protocol and the standalone liblc3 LTPF route. Even the
deliberately over-optimistic sum of:

- all 71,100 append bytes;
- all 12,828 bytes of PT reserved padding; and
- all 10,040 bytes of both LTPF caves after removing the existing provider

is only 93,968 bytes. It remains **34,784 bytes short** before accounting for
the fact that PT padding is reserved and LTPF removal is not authorized. This
aggregate necessary-condition failure proves that fragmenting sections across
every known range cannot solve the current placement.

## Authenticated audio-service ingress

The official `platform\audio\service_audio.c` object remains exactly 2,884
bytes at `[0x0057A900,0x0057B444)`, SHA-256
`01864fb4fc778a70c3c50b7999c8a43b86d4f8763479e8cf5e47d7a529207193`.
Its complete LC3 caller set is:

| Call site | Caller | Stock target | Original bytes |
|---:|---|---|---|
| `0x0057A938` | `service_audio_lc3_encoder_setup` | `lc3_setup_encoder` at `0x00591374` | `16f01cfd` |
| `0x0057A9C2` | `SVC_Lc3EncodeMono` | `lc3_frame_samples` at `0x00590E64` | `16f04ffa` |
| `0x0057A9CC` | `SVC_Lc3EncodeMono` | `lc3_frame_bytes` at `0x00590F78` | `16f0d4fa` |
| `0x0057AA9E` | `SVC_Lc3EncodeMono` | `lc3_setup_encoder` at `0x00591374` | `16f069fc` |
| `0x0057AB14` | `SVC_Lc3EncodeMono` | `lc3_encode` at `0x0059138A` | `16f039fc` |

All five are authenticated Thumb-2 `BL` instructions. If text hypothetically
started at aligned address `0x007ECA50`, every site could reach every bounded
provider root: observed displacements are only 2,602,996 through 2,604,328
bytes, well inside the +/-16 MiB encoding range. Branch reach is therefore not
the blocker.

The calls still cannot be rewritten directly to the four bounded-provider
entries. Stock setup and encode use liblc3's low-level ABI and service-owned
encoder storage; the provider uses explicit config, plan, provider, storage,
and lifetime contracts. There is no one-for-one mapping for the frame helpers,
the two setup calls, and encode. `service_audio.c` is not source-routed in the
current core. A service adapter or source replacement must own provider state
and preserve the recovered packet/buffer behavior before any call patch can be
authorized.

## LTPF overlap

The existing Apple LTPF component is not free space. Its route patches the
stock call at `0x0059145C` inside stock `lc3_encode`; the official instruction
targets `0x00438FB8`, while the current canonical image targets the maintained
provider at `0x00445664`. Its text uses 5,596 of a 5,626-byte cave at
`0x00445664`, and its read-only segment uses 1,980 of a 4,414-byte cave at
`0x004FC648`.

The full encoder already compiles upstream `src/ltpf.c`, so a future full
service route needs an explicit supersession decision. Until then both caves
remain reserved and the existing patch remains live for stock `lc3_encode`.
Removing the standalone LTPF route is not silently assumed; importantly, even
reclaiming both caves in full cannot make this encoder fit.

## Relocation and runtime boundary

The deterministic relocatable object still has 567 unapplied relocations:
400 internal and 167 external. The external set is exactly 12 symbols:
`__aeabi_memclr`, `__aeabi_memclr4`, `fabsf`, `floorf`, `fmaxf`, `fminf`,
`memcpy`, `memmove`, `memset`, `roundf`, `sqrtf`, and `truncf`. This audit does
not infer addresses merely because similarly named stock or overlay functions
exist; every target still needs an authenticated ABI-compatible binding.

The 404-byte `.data` section contains relocated pointer tables and is emitted
with `SHF_WRITE`. No Apollo load-address/run-address or proven immutable-XIP
policy has been assigned. Raw `.text`, `.rodata`, and `.data` artifacts remain
unloadable until a final placement linker applies every relocation and emits a
new OTA receipt.

## Flash-plan reconciliation

The generated `g2/build/flash-plan.json` present during this audit describes
an older 3,952,346-byte Apollo component ending at `0x007FCEBA`, with only
4,422 bytes before the update record. It does not match the current canonical
3,885,668-byte core receipt and is reported as stale, not used as placement
authority. The proof uses the more optimistic current-core headroom, so the
stale plan cannot change the blocked result.

Production routing is therefore **not feasible without moving another
component or shrinking/specializing the admitted encoder by at least 57,652
aligned bytes**. A specialization would require authenticated G2 duration,
sample-rate, and bitrate constraints before removing any tables. Hardware,
acoustic quality, BLE interoperability, stack, and timing qualification were
not attempted and remain blocked by unavailable physical evidence.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_placement.py --pretty
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_encoder_placement
```

The machine-readable contract is
`components/apollo_main/liblc3_encoder/placement_routing_proposal.json`.
