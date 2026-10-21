# R1 shared i2c_5 transport integration

This source converts the fixed-state bus wrappers at `0x50510` and `0x50534`
and the NFC board-resource operations at `0x504C0` and `0x504D8` to C. It uses
the existing reconstructed registry implementation and actual ST25 driver and
board-binding objects. No missing operation is replaced with a success stub.

The state section preserves the recovered layout: GPO handle at `0x20006838`,
bus handle at `0x2000683C`, and the 20-byte shared request at `0x20006840`.
The read path updates command, register, read buffer and read length. The write
path updates command, register and write length, but changes its buffer pointer
only when the caller supplies a non-null pointer. All other fields and padding
retain their prior bytes. Discovery must bind the actual device handle; no
fabricated device is installed by this component.

## Corrected GPIO sequence

Stock `nrf_gpio_pin_set` at `0x79434` writes GPIO `+0x508` (OUTSET). For P1.10
that is address `0x50000808`, bit `0x400`. The corresponding OUTCLR address is
`0x5000080C`. Resource acquire performs OUTSET, delay(10 ms), OUTCLR,
delay(10 ms), then registry open. Release performs registry close, then OUTSET.
This corrects the reversed low/high interpretation in the historical boundary
note; it makes no claim about the downstream electrical effect.

## Build and bounded verification

