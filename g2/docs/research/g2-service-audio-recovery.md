# G2 `service_audio.c` recovery

Status date: 2026-08-12  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: complete linked object and provider boundary closed; production source
not yet routed

## Object boundary

`platform\audio\service_audio.c` occupies
`[0x0057A900,0x0057B444)`, 2,884 bytes, SHA-256
`01864fb4fc778a70c3c50b7999c8a43b86d4f8763479e8cf5e47d7a529207193`.
Fourteen Ghidra-discovered functions account for all 2,676 executable bytes
and 1,073 reachable instructions. The remaining 208 bytes are one four-byte
alignment/string pointer and the terminal literal pool. The following object
begins at `0x0057B444` with an inline CMSIS NVIC helper belonging to
`driver\pdm\drv_pdm_production.c`; it is not audio-service data.

The object has 113 direct calls: nine internal and 104 external. Whole-image
ingress finds 33 direct BL sites to real entries, no stored pointer to an
object entry, and no strict interior ingress. One raw BL-shaped word at
`0x005FA9D6` overlaps liblc3 generated table data and is recorded separately;
it is not executable ingress.

## Recovered behavior

The first three functions form the LC3 adapter:

- map the supported PCM format enum to two, three, or four bytes per sample;
- lazily initialize and cache an encoder; and
- validate frame geometry and encode one or more mono/interleaved frames.

`SVC_PcmAppRegister`, `SVC_PcmAppUnregister`, and
`SVC_PcmAppProcessData` implement two source slots. If a callback is
registered, incoming PCM is dispatched to it. The only three static
registration callers select exactly two already closed production-microphone
callbacks: `0x0058F4E4` and `0x0058F5E0`. The sole `BLX` at `0x0057AE4A` is
therefore resolved to a two-entry first-party set, not an open indirect edge.

Without a registered callback on source zero, the fallback path:

1. acquires the 1,600-byte audio-algorithm work buffer;
2. computes SSR and TDOA/angle through the closed `service_algo.c` object;
3. encodes the PCM with liblc3;
4. appends the two signed 16-bit results;
5. emits a periodic diagnostic/hexdump every 40 frames; and
6. forwards the completed packet through the BLE message facade.

The remaining eight functions implement optional rotating PCM capture under
`/audio/`, format `%s%s_%02d%s` names with a `.pcm` suffix, find the first
unused sequence number, create the directory if absent, rotate at a configured
byte ceiling, write, and close each of two source recorders.

## Provider closure

Every external direct edge terminates at a known provider:

| Provider | Calls | Disposition |
|---|---:|---|
| EasyLogger diagnostics/hexdump | 76 | admitted 2.2.99-compatible core at `a596b264…` |
| IAR DLIB memory/formatting | 8 | bounded/source-recreated runtime seam |
| CMSIS-FreeRTOS tick wrapper | 3 | exact v10.5.1 source at `d213f261…` |
| Google liblc3 | 5 | admitted v1.1.3 tagged baseline at `96a3af0…` |
| closed `service_algo.c` | 2 | complete first-party neighboring object |
| source-owned file runtime | 7 | production wrappers over littlefs |
| littlefs backend adapters | 2 | admitted v2.10.1-equivalent provenance |
| first-party PCM notification | 1 | bounded BLE message facade |

The LC3 calls are precisely `lc3_frame_samples`, `lc3_frame_bytes`, two
`lc3_setup_encoder` calls, and `lc3_encode`. Their source/version proof is in
[`g2-liblc3-source-recovery.md`](g2-liblc3-source-recovery.md). The object
contains no embedded third-party definition and adds no discriminator beyond
that independently admitted codec boundary.

## Reproduction

The function, provider, and closure records are:

- `tools/manifests/g2-service-audio-function-map.tsv`;
- `tools/manifests/g2-service-audio-provider-map.tsv`; and
- `tools/manifests/g2-service-audio-closure.tsv`.

`tools/analyze_g2_service_audio.py` authenticates the image, object partition,
call graph, whole-image ingress, callback registrations, provider provenance,
closed callback/algo objects, and absence from the production overlay. Run
`make service-audio-closure` for the focused analyzer plus regression tests.

Production source routing remains separate first-party implementation work.
It depends on the target LC3 integration gates, audio buffer ownership,
filesystem recording policy, concurrency/lifetime review, and device tests;
none is an unresolved third-party family or opaque utility-function gap.
