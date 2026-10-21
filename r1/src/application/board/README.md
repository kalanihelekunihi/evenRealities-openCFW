# Combined native board-provider component

`build_native_board.py` links each component exactly once: native registry,
shared i2c_5/ST25 glue and API, four TWI records, seven GPIO records, three ADC
records, and the actual pinned Nordic GPIOTE/SAADC provider objects. This is
a relocatable component, not a complete application image.

```
make -C r1 native-board-candidate
make -C r1 native-board-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

The original-versus-compiled oracle registers all 14 records under all six
group orders and passes 54 comparisons. It checks names, record addresses,
operation-table addresses, list ordering, complete shared NFC state and ordered
MMIO writes. NFC discovery obtains actual `nfc_gpo_irq` at `0x200071AC`,
`i2c_5` at `0x20007584`, and `vnfc_rect_adc` at `0x20006F58`.

This combined test found and corrected missing initial values in the shared
request: command `0xA6`, write length 1 and read length 1. Repeated discovery
retains lazy GPO/bus handles and refreshes the ADC handle; clearing the list
clears ADC while retaining cached GPO/bus, matching original behavior.

No handle or callback is prebound in the test. The fatal ADC error and ST25
millisecond-delay seams trap if invoked; neither path is exercised here.
Newlib memory/string routines are attributable binary test dependencies.
Physical hardware, full startup/RTOS integration, C-only runtime closure and
original instruction/whole-image identity remain unproven.

The memory/string references above are now supplied by the source-compiled
runtime candidate (`r1/src/application/runtime/README.md`). The current board oracle
links no GNU/newlib binary archive. Remaining production references are the
ADC fatal-error and ST25 millisecond-delay seams; original runtime instruction
identity remains unproven.

The error-log/getter and millisecond-delay wrappers are now compiled in
`stock_seams.c`. Stock error handling at 0x4E5BC is conditional logging and
returns; it does not reset or halt. All 1,798 seam comparisons pass, including
all mode flags and backend mutation between volatile reads. Delay checks
compare work-unit calls, not original cycle timing. The current component's
only unresolved references are `r1_structured_log_format` and
`nrf_log_frontend_std_1`; both remain real logging providers. The board oracle
traps if either backend is reached rather than supplying a success stub.

`structured_log.c` now supplies the native formatter wrapper plus clock/export
state getters. It checks the clock gate, suppresses mode-bit-0 logging while
export-active is nonzero, packs the descriptor's low 22 address bits under the
marker's upper 10 bits, and forwards the native variadic cursor after restoring
the interrupt mask or leaving the task critical region. CMSIS intrinsics come
from the authenticated SDK header, not copied executable bytes.

All 6,656 comparisons pass across mode bytes, gates, task/ISR contexts, BASEPRI
values, marker bits and three variadic words. Critical calls and final encoding
are intercepted in that oracle. The board link now exposes the next real
requirements: Nordic log frontend, structured encoder and FreeRTOS critical
entry/exit. State-cell writers, actual encoding, scheduler integration and
physical asynchronous exceptions remain open.

The board now consumes the actual source-compiled Nordic critical entry/exit
functions selected from `port_cmsis.c`. Their recovered assertion contract is
scoped to that translation unit. All 1,040 stock comparisons pass, including
104 assertion faults. The logger's 6,656-case oracle also passes without
intercepting critical calls (only final encoding is intercepted). The board's
remaining references are the structured encoder and Nordic frontend. This
closes critical-call linkage for this component, not whole scheduler startup.

The compact encoder at 0x46FD4 is now compiled in `structured_encode.c`.
Its 12-byte prefix and up-to-32-byte payload preserve severity filtering,
sequence wrap, tick remainder, timestamp selection and the original parser.
Integers occupy four bytes (including the low word of aligned 64-bit values);
strings occupy 16 bytes, retaining a long string's suffix and zero-filling
short or NULL strings. Precision-star operands and ignored/unknown conversions
follow the original argument consumption, rather than a general printf policy.

All 1,729 comparisons pass on exact frame bytes and external call order,
including alignment, overflow and string-suffix cases. Time sources, floating
conversion and final cache append are intercepted. Floating input bits and
packing are tested; IEEE conversion itself is not supplied by this encoder.
The board now exposes these real dependencies in addition to the Nordic
frontend. The unchanged pinned musl subset also supplies source-compiled strlen.

`structured_time.c` now supplies native RTC timestamp adaptation, backend
get-time thunk and local timestamp arithmetic. It uses a zeroed 64-byte registry
request and returns the word at +44 regardless of dispatch status. Local time
calls the installed backend with NULL context and adds signed minute offset
multiplied by 60, with 32-bit wrapping. Unbound backend access is not guarded.

All 185 comparisons pass, including 70 matching unbound reads, ignored provider
statuses, missing devices/operations, extreme timestamps and signed offsets.
Final RTC/backend operations are intercepted; actual RTC record registration,
clock-source installation, synchronization and physical clock behavior remain
open. The fixed roots begin unbound, matching stock startup. The board's current
references are Nordic log frontend, kernel tick, float conversion and cache
append; the two timestamp consumer symbols are resolved by compiled C bodies.
