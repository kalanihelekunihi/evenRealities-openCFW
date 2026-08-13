# 230...248-byte frontier correlation

The five largest unresolved application functions after the 256...262-byte closure are now
source-routed from immutable body hashes, complete instruction extents, direct-call scans,
function-pointer evidence, and the existing R1 firmware-security audit. Twelve supporting helpers
close the relevant record, provider, and constructor paths.

| Recovered function | Executable bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x000947DE..<0x000948D6` | 248 | `d8a0776a8e0c82ef262d2b0f639bd8a68fe13aa3cb3a1e5b0cbe7a6b0b7dabff` | GoMore licensed-provider-only accumulator |
| `0x00095168..<0x00095260` | 248 | `ed98b97d47a79e50052c11f335e86cc96d8bbb63d0036d6ef578256d86ee2ac3` | R1 `kv.bin` newest-slot reader |
| `0x00035E34..<0x00035F26` | 242 | `f2ecfeb5f11b06acbacf5c0c99c263c724dbdd591208bcf640742140a123a440` | unidentified shared quantized-neural runtime |
| `0x0005E228..<0x0005E314` | 236 | `73c551c618987b0704727618c69a9896b90a535830d159bf49ef337f3631a5c6` | R1 `ep.bin` readiness policy over FAL |
| `0x00062A5C..<0x00062B4C` | 240 | `b817aafc38f47db97d93cffb63f3dcf154fa5f9bf9b4b9eed86ea35c8fadb50f` | R1 legacy device-info formatter |

Ghidra's size column reports 234 bytes for `0x00062A5C`, but its inclusive end and the recovered
instruction stream contain a case-4 branch at `0x00062B46` and default return at `0x00062B4A`.
The corrected executable extent ends immediately before `0x00062B4C`. The five frontier functions
therefore total 1,214 executable bytes (1,208 bytes in the original inventory). Twelve supporting
helpers add 720 bytes. The complete closure is seventeen functions / 1,934 executable bytes
(1,928 inventory bytes): eleven R1 product functions or data accessors, three GoMore-provider
functions, and three blocked shared-runtime functions.

## R1 storage behavior

`0x00095168` is the already documented operation-table reader for the R1-specific `kv.bin` store,
not FlashDB KVDB. It requires initialized partition/device state and non-null destination and
length, selects `slot_count - 1`, reads the 24-byte first-class header, checks its magic against the
registered class, then reads exactly the requested offset and length. Stock does not add a wider
offset-plus-length check at this layer. The existing `r1_kv_store_initialize` and `r1_kv_store_get`
implement the bounded clean-room snapshot selection and class loading; FlashDB 2.0.0 remains the
provider only for `health.db`.

`0x0005E228` finds the `ep.bin` FAL partition, resolves its named flash device, and accepts it only
when its length is at least 8,192 bytes. Missing partition, missing device, or an undersized
partition clears the retained handles and leaves initialization false. The lazy coordinator at
`0x0005E0EC` creates its synchronization object, invokes this readiness path, and requests the
already implemented cursor scan after a newly successful initialization.

`r1_ep_plan_initialization` reproduces only those decisions. It performs no live flash lookup,
read, write, erase, allocation, synchronization, or logging. The caller binds the pinned FAL and
Nordic internal-flash port; `r1_ep_scan_cursor` remains the payload-redacting scan over an injected
8,192-byte buffer.

## Legacy device-info formatter

`0x00062A5C` is called by the recovered legacy command router and formats selectors from request
byte 3. Its fixed-record inputs are the already audited R1 `nv_r1` fields; its selector-4 input is
the caller-supplied 20-byte Nordic identity snapshot. The stock wire results are:

| Selector | Returned length | Bytes after the preserved four-byte request prefix |
| ---: | ---: | --- |
| 0 | 25 | 21 product-BSN bytes, or `0xFF` when its stored length is erased |
| 1 | 25 | 15 product-SN bytes, or `0xFF` when erased, followed by six zero bytes |
| 2 | 13 | six temperature-calibration bytes and only the first three transmitted bytes of a six-byte accelerometer copy |
| 3 | 43 | 36 bytes of `0xFF`, then configuration byte `0x70`, low byte of word `0x74`, and byte `0x78` |
| 4 | 24 | the 20-byte Nordic identity snapshot |

Selector 2 really passes length 13 after writing both six-byte blocks; the clean-room builder
preserves that truncation quirk. Unknown selectors return unsupported. `r1_legacy_device_info_build`
accepts bounded caller-supplied data and returns a maximum 43-byte buffer. It does not read FICR,
UICR, SRAM, or persistence; choose an active link; or expose the stock legacy transport sender.

The seven fixed-record accessors at `0x0007B9C8`, `0x0007B9EC`, `0x0007BA08`, `0x0007BA24`,
`0x0007BA40`, `0x0007BA78`, and `0x0007BADC` are represented as fields in
`r1_legacy_device_info_sources`, rather than duplicated as local storage-provider code.

## Provider boundaries

`0x000947DE` is called only by `0x00094070`, which is reached only from the already gated GoMore
sleep path at `0x00060B80`. It updates a private fifteen-slot per-minute accumulator and uses the
six-byte reset helper at `0x00071B24`. The orchestrator, accumulator, and helper remain
licensed-provider-only; no private GoMore state layout or algorithm is reconstructed.

`0x00035E34` derives quantization parameters for indirect executor `0x000293FC`. Thumb pointer
`0x000293FD` is stored at `0x00074D04` by descriptor constructor `0x00074CE4`. That constructor is
called by model-graph builders independently gated to both GoMore and Goodix. This machinery is
shared by GoMore and Goodix. The pair therefore
cannot be attributed solely to either vendor. It is recorded as an unidentified runtime shared by
GoMore and Goodix and remains `investigate_before_implementing`; generic similarity to a neural
library is not enough to authorize a substitute.

Reproduce with:

```sh
python3 tools/summarize_r1_frontier_230_248.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The retained local functions link at `0x0003635C` (`r1_ep_plan_initialization`), `0x000363BC`
(`r1_kv_store_get`), and `0x000369FC` (`r1_legacy_device_info_build`). The unsigned Nordic
application contains 94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS. Its
95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.
Code signing, deployment authorization, private keys, live device identity reads, provider
substitution, security-enforcement bypasses, and device programming remain outside this closure.
