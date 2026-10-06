# Local command queue termination and disable/uninitialize

Names `iom`/disable/uninitialize are behavioral inference; consolidated stock symbol attribution remains unverified. Addresses, fields, bytes and behaviors below are authenticated/compared directly. New interfaces: `opencfw_iom_cq_term`, `opencfw_iom_disable`, `opencfw_iom_uninitialize` in `g2/components/foundation/radio_iom_release/iom_release.h`.

```c
uint32_t local_cq_term(void *h) { //0x55c11a,32B; mapped h required
    if (*(u32 *)(h+0x828)) {
        am_hal_cmdq_term(*(void **)(h+0x828), true); // status ignored
        *(u32 *)(h+0x828) = 0;
    }
    return 0;
}
uint32_t disable(void *h) { //0x55c430,104B
    if (!h || (h->prefix & 0x01ffffff) != 0x01123456) return 2;
    if (!(h->prefix & 0x02000000)) return 0;
    if (*(u32 *)(h+0x24)) return 3;
    reg = 0x40050000 + (h->module << 12) + 0x11c;
    *reg &= ~1; *reg &= ~0x10; // separate ordered RMWs; module reread
    local_cq_term(h);
    h->prefix &= ~0x02000000;
    return 0;
}
uint32_t uninitialize(void *h) { //0x55c286,54B
    if (!valid(h)) return 2;
    if (h->prefix & 0x02000000) disable(h); // status ignored
    h->prefix &= ~0x01000000;
    return 0;
}
```

The queue slot is caller-local, unlike the existing MSPI termination wrapper's global module slot. Reusing that MSPI wrapper would change ownership. This implementation instead reuses unchanged `am_hal_cmdq_term` and its existing index/PRIMASK provider. No duplicated CQ function, synthetic delay or executable stub.

| Object | What this chain does | What remains |
|---|---|---|
| Caller queue slot@0x828 | Nonzero slot invokes forced termination, then slot cleared even if CQ validation returned2 | No freed allocation or alternate owner established |
| CQ object | Valid term updates index/head, clears init bit24, disables CQ bit0 and clears configured pause-mask bits | Buffer bounds/tail/size/raw sequence retained; enable bit25 retained |
| CQ command buffer | Sentinel contents unchanged; no dereference/free in tested chain | Actual transactions, queued callbacks and DMA access not drained/proven |
| Caller prefix | Successful disable clears enable25; uninit clears init24 even if disable returnedbusy3 | Busy uninit can leave enable25 set while init24 isclear; no module reset |
| Callback/task objects | No invocation or access in this chain | Scheduled work and object ownership elsewhere unchanged/unknown |
| Interrupts | PRIMASK saved/restored only around index/head update | Outer register/prefix/slot mutations not atomic; no NVIC/pendingIRQ clear |

Forced termination skips the queue-empty rejection; it is not a completion wait. Pending word@0x24 blocks disable before MMIO, but private local termination itself does not check that word. The surrounding release0x52df12 ignores disable/power/uninitialize statuses and clears its tracking bytes; that wrapper is still static call-chain evidence, not a tested full release.

One exact limitation: on index wrap, stock writes intermediate curIdx then final corrected curIdx under PRIMASK1; current unchanged O2 provider writes final only. The verifier independently checks each exact raw sequence, saves both, and canonicalizes only that contiguous curIdx sequence for final call-contract comparison. Other RAM writes, ordered MMIO, masks, full final objects and guards remain strict. No internal RAM-store identity or equivalence for DMA/NMI/other asynchronous observers is claimed.

Tests cover null/invalid/disabled/enabled/busy prefixes, null and invalid queue, forced nonempty queue, wrap/high hardware index, modules0/1/7, masks0/1 and pause-mask variants. Module validity is not checked by these bodies; tests use only mapped register banks and do not approve physical module7.

Next power path: caller passes handle, operation2, retain1 to0x55c7e8. Its powerdown branch0x55c946 tests enable/pending and hardware status@0x248, snapshots registers into fields0x86c..0x89c, conditionally invokes CQ disable0x538e8c via0x55c168, then calls0x47f7ae and0x4c4530. Those power-control bodies and hardware transitions are outside this batch; their available instructions can be analyzed next. No external blocker to that offline analysis is claimed.
