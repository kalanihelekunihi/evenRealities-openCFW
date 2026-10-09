# Remaining finite source-backed boundary

The54entrycensus now has39independently reviewed extents/2,912bytes and seven
new exact selected candidates/1,036bytes awaiting review. Eight entries remain
unmatched against the current pinned public source and unchanged comparator
flags. This is not whole-project or all-public-source exhaustion.

`compare_residuals.py` records the eight raw stock/object windows and every non-relocated
mismatch. Compiled-length windows are explicitly not promoted to firmware
function extents. Relocation fields are excluded only for diagnosis, never
patched into results or executable code.

## Concrete source questions for the discovery track

1. **Flash producing source/version:** ClockBackup, ClockConfig and ClockRestore
   contain an extra stock `c046` NOP immediately before their SROM-status call.
   Current public source does not emit it, and current ProcessStatusCode emits
   128bytes against the58bytehistorical body at `0x8BF4`. WriteRow also differs
   at171non-relocated positions. Find authenticated public source history or
   build-contract evidence explaining the NOP/status-call implementation, not
   a hand-inserted NOP, replacement stub or arbitrary compiler sweep.
2. **ILO variable-section build contract:** Stock start/stop load two distinct
   byte-variable literal addresses (`0x20000F1D` guard, `0x20000F1E` measurement
   flag), each through byte offset0. The current object addresses one `.bss`
   section and uses nonzero byte offsets. Compensation has the analogous three
   non-relocated byte-offset differences plus relocated globals/calls. This
   suggests a per-variable section/layout compilation contract; it does not
   prove a particular flag. Obtain authentic producing/public build recipe
   evidence for data-section emission before treating a new flag as stock.
3. **PM callback source/lowering:** ExecuteCallback still differs at69
   non-relocated bytes after original-address linking; its registration and
   outer sleep wrappers match. Determine whether an authentic source revision
   or independently supported variable-section/lowering configuration explains
   callback-global access and the control-flow differences. Retain the mismatch
   rather than infer matching sleep semantics from matching wrappers.

The exact producing checkout and compiler/linker configuration remain unknown.
Those are the next inputs for this finite branch. No missing hardware trace is
needed merely to investigate static bytes; hardware observations are still
needed for physical clock/power/bus claims. The compiler division body is a
separate explicitly unimplemented external binding in the clock comparator.

All original source, symbol names, raw failures and historical receipts remain
available. No source/flag fitting, production changes, Git mutations, shared
campaign changes or device writes were performed.
