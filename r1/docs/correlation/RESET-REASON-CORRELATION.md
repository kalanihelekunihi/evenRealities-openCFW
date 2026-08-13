# Reset-reason correlation

Snapshot: 2026-08-12.

## Result

Two recovered functions / 834 bytes close the boot reset-reason path. A 754-byte R1 product
function recognizes the seven reset causes exposed by the stock nRF52840 build and attaches the
retained reset trace to software resets. An 80-byte R1/Nordic adapter reads the provider register,
invokes that product decoder, stores the result, and clears the original register mask.

The recovered application image has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Exact functions

| Executable extent | Bytes | Clean-room name | SHA-256 | Direct caller |
| --- | ---: | --- | --- | --- |
| `0x00077E98..<0x00077EE8` | 80 | `r1_reset_reason_nordic_adapter` | `5d24b57782f7b573907ef704ee7c3b77eb3e1288b6c5e39d11f3bd2ebc9efda5` | `0x00075FE4` |
| `0x0008198C..<0x00081BF8` + `0x00081FB8..<0x0008203E` | 754 | `r1_reset_reason_decode_and_report` | `1b23f0b5846eac38c0c83c905937dcdae6e3bba0c6ff3411b0b96f5a2ad0764f` | `0x00077EDC` |

The decoder is non-contiguous because Ghidra places embedded literal/string data between its two
code spans. Its hash concatenates only the two executable extents in address order.

## Recovered behavior

The adapter's literal at `0x00077EE8` is `0x40000400`, the nRF52840 `POWER.RESETREAS` register.
The decoder returns the recognized mask while preserving raw input separately in openR1:

| Bit | Meaning |
| ---: | --- |
| `0x00000001` | reset pin |
| `0x00000002` | watchdog |
| `0x00000004` | software system reset |
| `0x00000008` | CPU lockup |
| `0x00010000` | System OFF wake by GPIO detect |
| `0x00020000` | System OFF wake by LPCOMP |
| `0x00040000` | System OFF wake by debug interface |

The complete recognized mask is `0x0007000F`. Raw zero is reported as power-on or brownout. On a
software reset, the decoder reads the retained program counter, return address, and persist tag.
It reads the reboot-caller byte only when the persist tag is `2`; invalid retained CRC suppresses
the entire attached trace.

The stock adapter calls the decoder before writing the original raw value back to RESETREAS. This
is the nRF52 write-one-to-clear lifecycle and prevents stale causes accumulating into the next boot.

## Product/provider boundary

`r1_reset_reason_decode_and_report` is `r1_product_specific` with disposition
`clean_room_behavior_only`. Its verbose SDK/RTT logging calls are observational presentation, not
part of the portable report contract.

The adjacent common logging facade at `0x000914EC`, `0x000915A8`, and `0x00091638` was compared
against Nordic SDK 17.1.0 during this closure. It is not Nordic's `nrf_log_frontend_std_n` family:
those exact provider functions are already independently mapped at `0x000799C0` through
`0x00079A44`, whereas these helpers add separate enable-state, interrupt masking, and product sink
calls. They therefore remain unclassified and implementation-blocked; this closure does not absorb
or recreate them merely because the reset decoder calls them.

`r1_reset_reason_nordic_adapter` is `r1_nordic_sdk_provider_adapter` with disposition
`clean_room_adapter_only_use_nordic_sdk`. OpenR1 supplies only the boot ordering, decoded-report
storage, and calls to Nordic `nrf_power_resetreas_get/clear`; the memory-mapped register semantics
remain in Nordic's `nrf_power.h` provider.

The exact bytes, register literal, caller sets, masks, and source boundary are checked with:

```sh
PYTHONPATH=tools \
python3 tools/evidence/summarize_r1_reset_reason_closure.py
```

## openR1 result

The portable decoder is unit-tested for zero, every recognized bit, unknown-bit preservation in
the raw field, software trace attachment, persist-tag-2 reboot caller gating, fault tag behavior,
CRC rejection, and null arguments. Host, ASAN/UBSAN, and Cortex-M4 builds pass.

The Nordic integration runs before CmBacktrace and the scheduler, saves the report behind a
retained internal `.openr1_reset_reason_api`, and clears RESETREAS through the provider HAL. The
current linked image has text 85,608, data 220, and BSS 132,448 bytes; its HEX SHA-256 is
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and BIN SHA-256 is
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Code signing, boot redirection, and deployment bypass remain outside this implementation.
