# Notification block, wake/timeout, and resumed return

**360 original/source compositions PASS.** The fixture enters the locked
notification wait, preserves the blocked continuation at its yield boundary,
then applies either the recovered UART notifier path or the recovered tick
expiry path and resumes that same continuation. The compiled reconstruction
matches the locked firmware's return value, output value, notification state,
list membership, tick state, critical-section state, and PendSV write for every
case in [results.json](results.json). The exact ELF and inputs are recorded in
[reproduction-receipt.json](reproduction-receipt.json).

This closes the software path from a positive-timeout wait through delayed-list
insertion and back to the caller. A notification removes the task from the
delayed list, makes it ready, preserves the notified value until the resumed
wait consumes it, and applies the requested exit-clear mask. Timeout expiry
makes the task ready and the resumed wait returns failure because no
notification is pending.

The fixture executes the actual yield request on both sides, but it deliberately
stops before exception entry. It then orders the notifier or tick action and
restores the saved wait continuation. Consequently this proves the task/list
and resumed-return semantics for that ordering; it does not fabricate PendSV
delivery, exception stacking, scheduler selection, or real interrupt timing.

The 360 cases cover notifier and timeout outcomes, ticks 1/2/7, priorities
0/3/7, initial notification values 0 and `0x11223344`, entry-clear masks 0 and
`0x00ff0000`, exit-clear masks 0 and `0x0000ffff`, and replace/set-bits notifier
actions. Infinite wait and tick-wrap insertion remain covered by the preceding
block-insertion batch rather than repeated here.
