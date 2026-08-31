# G2 GX8002 codec-host recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Result

The retained first-party translation unit `platform\audio\service_codec_host.c` is closed as a linked binary object in the official G2 2.2.6.10 OTA image. Its physical interval is `[0x0057BA88,0x0057DC40)`: 8,632 bytes with SHA-256 `83a042c43132baea06c3377689d7bc90b789fabc4bea39f25a4a4fe66cac261a`.

The object contains 26 linked functions. Thirteen are retained-path anchors and thirteen adjacent pathless bodies were restored from source order, call topology, literal ownership, and the enclosing IAR object boundary. Their 7,318 concatenated body bytes hash to `88264b60441f49660eba62171af67a9303c92985e90ab5539fda6b8b864a0b4f`. Seventeen owned alignment/literal-pool gaps total 1,314 bytes and hash to `9ed4d2b885b71bea352cf06d2a972bb79708bbb2e3d9d48db80e7a54a618bd34`.

This remains binary inclusion and behavior closure rather than historical source recovery: no authenticated vendor source inventory or license was found. A separately authored MIT production reconstruction now implements all 26 linked entry points in `components/apollo_main/core_overlay/service_codec_host.c`. The Apple-clang Cortex-M55 build emits 4,262 bytes of source text plus 38 bytes of runtime alignment, authenticates 111 external relocations, and routes all 26 stock bodies through guarded `B.W` replacements. The 7,318 body bytes are therefore source-owned; the 1,314 bytes of literal pools and alignment gaps remain authenticated official data.

## Function inventory

The exact ledger is pinned in `tools/manifests/g2-service-codec-host-function-map.tsv`. Twenty-three names survive as exact diagnostic strings. They cover:

- host initialization, message packing/unpacking, UART send/read, and request/response transport;
- version, beamforming mode, wakeup mode, microphone-state, gain, DMIC, I2S-output, and one-bit-delay commands;
- the corresponding `SVC_*` validation wrappers; and
- asynchronous `GX8002_GetVoiceEvent` handling.

Three pathless leaves retain descriptive `semantic_*` labels: UART cleanup, magic-word comparison, and message release. No unsupported historical name is assigned to them.

## Wire protocol and state

The wire magic is ASCII `BUXX`. A packed message begins with a 14-byte header:

| Offset | Width | Field |
| --- | ---: | --- |
| 0 | 4 | magic |
| 4 | 2 | command |
| 6 | 1 | sequence |
| 7 | 1 | flags |
| 8 | 2 | body length |
| 10 | 4 | header CRC-32 over bytes 0 through 9 |

The body is limited to 16 bytes. A flag selects an optional four-byte body CRC. The sequence byte lives at SRAM `0x20075013` and increments per packed message. Outbound and inbound staging buffers are at `0x2007399C` and `0x2007397C`.

Initialization configures the UART for 115,200 baud. The blocking reader acquires the 14-byte header first, then the declared remainder, yielding for one tick when the UART reports no data. The request/response path initializes transport, sends, blocks for a response, tears transport down, and unpacks the result. Command helpers retry up to three times.

The recovered commands are read-version `0x02`, switch-beamforming `0x07`, switch-wakeup `0x08`, microphone gain `0x0B`, DMIC open `0x0C`, DMIC close `0x0D`, one-bit microphone delay `0x0E`, I2S output `0x0F`, and query-microphone-state `0x70`. The delay path sends the exact fixed request `425558580e0101000000d4db2f68`. Public `SVC_*` wrappers validate the command-specific response status and length before reporting success. The source reconstruction additionally rejects a voice-event response shorter than three body bytes before decoding its event and value fields.

## Ingress and false-pointer closure

An exhaustive Thumb scan finds 83 calls to exact entries: 58 intra-object and 25 exterior. Their ordered little-endian pair digest is `f4f9f14be8990a0ed823332c2c4bdd83e0bae39e57ecf9b760558ab50bad79da`. The 26 bodies contain 379 direct calls with digest `a688287e438040cc3e97f7a0cfece0dd532fa9d6efab5b105cb64d1033f5be78`. No direct call or `B.W` targets a strict interior.

The all-byte four-byte-window scan finds one numeric collision: aligned data at `0x006309BC` contains `0x0057C001`, which normalizes into the middle of the unpacker. It is not an exact entry, stored function pointer, branch target, or consumer. There are no aligned stored exact-entry pointers. This fail-closed distinction prevents arbitrary data from becoming false ingress.

## Reproduction

Run:

```sh
make service-codec-host-closure
make source
```

The analyzer authenticates the official image, all three object manifests, every body and owned gap, both object boundaries, the retained path and its four pointer cells, 23 exact symbols, call topology, pointer-like windows, protocol literals, all 26 source leaves, 111 relocations, 26 guarded redirects, component ownership, and package/flash-plan identities. The candidate suite host-executes success, retry, CRC, truncation, allocation, cleanup, fixed-message, wrapper-status, and voice-event bounds paths, then compiles every selector for Cortex-M55.

## Limitations

- The historical source-only function count remains unknown because the vendor source file is unavailable.
- Semantic labels are clean-room descriptions, not recovered symbols.
- Binary closure does not grant a license or justify copying vendor implementation text.
- Software implementation, target compilation, guarded routing, component assembly, and OTA packaging are closed.
- Live UART3/GX8002 command/response, audio, DMIC, I2S, and asynchronous voice-event behavior is explicitly blocked by unavailable physical evidence: the authorized right temple is nonresponsive, the authorized left temple must remain stock, and no responsive authorized pair or golden codec/UART capture is available.
