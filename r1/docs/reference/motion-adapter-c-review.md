# R1 factory motion event adapter in C

`r1/src/application/runtime/native_motion_adapter.c` supplies native callback
`0x6f304` (118 instruction bytes, two padding bytes and one four-byte literal).
REA assembly and byte readback were checked against the locked application.
[The machine-readable review](motion-adapter-c-review.json) retains source/build
hashes, startup proof, passing replay scopes and the rejected stack-identity
check. The candidate does not establish complete stock equivalence.

## Recovered behavior and ownership

The callback ignores its handle and any third stream-length argument. Its gate
is the halfword at input byte 180, not the stream length. With a nonnull input,
nonzero gate and inactive factory mode, it clears a 36-byte local packet, writes
header bytes `00 01 40 04`, copies three axis halfwords to packet offsets four,
six and eight, and calls the legacy sender with length ten. Inputs are read
fresh after the clear provider returns. A clear-provider mutation of active
state does not restart the branch decision.

Otherwise, active mode, nonnull input and a nonzero gate select caching. The
native duplicate active/gate loads are preserved. Each halfword is read and
stored before the next is read, retaining sequential overlapping-input behavior.
Zero input/gate suppresses both paths. No new length check or pointer guard is
introduced.

The existing `r1_factory_mode_state` owns the active byte at `0x20006c34`. Only
the six-byte cache at `0x20006c5a` is newly owned as `r1_factory_motion_samples`,
with two-byte alignment. This does not extend the earlier 28-byte state prefix
or claim the ten intervening bytes. Native RW/ZI handlers were executed against
poisoned regions with guards, with an independent RW decoder agreeing. The cache
object matches six native zero bytes. Final placement remains unproven.

## Validation and retained counterexample

The direct fixture passes 2,289 paired native/C cases for ordered non-stack
accesses, state/input/cache slabs, guards, masks, normal-return SP and callee-saved
registers, clear length and all 36 packet bytes observed by the modeled sender.
Cases cover zero/noncanonical active bytes, zero and extreme gate values,
unsigned axis extremes, unaligned and overlapping input/cache addresses, clear
provider mutations and null inputs. Clear and sender are modeled in that set.
The callback's void return leaves R0 caller-clobbered and excluded.

Another 972 paired cases execute the actual native/C stream dispatcher, motion
callback, EABI clear wrapper and memset implementation. Sensor read, list
head/next and sender capture are modeled. The input gate is exercised with both
six-byte and 184-byte stream sample widths. Linked provider hashes are recorded.
The six compiled negative controls reject a wrong gate offset, wrong active
path, wrong packet header, short clear, short reply and wrong cached axis.

**The local packet address differs.** Native clear/send calls use a 48-byte
frame and packet at caller SP minus 48. C uses a 56-byte frame and packet at
caller SP minus 56. The passing byte-contract fixture excludes those packet
addresses from equality and records them separately. A strict pointer/depth
check fails at C clear entry `(56, 56)` against native `(48, 48)`; the rejected
check is retained in `build/goal-r1-motion-adapter-c/frame-gap.log` and the JSON
review. Source/optimization probes did not close that gap and remain under the
ignored build directory.

Through the dispatcher, packet offsets become 88 native versus 104 C bytes,
including the dispatcher's prior frame gap. No equality is claimed for a sender
that inspects the absolute pointer, aliases caller stack storage or retains the
packet asynchronously. The transport has not been integrated or physically
validated. Private stack contents, caller-clobbered registers and APSR are also
excluded. These are explicit limits of this behavior candidate, not a full ABI,
stack or byte-identity result.

## Build status and next dependencies

`make sources-check` passes. All 615 units compile (541 application, 74 bootloader),
and both relocatable compositions pass without failures or duplicate strong
symbols. All preceding 614 objects remain identical. Only the adapter unit is
added to the manifest and only its existing frontier row changes. Its import
resolves and `r1_legacy_bounded_reply_send` becomes explicit, leaving 168
application and 34 bootloader imports. The legacy wrapper at `0x8967c` forwards
the packet to the type-two transmit dispatcher when a valid glasses connection
exists; that integration remains unfinished.

Scoped qualification compiles the unit but admits zero bytes. The canonical
source plan is unchanged. A fresh hybrid matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
with 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. A complete source-only build, candidate byte identity and real
motion delivery remain incomplete.

Reports: `build/sources-goal-r1-motion-adapter-c/report.json` and
`build/hybrid-goal-r1-motion-adapter-c/build-report.json`. Experiments, rejected
frame checks and fixtures remain under `build/goal-r1-motion-adapter-c/`;
durable receipts are in the JSON review above.
