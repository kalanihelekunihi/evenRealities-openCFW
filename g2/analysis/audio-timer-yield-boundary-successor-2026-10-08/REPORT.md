# Corrected timer daemon yield boundary

**40 PASS original/native comparisons**, reusing the unchanged sealed daemon ELF `6e28bd25c7f6d8123e0a8a1f55fb679a44272c0d14be21808fbf6145d13525f9`. This additive successor preserves [the earlier sealed batch](../audio-timer-daemon-order-closure-2026-10-08/REPORT.md). [Results](results.json), [runner](verify.py).

The earlier pre-due fixture let port-yield0x4420BC write PendSV request and return while NVIC exception delivery was passive. The instruction body returning under that emulator model did not establish a real task handover. Its completed drain/next-iteration observation is superseded by this stronger execution boundary.

New tests stop before the first yield instruction. Eight pre-due queued-command cases retain queue count1 and active-list count1, with no drain reached. Twenty-six due-entry cases stop at actual callback entry, two empty-queue cases stop at restricted-wait entry, and four selected wrap cases reach next iteration without crossing a yield boundary. None supplies callback, blocking or yield success. Scheduler suspension is now read at0x20074A58;0x20074A30 is explicitly labeled task count. The old sealed field mislabeled that address and remains unchanged as history.

These fixtures have modeled task count0/running1 and direct daemon entry. Existing actual constructor evidence sets timer priority54 versus audio47. Existing wake evidence can stop delete before its auxiliary free, and an already-blocked daemon's continuation reaches drain before next expiry selection. Due-before-drain is a conditional control rule, not proof this live scheduling state exists.

[Native wake/provider successor](../audio-timer-wake-provider-closure-2026-10-08/REPORT.md) closes selected executable providers. [Stock callback successor](../audio-watchdog-callback-closure-2026-10-09/REPORT.md) proves the stock callback ignores its argument. Callback pointer/auxiliary lifetime, IRQ delivery and live context return remain unverified; no hardware defect or safe patch is asserted.
