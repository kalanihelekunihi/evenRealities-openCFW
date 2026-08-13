# R1 structured-log cache correlation

## Disposition

Sixteen functions / 1,802 executable bytes are admitted as R1-specific structured-log record,
live-cache, configuration, and persistence-orchestration behavior. Twelve are Ghidra inventory
functions; four exact functions / 82 bytes at `0x00091490`, `0x00091494`, `0x000914A0`, and
`0x000914F8` were omitted by Ghidra and are manual provenance supplements.

No third-party implementation has been identified for this record/cache layer. It is not Nordic's
logging frontend: the firmware separately links and byte-matches Nordic SDK 17.1.0
`nrf_log_frontend_std_0` through `_std_6` at `0x000799C0...0x00079A44` and `std_n` at
`0x00090FEC`. The R1 layer instead wraps the Nordic 22-bit standard-log address/header convention
in a product record, copies bounded transient arguments into a separate live cache, coordinates
the product `log.bin` store, and supplies the cache tail to the R1 composite diagnostic export.

The functions are therefore `r1_product_specific` / `clean_room_behavior_only`. This permits an
independent implementation of the documented record and cache contract. It does not permit local
copies of Nordic, Arm/toolchain, FreeRTOS, the unidentified clock/calendar or device-registry
providers, nor does it authorize a raw private-log export sender.

## Exact closure

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x00041C5C` | 166 | live-cache copy/peek primitive |
| `0x00041D08` | 36 | available-byte count |
| `0x00041D30` | 332 | typed structured-log argument encoder |
| `0x00041E80` | 194 | live-cache append and flush policy |
| `0x00046FD4` | 616 | format-aware structured-log argument encoder |
| `0x000514BC` | 32 | adapter to the abstract clock record |
| `0x000590A0` | 6 | log-export active-state query |
| `0x00091460` | 48 | live-cache read facade |
| `0x00091490` | 4 | live-cache count facade; manual supplement |
| `0x00091494` | 6 | threshold setter; manual supplement |
| `0x000914A0` | 66 | periodic 4,096-byte persistence; manual supplement |
| `0x000914EC` | 6 | mode getter |
| `0x000914F8` | 6 | mode setter; manual supplement |
| `0x000915A8` | 140 | typed public facade |
| `0x00091638` | 138 | format-aware public facade |
| `0x00091864` | 6 | clock-source availability getter |

Every body hash and complete direct `BL`/`B.W` caller set is frozen by
`summarize_r1_structured_log_cache.py`. This includes 2,554 direct calls to the mode getter and 853
direct calls to the format-aware facade, so their system-wide use is checked as an exact aggregate
rather than inferred from a few representative callers.

The former largest unknown, `0x00046FD4`, has the public facade at `0x00091638` as its sole caller.
The sibling encoder `0x00041D30` likewise has `0x000915A8` as its sole caller. Both converge on
the 194-byte cache append routine at `0x00041E80`; its only two callers are those encoders.

## Recovered record and bounds

Both encoders construct a record beginning with byte `0x7B`, one rolling sequence byte, the RTOS
tick modulo 1,000, fixed header bits `0xDC000000`, a time value chosen through the abstract clock
adapter, and the packed Nordic-style severity/module/format metadata. The fixed prefix consumes
12 bytes.

The typed encoder copies at most eight ordinary four-byte arguments. Its special string-bearing
record modes copy at most sixteen bytes from each admitted string and further cap the number of
such strings. The format-aware encoder parses flags, width, precision, `l`/`ll`, and `h`/`hh`
qualifiers only to determine argument width and safe capture. It:

- caps ordinary captured arguments at 32 bytes;
- copies at most sixteen bytes for `%s`, right-aligning overlength strings to retain their tail;
- consumes eight-byte values for `ll` and floating conversions with ABI-correct alignment;
- delegates floating conversion to the Arm toolchain runtime; and
- emits the bounded record to the common live-cache append routine.

The cache is a circular byte buffer described at runtime by `0x200068F4`. The copy primitive can
peek or consume across wrap, the count helper computes available bytes from the same read/write
indices, and append refuses a record that cannot fit. Product mode selects either a 236-byte
immediate product dispatch threshold or a 4,096-byte storage-event threshold. The periodic worker
does not run during a composite log export, requires 4,096 cached bytes, applies the recovered raw
10,000 timing gate, consumes exactly one page, calls the separately bounded `log.bin` page writer,
and yields through authenticated CMSIS-FreeRTOS.

## Provider exclusions

The local boundary may call but must not recreate:

- Nordic SDK 17.1.0 logging sources and their independently source-routed frontend functions;
- authenticated CMSIS-FreeRTOS tick access and FreeRTOS critical-section entry/exit;
- Arm C/EABI `memcpy`, `memset`, `strlen`, and floating-conversion helpers;
- the unresolved generic device operation used by `0x000514BC` to obtain its clock record;
- the unresolved time/calendar provider selected when a synchronized local timestamp exists; and
- the `log.bin` flash writer, composite private-log exporter, and transport sender, which remain
  separate boundaries and are not implemented by this closure.

The cross-firmware string hit at G2 address `0x00346FD4` is an unrelated GX8002 power diagnostic;
address coincidence is not attribution evidence for the R1 body at `0x00046FD4`.

## Reproduce

```sh
python3 scripts/firmware/summarize_r1_structured_log_cache.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```

The summarizer is static and reads no live ring or private log content.
