# Combined Bosch configuration path execution

Seven normal source objects pass 1,680 combined stock/source scenarios
through the real C configuration sequence, interface and device
initializers, device checker, accelerometer config/enable routines, power
setter, FIFO setter and their parameter/bitfield helpers. Register reads,
register writes, delays and logging are modeled. Firmware sources are
unchanged; this extends verification beyond mocked configuration steps.

The successful path performs 18 register I/O operations: chip ID read;
range and ODR writes; accelerometer enable read/write; power-disable
read/write; three FIFO read/low-write/high-write groups; and power-enable
read/write. The probe asserts that exact prefix and compares all public
context accesses, register values, payloads, delay calls, log strings and
statuses, return values, context/guards, register map, callee-saved
registers, stack restoration and interrupt masks. Unexpected execution
of any other probe stub fails the comparison.

The matrix covers every uniform register seed byte at rates 25, 50, 100
and 200; both `-1` and `-2` register errors at each of the 18 I/O positions;
changing log-mode results; randomized register maps, rates and masks;
wrong/missing chip-ID responses; and partial read outputs. Failed writes
may commit their payload in the model, checking that subsequent error
handling preserves existing changes rather than rolling them back.
There are 1,042 successful configurations in the matrix.

For complete successful reads, an independent register oracle verifies:

| Register | Final value |
| --- | --- |
| `0x40` | selected ODR code, 6 through 9 |
| `0x41` | 2 |
| `0x7d` | initial value OR 4 |
| `0x7c` | initial value OR 1 |
| `0x48` | initial value AND `0xfc` |
| `0x49` | (initial value AND `0x83`) OR `0x40` |

This includes the reserved low two bits in FIFO register `0x49`. Delays
include 25,000 microseconds after the accelerometer-enable write even
when it fails, and 1,000 microseconds between successful low and high FIFO
writes. No cleanup or retry is inserted on failure.

The controlled link places the context at `0x2001e4e8` and bus-address word
at `0x200076c0`, normalizing callback code pointers by role. These are
probe placements, not final layout proof. Mocked APIs clobber caller-saved
registers and require eight-byte stack alignment. Private frames differ.
Direct transport, physical bus operation, timing, complete fault state,
final linking and byte identity remain unverified. No source-plan
selection or G2 workflow gate changed.

The bound report remains `build/sources-goal-r1-bma-config/report.json`:
all 562 units compile, with no failures or duplicate strong symbols and
227 application / 34 bootloader imports. [Machine-readable evidence](bma-config-integration-review.json)
binds the seven input sources/objects, report, earlier REA-backed reviews
and ignored probes under `build/goal-r1-bma-config-integration/`.
