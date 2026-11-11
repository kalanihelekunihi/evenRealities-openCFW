# GPIO lifecycle and command lookup order

The GPIO open/close and command lookup loops now explicitly load the caller
device name before the record name. This extends the previously verified
[configuration/read repair](output-gpio-read-order-review.md) to
`gpio/native_output_gpio_lifecycle.c` and `gpio/native_output_gpio_command.c`.
Raw stock instructions at open `0x54d98`, close `0x54c58` and command `0x54d20`
load the device name into R1 before loading the record name into R0. The old
C argument expression did not enforce that order.

All 690 stock/C comparisons pass. They cover five records and a missing name,
closed/open states, task/direct dispatch modes, enabled/disabled and null
lifecycle callbacks, command values 0/1/2/3, and negative signed values whose
wrapping table addresses remain part of the native behavior. Controlled
callback targets populate those table locations; no new bounds guard is added.

A name mutation at the first record-name load reproduces the old source
mismatch independently for open, close and command. Stock and corrected C
select the original record; old C observes the later name. Checks compare
ordered name reads, strcmp arguments, callback identity/argument and state,
delay handoffs, the full controlled GPIO configuration, return value, R4-R11,
SP, interrupt masks and provider-call alignment. Lifecycle callbacks receive
their native self-address argument where applicable; operation callbacks
receive the selected record. Callbacks and strcmp clobber caller-saved registers.

These probes model strcmp, lifecycle/command callbacks and the delay primitive.
They do not establish physical GPIO behavior, timing, fault/concurrency
coverage or native byte equality. All 562 R1 units compile with zero failures
or duplicate strong symbols; imports remain 211 application / 34 bootloader.
The other 560 units are unchanged, source checks pass, and the source plan
and G2 workflow remain unchanged. Full bindings and regression observations
are in the [machine-readable review](output-gpio-lifecycle-read-order-review.json).
