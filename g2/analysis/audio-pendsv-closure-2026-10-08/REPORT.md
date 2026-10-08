# PendSV context save, actual task selection and restore prefix

**32 PASS original/independent functional comparisons**, including integer and FP-register context branches. [Independent C model](../../components/audio/pendsv_offline/context.c), [results](results.json), [instructions](original-disassembly.txt), [provenance](provenance.json). This is a context model, not a deployable interrupt handler.

Locked vector word at `0x438038` points to Thumb `0x5FA0C9`. Original handler reads PSP; when EXC_RETURN bit4 is clear, it pushes S16..S31 first. It then stores a ten-word frame `{PSPLIM, EXC_RETURN, R4..R11}` below that optional FP region and publishes its address to current TCB+0. It sets BASEPRI0x30, executes DSB/ISB, calls actual selector **`0x4551B4`**, clears BASEPRI, reads the selected TCB frame, restores the ten words, optionally restores S16..S31, writes PSPLIM/PSP, and reaches **`BX EXC_RETURN` at0x5FA11E**.

**Tests stop before that BX instruction.** No exception return or hardware unstacking is substituted with success. Exception entry, hardware-saved R0..R3/R12/LR/PC/xPSR and low FP registers/lazy stacking are not modeled. No firmware instruction is skipped or modified and no called function is stubbed.

## Actual ready selector

When scheduler-suspension count `0x20074A58` is nonzero, selector sets yield-pending `0x20074A44` and retains current TCB. Otherwise it clears pending-yield, checks four A5A5A5A5 words at the outgoing task's stack base (TCB+0x30), logs outgoing TCB+0x58 into a64-entry pair history ring (`0x2006F348`, index `0x20074A5C`), scans down from highest priority `0x20074A38`, advances that ready list's index past the sentinel, and publishes its owner as current TCB. It records incoming TCB+0x58, increments/wraps ring index, and returns. Stack-overflow hook `0x46D86C` and no-ready-task assertion are outside the independent model's valid-fixture contract.

Original selector executes completely with valid synthetic canaries and two coherent ready tasks at priorities1/2. Independent C implements ready selection/history and frame storage, rather than calling the original selector. Cases vary suspended0/1, history index0/63, initial PSPLIM0/stack base, PSP alignment offset0/8, and integer/FP frames. They compare saved context, TCBs, ready-list index, scheduler globals, complete history ring and restored register values. Original BASEPRI ends0; PSPLIM is read back by explicit architectural fixture helper.

## Architecture and limits

Unicorn uses **Cortex-M33 ARMv8-M profile** for the selected M55-compatible context instructions; this supports PSPLIM and conditional FP stores/loads. It is not an emulated M55 hardware platform. Fixture seeding/readback executes its own MSR/MRS PSPLIM instructions outside the firmware path. FP register raw bits are initialized via emulator registers with CPACR enabled in synthetic SCB; no FP arithmetic, DMA, IRQ delivery or asynchronous producers are tested.

This proves the selected software can save, select and restore these constructed contexts through the final exception-return boundary. It does not establish live scheduling, timeout expiration, timer-daemon command-vs-expiry interleaving, hardware shutdown completion or safe lifetime reachability. Original-instruction support was sufficient here; an unsupported-instruction blocker was not assumed.
