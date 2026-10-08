# Selected saturated-scan software composition

Independent source ../../components/touch/saturated_scan_offline/scan.c composes the new native frame loader, watchdog/poller and integer maximum helpers. This closes actual selected widgettypes2/6 and mode0 software body7bc0 while keeping mode switch6ac0 as an explicit adapter. Type7 alternate-frame ABI is excluded; no selected factory widget is type7.

It requests transitionmode5; creates six temporarywords `{0,0,0,slot[3]&0xffffbfff,slot[4],slot[5]}` from slot stride28. On transition success it loads/triggersframe, computes software watchdog and polls completion. On zero returnedbudget it ORs status4. It then reads FIFO low16 atHW+3200 and disablesHWCTL bit31 REGARDLESS of transitionfailure/timeout. Corrected saturated maximum is always written, with outputmin1/max65535 and unsigned correction behavior described in the max-raw batch. Caller must inspectstatus; a nonzero count does not establish successful acquisition.

96 full-body original/native comparisons span state-switchstatus0/1/4/8, FIFO0/1/100/65535, immediate/delayed/timed-out synthetic completion and types2/6. Actual original9178/6928/7288/6980/arithmetic execute on the stock side; independently compiled versions on the native side. MMIO read/write sequence and values, output and status match. ONLY mode-switch6ac0 is explicitly stubbed with identicalreturnstatus; FIFO/interrupts are synthetic. Native module has no retained firmware calls. Physical acquisition, whole-mode lifecycle, interrupt concurrency and board response remain unverified.

Reusable interface uses a functionpointer for mode transition, making the unreconstructed dependency visible rather than silently replacing it with success. Further actionable static work:mode switch6ac0 and its current-mode guards/GPIO/clock/frame dependencies; initialization that sets max-count requeststatusbit8. No external input is needed for those software leads. Hardware trace or validated MSCLP model is required to establish actual FIFOresponse and physical timing, not to continue static reconstruction.

No commits, index, production image, shared campaign, checkpoints or device writes.
