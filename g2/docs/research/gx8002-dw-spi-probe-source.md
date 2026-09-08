# DW SPI probe C candidate

The reconstructed probe uses authenticated SDK `spi_master` types and the
private-state prefix recovered from the fully matched SDK object. Native macOS
C-SKY compilation emits 256 bytes within the 268-byte stock region at package
0xfa0c (runtime 0x10206480). The candidate remains unregistered and unqualified.

C preserves the observed pointer/callback initialization, module-14 clock calls,
threshold probing with 256 attempts, the special mismatch-at-257 result, FIFO
drain and busy polling, clearing of active message/transfer, master registration
and IRQ 16 registration. The threshold pointer used for the final zero write
is retained from the last probe iteration, matching the decoded address flow.
Existing nonzero depth fields bypass probing. No polling timeout or validation
has been invented.

The next qualification must compare ordered MMIO/state operations, callback
addresses and ABI against stock for preconfigured depths, early/saturated/all-
success probe outcomes, receive drain sequences and delayed busy completion.
Clock and registration helpers require composition beyond an injected-call
model. Compilation alone is not evidence of hardware operation or complete
source recovery. The linked callback addresses still refer to existing code;
this candidate does not claim their bodies as newly reconstructed source.

An independent transaction model now covers initialization writes, helper
arguments, existing-depth bypass, attempted readback values 2 through 257,
zero-on-257-mismatch and 258-on-full-success results, threshold cleanup,
FIFO drain, busy status scripts and final registrations. Five model tests pass
on macOS. Incomplete or unused hardware scripts fail rather than being treated
as successful execution. These model tests do not yet compare decoded C with
stock; that target interpreter and helper composition remain required.

Decoded stock and candidate now pass 944 cases against that independent model,
including exhaustive mismatch points 2–257 for each FIFO threshold probe,
preconfigured depths, complete successful probing, FIFO drain and busy delays.
Every modeled transaction must occur in order with the exact address/value;
extra or missing transactions fail. Helper calls clobber caller-saved registers
and the fixed 12-byte frame must preserve the ABI. Helpers are not permitted
to mutate state in this initial model. Mutation tests and reviewed evidence
pinning remain required before admission.

The candidate is now qualified and registered for integration. Eleven focused
model/target tests pass, including mutations of callback/IRQ addresses,
threshold reset, probe bound and busy waiting. The reviewed report pins the
verifier, model, builder and attribution-script hashes; the 944 decoded cases
pass after pinning. Full integration and package verification are pending.
Hardware and helper-composition limitations above still apply.
