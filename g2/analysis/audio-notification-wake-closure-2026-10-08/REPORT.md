# Audio waiting notification: delayed/ready ownership and suspended wake path

**864 fresh three-way PASS waiting-state1 comparisons**: actual original/public wrapper and ISR generic-notify kernel versus independent [wake.c](../../components/audio/notification_wake_offline/wake.c)/[ABI](../../components/audio/notification_wake_offline/wake.h). Original context/mask providers remain common peers; no result stubs. Reuses sealed thread-flags wrapper, but adds independent **index0/action0/1 ISR kernel reconstruction**. Other actions/indices, invalid pointers and full kernel are outside this contract.

## Proven ownership transitions

TCB state item+4,event item+18(hex),priority+2C,notification+68,state byte+6C. Two actual provider calls OR flags then query; first sees waiting1, sets received2; second sees2 and does not repeat wake/list operations. Coherent synthetic current and blocked TCBs, delayed list, per-priority ready lists0/1/2 and pending-ready list.

- Scheduler suspended count20074a58=0: removes state item from delayed list, updates highest priority20074a38, links state item in priority ready list2006a49c+priority*20. Event item stays unlinked. Delayed count drops0.
- Suspended count1: state item remains delayed; event item links into pending-ready list20073d24. Neither state removal nor ready insertion is performed yet. **A flag update/received state does not mean the task is already ready.** Scheduler-resume handling is excluded here.
- Higher priority than current task20074a20 sets wake output and pending-yield global20074a44. Actual wrapper requests PendSV. Equal/lower priority does not request it. **No exception delivery/context switching occurs.**

Flags0/400000/800000/C00000, old0/100, blocked/current priorities0/1/2, suspended0/1, PRIMASK0/1, BASEPRI0/10/30. All list/value writes asserted BASEPRI30; caller BASEPRI/PRIMASK restored. Notification bits/state, linked ownership/list counts/current task and scheduler globals compare. Fixtures are synthetic allocated/coherent lists, not actual initialized audio TCBs, timeouts, races or hardware schedule. No TCB/event ownership/free or PCM snapshot transfer occurs.

## Dispatcher address correction and remaining initialization lead

Locked literal **53CEB4 contains20003FBC**, not20073FBC. Dispatcher53C5AC scans eight8-byte rows at **20003FBC**, matching low16-bit message type and nonnull callback. The wrong20073FBC appeared in prior audio reports, including the preceding thread-flags report; those sealed artifacts are preserved. Earlier original-provenance already recorded the correct literal. This is a documentation-address correction, not new initialized-table proof or changed firmware. Exact registered-function literal screen is in dispatcher-static-xrefs.json; it finds this consumer reference only. Base-relative/indirect initialization is outside that screen.

Authenticated initialized table contents/producer store or decoded startup-data mapping to this address are still needed to establish that type2 maps to53C6F2 in a booted system. No initializer or live-RAM evidence was invented. The image's startup data remains an actionable static analysis lead; missing runtime initialization/task traces restrict behavioral claims, not all source work.

Build/run build_offline.py/verify.py with ArmGNU13.3/opencfw venv. Public body is regenerated from preserved official source/receipt, not a transient previous ELF or generator run. Cortex-M4-compatible code from M55 image; no vector/hardware claim. All872 prior seals,110 audit inputs and4 checkpoints preserved; no commits,index,production/device writes. Next bounded source work: pending-ready resume, actual notification wait/timeout or decoded table initializer.
