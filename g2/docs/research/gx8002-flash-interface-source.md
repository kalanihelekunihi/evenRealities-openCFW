# Upstream flash interface identification

The authenticated NationalChip SDK at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` supplies the `GX_FLASH_DEV` interface
in `include/driver/gx_flash.h`. With `CONFIG_MTD_TESTS` disabled, its 30 slots
match the 120-byte shipped table at runtime 0x20026504 (package 0x18518).
There are 23 non-null pointers. The gettype slot agrees with the observed
routine that returns the selected device's first field; the OTP-lock slot
agrees with the status-register lock sequence already inspected.

`analyze_gx8002_flash_interface.py` authenticates the header against the pinned
git blob, records its SHA-256, parses the declarations with the test-only
fields removed, and inventories each pointer and package offset. The report
is `gx8002-flash-interface-inventory.json`. This is upstream-backed layout
identification, not proof that every implementation matches its declaration.
Each callback still needs decoded behavioral qualification.

This mapping names the remaining recovery work: ordinary read/program/erase,
write-protection controls, OTP operations and UID reading. Null interface
slots are observed absence of operations; they are not newly introduced stubs.
The interface table and its implementations remain retained in the experimental
package until separately replaced and qualified.

Additional native resume-initializer probes: priority register allocation,
priority plus disabled shrink wrapping, and a shorter lexical lifetime for the
configuration local each still produce 208 bytes with a 36-byte frame. They do
not resolve the stock 32-byte frame comparison. Probe outputs remain separate
from the candidate and are not admitted.

A separate constant-configuration probe resolves the earlier frame-size issue.
Changing only the initial zero configuration local to static const and placing
its four-byte source-defined value after the function in the existing envelope
produces 212 bytes total and a 32-byte frame (12 saved + 20 outgoing arguments).
The recovered platform configuration operation9 reads the input twice and
writes only A000003C and 20027314; it neither modifies nor retains the pointer.

The full executor now accepts an explicit read-only configuration mapping for
this probe, validates the pointed-to zero and operation9, and otherwise retains
the original stack-input checks.198 stock/probe cases match complete traces,
return values and32-byte frames. The probe ELF's final four bytes were checked
as zero at100246C0. This is not yet the canonical initializer or an admitted
replacement: reproduce the build in the normal builder, pin source-defined
constant ownership, add rejection tests and run the complete admission path.
Probe artifacts: build/gx8002-board/flash-constant-probe.c/.o/.elf/.ld/.txt.

The constant-configuration design is now canonical. The normal macOS builder
links208 bytes of reconstructed code/literals at100245F0 and a distinct4-byte
source data section at100246C0, covering the complete212-byte original envelope.
It validates the constant section location, zero value and relocation absence;
the admission report accounts for those four bytes as data, not executable C.

Full comparison passes198 cases with equal32-byte frames. Selection coverage
is also rerun. Calls now require the complete32-byte frame, and return checks
cover all callee-preserved registers. Seven rejection tests cover missing or
nonzero constants, wrong constant address, missing or oversized call frames,
wrong configuration operation and unknown helpers. The platform-config source
hash is recorded to bind the read-only-input assumption to recovered code.

The historical split setup/return tools now route to the full continuous
verifier. Their older independently supplied state and configuration-output
assumption are superseded. Both entry points pass198 cases. Admission is
registered; full codec integration is running. Physical startup composition
and device qualification remain open.

Resume initializer integration completed with261 passing tests. The macOS
codec now owns119 C functions /135 code occurrences,24 data regions and159
total replacement regions:8388 C bytes,2216 source data,80 metadata,326 fill
and315082 retained bytes. Codec SHA:
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
The original32-byte frame is preserved. No physical execution or source-only
completion is claimed; remaining board admission and opaque regions continue.
