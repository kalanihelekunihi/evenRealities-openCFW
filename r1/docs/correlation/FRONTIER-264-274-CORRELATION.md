# 264...274-byte frontier correlation

The five largest unresolved application functions after the 280...308-byte closure, plus one
exclusive helper, are now source-routed from immutable body hashes, complete direct-call scans,
and function-local control-flow review:

| Recovered function | Executable bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00067C30..<0x00067D42` | 274 | `70ea4f3fd687ed7d5f41b0903f57c72a0a1959f0ffbcf66bf9de9c6cf90bb07b` | GoMore licensed-provider-only segment expansion |
| `0x00032408..<0x00032518` | 272 | `83301191875e916b0ab3e015539b271619b3a21d73be2ef98c6a6716ce8ed9a9` | R1 five-byte EUS fragmenter |
| `0x0003D9B8..<0x0003DAC4` | 268 | `47429c4059d0ff96affac47defecc12d455f1cff4673df2de03aa81ce8bd1d6a` | R1 battery diagnostic cadence |
| `0x0003EE34..<0x0003EF3C` | 264 | `818b5c79dbb504b629dab1974cb8290f5fab659848e852101c06429815e0680f` | R1 payload-redacting `ep.bin` scan |
| `0x00064274..<0x0006437C` | 264 | `91525fb97e34b1faf918a5895aa06acb208b030ea6dde49d0a8a21d2d1486e04` | GoMore licensed-provider-only IIR filter |
| `0x000641C4..<0x000641F0` | 44 | `1cf6848b2f7eba15d09cf9ce3df20aa0bca3d07db4b4a3d686ea7f08bbe04f0e` | GoMore licensed-provider-only segment-fill helper |

The five frontier functions total 1,342 bytes. Including the helper, this closure source-routes
six functions / 1,386 bytes.

## Product-owned behavior

`0x00032408` has four direct callers at `0x0004E7A4`, `0x0004E804`, `0x0004E862`, and
`0x0004E896`. It is the producer paired with the already pinned EUS receiver. The existing
`r1_fragment_message` implementation preserves its five-byte sequence-plus-UInt32LE-checksum
header, 239-byte payload, descending sequence, 4,096-byte input bound, 17-fragment ceiling, and
non-reflected CRC-32C. Allocation and live BLE transport remain external.

`0x0003D9B8` is called once at `0x00032120` from the R1 battery runtime service. Its wrapping
eight-bit counter requests the status diagnostic every five-cycle boundary. At 30 it also requests
the compensation/full diagnostic and resets the stored counter to zero. The pure
`r1_battery_diagnostic_cadence_step` result contains only those two action flags and the next
counter; it performs no live logging, sampling, PMIC operation, or persistence.

`0x0003EE34` is called once at `0x0005E10A` by the `ep.bin` recovery path. It scans exactly 1,024
eight-byte records in the 8,192-byte two-page partition. The first record whose low header nibble
is not magic `0xA` becomes the first-free cursor. If every record has magic, the cursor follows the
greatest nonzero UInt32LE timestamp, with a later equal timestamp winning, modulo 1,024. When all
records have magic and all timestamps are zero, the stock cursor is one. The clean
`r1_ep_scan_cursor` consumes only a caller-supplied offline buffer and returns cursor/latest-index
metadata: no raw ep.bin payload is exposed, and no flash mutation, logging, or transport occurs.

## Provider boundary

`0x00067C30` is reached only from the already gated GoMore body containing callsite `0x00056F42`.
Its three calls to `0x000641C4` at `0x00067C92`, `0x00067D0C`, and `0x00067D2E` establish the
44-byte helper as private to the timestamp-to-sample segment expansion. `0x00064274` is reached
only at `0x000688A2` inside a gated GoMore caller and applies private floating-point IIR state and
coefficients. These three functions remain licensed-provider-only. OpenR1 does not reconstruct
their private ABI, coefficients, resampling, filtering, or signal-processing behavior.

Reproduce with:

```sh
python3 scripts/firmware/summarize_r1_frontier_264_274.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```

The clean-room EUS, `ep.bin`, and battery-cadence APIs link at `0x00032478`, `0x00036234`, and
`0x00037552` in the unsigned Nordic application. It contains 90,956 bytes of text, 236 bytes of
data, and 132,456 bytes of BSS. The 91,192-byte BIN has SHA-256
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`; the standalone HEX has
SHA-256 `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`.
Code signing, deployment authorization, private keys, security-enforcement bypasses, and live
device programming remain outside this closure.