```
make -C r1 i2c5-candidate
make -C r1 i2c5-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

The target compiles the transport and registry under compatible enum/ABI flags,
then makes a relocatable link with the actual ST25 implementation, register
implementation and R1 board binding. Compiler memory helpers, strcmp and the
millisecond-delay seam remain unresolved. This is component integration, not
an executable application image.

The oracle compares 782 calls against authenticated original Thumb, executing
the actual compiled veneer, request wrapper and registry-dispatch code. It
checks null devices, missing operations, provider status propagation, full
request bytes and untouched padding, address truncation, lengths through 65535,
null-buffer retention, and ordered MMIO/delay/provider actions. Final electrical
bus operations and delays are intercepted in emulation; they are not supplied
as production implementations. Resource functions have void contracts, so
incidental R0 values are not compared. The integrated transport now uses the native dispatchers described below.

## REA and Ghidra evidence

`python3 r1/tools/prepare_stock_analysis_elf.py` creates an analysis-only ET_EXEC
wrapper with `.text` at `0x27000` and verifies an exact round trip of all 646408
application bytes. It adds transparent analyst labels for three reviewed entries.
This wrapper contains retained original code and never counts as C source or a
source-build input. Import it with automatic ELF format detection. Explicit
language selection in Ghidra-MCP uses raw import; ET_REL also receives a default
rebase. Neither is appropriate for this absolute-address analysis.

REA and Ghidra-MCP both observed the GPIO setter at the correct `0x79434`
address and its write at `port+0x508`. Ghidra-MCP's 20-byte memory readback also
matches the original image. Dossiers and wrapper identity are stored under
`pre-consolidation:r1/research/source-build/i2c5/`. Both adapters use Ghidra, so their agreement
is not independent semantic validation. The original-byte execution comparison
is separately recorded in `verification.json`.

## Native registry and discovery

The native registry lookup (`0x85CE0`) and registration (`0x85D58`) now use
source-owned list storage at `0x20007680`, preserving the 24-byte record and
stock duplicate-check/validation order. NFC initialization (`0x50464`) lazily
looks up GPO and bus handles, but unconditionally refreshes the ADC cache
(`0x50D3C`, storage `0x20006854`). It writes P1.10 configuration `0x30F`
and OUTSET `0x400` on every invocation.

`registry-bootstrap-verification.json` records 62 comparisons against original
Thumb: list lookup/append/rejection, case sensitivity, cache retention,
ADC refresh/clearing and repeated MMIO writes. The candidate executes strcmp
from the authenticated GNU runtime distribution; that binary test dependency
does not establish C-only runtime closure. NULL names in a nonempty list remain
an excluded fault contract. Actual board record population and full startup
integration remain unresolved.

Seven native operation dispatchers now replace the older contextual dispatchers
on this transport path. Their recovered signatures preserve the device-only,
three-word, and four-word operation contracts. They do not add a NULL-table
fallback. `registry-dispatch-verification.json` records 84 stock comparisons,
including 21 matching unmapped-read addresses/widths for NULL operation tables.
This establishes bounded emulated fault behavior, not physical exception state.
Ghidra-MCP readback of both adjacent dispatcher bodies matches the stock bytes.
The historical contextual implementation remains for other consumers and still
has its documented hardening differences.

## Native software-TWI registration records

`r1/src/application/software-twi/stock_records.c` supplies the four native binding
wrappers (`0x56508/20/38/50`) and a typed, contiguous 448-byte storage section.
Each 112-byte record contains the engine at +8, registry record at +52, and
nine-word operation table at +76. Wrappers copy the name, bind that embedded
table, and return the actual registry registration result. The registration
oracle places the section at stock address `0x20007400` and compares all record
bytes, list-head changes and return values in forward/reverse order, with
existing unrelated devices and repeated duplicate registrations (48 cases).

The storage declaration is not a recovered initial-data seed. GPIO callbacks,
operation-table functions and scatter-loaded values still need source-owned
installation. No placeholder callbacks or fabricated populated records are
installed by these wrappers.

## Native TWI lifecycle

The native record module now supplies four open and four close bodies. Open
preserves the stock nonzero-flag shortcut, configures both pins through their
installed callbacks, drives both high, then sets the flag. i2c_4 additionally
uses the real Nordic output configuration wrapper twice. Close invokes both
pin-release callbacks before clearing the flag; it is idempotent.

`software-twi/lifecycle-verification.json` records 512 stock comparisons using
actual compiled Nordic callbacks, including repeated calls, flags 0/1/2/255,
port boundaries, complete record state (callback relocations normalized), and
ordered MMIO writes. No GPIO callback is intercepted in this test. Invalid
callback pointers, physical electrical effects, delay/transfer installation,
and a complete application image remain open.

## Native transfer adapters

Eight native read/write adapters now consume the fixed native records and call
the compiled transaction/primitive bodies. The dedicated integration build
compiles the engine with matching short-enum flags. Native single-byte writes
fetch their payload before wire callbacks, matching stock's ordering. Reads
retain the bus-specific register/count widths and i2c_5 merged closed/null
status. i2c_4 writes omit a register phase and retain a 16-bit payload count.

`software-twi/adapter-verification.json` records 570 stock comparisons with
actual compiled transaction and primitive bodies. Cases include NULL requests,
open flags 0/1/255, lengths 0/1/2/257 and phase-specific NACKs, checking full
callback traces, engine state, return statuses and payload buffers. GPIO/delay
callbacks are intercepted. NULL payload buffers and invalid callback states
remain excluded: reused reconstructed transaction bodies still contain extra
validation guards. Native table installation and full image linking remain open.

## Source-owned native initial configuration

The earlier zero-storage/installation gates for these four TWI records are now
closed at component scope. Typed C initializers populate names, recovered
pins/pull/delay scalars and real compiled GPIO/delay/lifecycle/transfer callbacks.
Lifecycle operation pointers accept the device argument; transfer pointers use
the four-word registry ABI with an ignored final word. No incompatible function
pointer casts or retained executable data initialize these tables.

`software-twi/native-initialization-verification.json` checks all 448 bytes
against original scatter execution, normalizing explicit name/code relocations
and verifying each compiled callback binding. It then executes 44 registration,
open/read/write/close comparisons through the actual native registry and provider
tables, without intercepting callbacks. MMIO is emulated with zero GPIO inputs;
therefore ACK/data are synthetic. Newlib strcmp remains a binary test dependency.
Delay cycles, invalid-buffer fidelity, full startup and the application link
remain open. These initialized records cover four TWI buses, not all board
providers (for example GPO and ADC records).

## Native NULL-payload fidelity

The native engine build now uses `SOFTWARE_TWI_NATIVE_CONTRACT=1` and
`-fno-delete-null-pointer-checks`. Its provider/transaction guards are omitted;
the separately compiled contextual reconstruction keeps its guard behavior.
The NULL-payload gate described above is now closed for the tested native
adapter cases: all 570 comparisons pass, including 76 matching unmapped reads
or writes, and matching early NACK returns. Access type/address/width and all
preceding callbacks are compared. Physical exception state and invalid callback
contracts remain unproven; this is not an all-input fault-equivalence claim.
