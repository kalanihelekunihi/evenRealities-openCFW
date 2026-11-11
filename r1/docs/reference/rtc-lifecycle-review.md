# R1 RTC open, driver bridges and registration

The existing C lifecycle and driver-bridge units now participate in relocatable
composition. All 171 stock-versus-source open/registration comparisons pass.
The actual C driver bridges execute before the mocked Nordic API boundaries,
checking the instance descriptor, eight configuration bytes, callback binding,
provider order, record state and return status.

Open returns 17 on name mismatch and zero without initializing an already
opened record. First open supplies prescaler 4095, IRQ priority 6 and tick
latency 65. A nonzero initialization status calls the returning error logger;
tick enable, peripheral enable and the opened flag still follow. Tests cover
three name-comparison results, opened values 0/1/255, success/error/negative
initializer words, opened-byte mutation during comparison and initialization,
and registry results. The nine operation-table roles also match native
registration. No physical peripheral access or interrupt delivery occurs.

The excluded RTC-specific error logger duplicated the existing common
`r1_adc_error` body. All 1,536 two-candidate comparisons pass across live
three-read mode sequences and error words. They check short-circuit mode
reads, marker values, descriptor/format identity, string contents and logger
arguments. The RTC copy and its unused private strings were removed; open
now calls the existing common returning logger directly. No forwarding body
or linker alias was added. All allocated lifecycle/driver sections remain
unchanged; normalized relocations differ only at that error target.

REA observes the complete 118-byte open body at `0x56318..0x5638D` and the
46-byte registrar at `0x563C4..0x563F1`, inclusive. The historical 44-byte
registration extent omits its two-byte return. Canonical ledgers and accepted
coverage were not changed.

The complete build compiles 561 R1 units (487 application, 74 bootloader), one
fewer after deleting the duplicate. Both compositions pass with no duplicate
strong symbols and unchanged imports: 238 application, 34 bootloader. Together
with the earlier calendar/tick, epoch and device reviews, this checks the
recovered C lifecycle at controlled provider boundaries. Nordic register-level
execution, full startup, hardware IRQs, clock drift, private stack/fault state,
exact instruction identity and source qualification remain open. No workflow
gate or source-plan entry changed.

[rtc-lifecycle-review.json](rtc-lifecycle-review.json) binds the report,
source/object comparison, duplicate logger comparison and REA observations.
Probes remain under ignored `build/goal-r1-rtc-lifecycle/`.
