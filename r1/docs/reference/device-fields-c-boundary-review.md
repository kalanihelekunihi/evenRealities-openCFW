# R1 device-info fields: retained native frame boundary

A direct C probe for stock `0x73710` was rejected. The production implementation
in `r1/src/application/board/native_kv_device_fields.c` remains unchanged.

REA/Ghidra confirms the native prologue saves 12 bytes and reserves another 52.
At its first cached-read call, the native record is exactly caller SP minus 64.
The probe used empty constraints, fixed live R4/R5, a C reservation and the
existing stack observation helper. Under the normal Clang profile it allocated
72 bytes and passed caller SP minus 72 as the record pointer. An executed
comparison confirmed both frame and record depths, with matching R4 input,
R5 handle-cell address and requested length 52.

That difference matters when cached reads leave bytes untouched or the input
aliases the stack view. Passing arithmetic or fully initialized-record tests
would not establish the required behavior. No full behavior claim was made and
the probe was not added to the source manifest or source plan.

The [receipt](device-fields-c-boundary-review.json) records the production unit,
probe hash, stock evidence and first-call counterexample. Ignored probe inputs
and the executable check are under `build/goal-r1-device-fields-c/`.
The next C attempt must preserve the native record position and then validate
failed/partial reads and input aliases before replacing the existing wrapper.
