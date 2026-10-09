# Newlib startup and exit provider comparison

Unchanged newlib at pinned Arm release revision
`7923059bff6c120c6fb74b63c7553ea345c0a8f3` was compiled with the previously
justified Cortex-M0+/Thumb/size/nano configuration. Acquisition and consumed
source/generated-header hashes are in results.json. Exact source notices are
retained; COPYING.NEWLIB is preserved in the adjacent memcpy acquisition.

Exit now reproduces **40/40stockbytes at[A9AC,A9D4)** after real GNU linking.
The stock literals bind the undefined weak `__call_exitprocs` to0 and the
stdio-handler slot to`20000F54`; the real BL binds `_exit` to`AA40` (Thumb
symbol`AA41`). GNU ld itself rewrites the undefined weak call to a branch/NOP;
no relocation bytes were patched. `exit-link-results.json` records exact
hashes and command. Historical54byte exit extent overlaps memset and remains
unchanged; this additive40byte result is independent-review pending.

Behavior from source and stock: preserve status, skip absent exit-procedure
provider, invoke nonnull stdio handler, then pass original status to `_exit`.
The halt provider and actual runtime handler contents were not executed or
source-attributed here. No new original-instruction fixture or physical exit
claim is made.

Constructor source emits68bytes and has37non-relocated differing byte positions
against the selected stock window. Stock separately shows `_init` callAA44,
preinit bounds both2000087C and init bounds2000087C..20000880. These are static
array-bound values; contents/live callbacks are not inferred. The unmodified
consumed nano configuration does not emit the `_init` call. This mismatch is
retained, not hidden by adding a source-selection macro. Authentic archive
member/generated build configuration is the next bounded attribution input.

These results do not establish vendor full build reproduction, whole-firmware
source completeness, campaign admission or startup/exit runtime composition.
No Git, production, device or shared campaign-state edits occurred.
