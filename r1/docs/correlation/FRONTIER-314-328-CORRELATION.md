# 314...328-byte frontier correlation

The next five largest unresolved application functions are now source-routed from immutable
body hashes, full direct-call scans, and function-local control-flow review:

| Recovered function | Executable bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x0008B184..<0x0008B2CC` | 328 | `7332ae1847cc0f7137e3d1b464c315dfa0b8b8e80b4d9af5d4ed41a5d5d5c76c` | R1 health clear-all orchestration |
| `0x00051108..<0x00051250` | 328 | `3f7836df81f8fb76d15d03120be74c32734bf62e7f42cd3d9b68286e72738cde` | R1 dual-temperature reducer/adapter |
| `0x000317CC..<0x0003190C` | 320 | `e8a945402151326dbbba0c4e5c8660b42bc21c7e3b3a5da8d0ab02647d32e5ac` | Nordic SDK 17.1.0 `nrfx_saadc_irq_handler` |
| `0x00091B08..<0x00091C42` | 314 | `6048b5e7b5b94000f3143c5918f323df480ea0de6959a19083826ec509f06cb9` | GoMore licensed-provider boundary |
| `0x000651CA..<0x00065304` | 314 | `1d346c3a4978ae586e3e784bb5430d94040c6a40cbac5593600e6e633aac5ea0` | GoMore licensed-provider boundary |

The Ghidra CSV reports 318 bytes for `0x000317CC` while also reporting the inclusive end
`0x0003190B`. The recovered instruction stream is continuous through the two-byte back-edge at
`0x0003190A`, so the corrected executable extent is 320 bytes. The summarizer records both the
318-byte inventory value and the independently verified 320-byte executable extent.

`0x0008B184` has one direct caller at `0x0004603A`. It conditionally clears the configured
time-series database, requests sleep-history clearing, obtains the current UTC offset and local
day start, clears four scalar daily caches, the 144-bucket activity cache, and the HRV cache,
refreshes their day/timezone metadata, and passes a zeroed aggregate to the health-algorithm
boundary. `r1_health_clear_all_caches` implements the six R1 cache transitions and returns typed
actions for FlashDB, sleep, and licensed health-algorithm providers. It performs no persistent
database mutation itself.
There is no persistent database mutation in the clean-room API.

`0x00051108` is called at `0x0003CD3A`, `0x0004F1CE`, and `0x00062C7A`. The stock routine opens
two GXT310 channels, waits `0x50` ticks, takes ten paired readings separated by five ticks,
discards one minimum and one maximum from each channel, divides the remaining sum by eight with
signed truncation toward zero, applies independently signed calibration offsets, and emits a
two-sensor result. `r1_temperature_pair_reduce` implements only that deterministic reducer and
calibration rule. Sensor power, I2C, timing, register access, and sample acquisition remain behind
the unresolved GXCAS GXT310 provider boundary.

`0x000317CC` has no direct `BL` caller because it is installed through the SAADC interrupt vector.
Its exact event order and state transitions match Nordic nRF5 SDK 17.1.0
`modules/nrfx/drivers/src/nrfx_saadc.c::nrfx_saadc_irq_handler`: END handling and secondary-buffer
promotion, low-power STARTED sampling, CALIBRATEDONE callback, STOPPED state reset, then the
channel-limit bit scan. OpenR1 already compiles that upstream source; no local IRQ handler is
reconstructed.

`0x00091B08` is called only at `0x0006531C` inside the byte-pinned GoMore tensor graph. It allocates
private tensors, converts private half-precision weights, performs a floating-point convolution,
and releases provider storage. `0x000651CA` has seven callers at `0x000884EA`, `0x00088546`,
`0x0008859E`, `0x000885F6`, `0x00088670`, `0x000886C8`, and `0x00088720` in the gated GoMore sleep
graph and applies private batch-normalization tensors. Both remain licensed-provider-only; no
weights, tensor ABI, formulas, or substitute neural runtime are implemented.

Reproduce with:

```sh
python3 tools/summarize_r1_frontier_314_328.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The two clean-room product APIs are retained at `0x00033D30` and `0x00033F22` in the unsigned
Nordic link; the upstream `SAADC_IRQHandler` is linked at `0x0002F5B4`. The application contains
94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS. Its 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`, and its standalone HEX
has SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.
Code signing, deployment authorization, private keys, and security-enforcement bypasses are
outside this closure.
