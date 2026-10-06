# DMA rearm pseudocode and interfaces

The compiled implementation is instruction reconstruction in `rearm.c`, not a copied SDK body. First-party pinned upstream supports register names and two-stage branch interpretation; stock bytes independently govern this implementation.

```c
// Full stock 0x5908a0; mapped handle/peripheral required, no lock or validation.
u32 service(h, captured_status) {
    m = h.module;
    if (TXDMASTAT(m) & ERR) dma_error(h, TX); // DMACFG=0, TXSTAT=0
    if (RXDMASTAT(m) & ERR) dma_error(h, RX); // DMACFG=0, RXSTAT=0
    if ((captured_status & RX_COMPLETE) && h.rx_pong != UINT32_MAX) {
        RXDMASTAT(m) &= ~COMPLETE;
        if (DMAENNEXTCTRL(m) & RX_NEXT_ENABLED) return 9;
        h.rx_selected = h.rx_selected == h.rx_pong ? h.rx_ping : h.rx_pong;
        RXDMAADDRNEXT(m) = h.rx_selected;
        RXDMATOTCNTNEXT(m) = h.rx_bytes >> 2;
        DMAENNEXTCTRL(m) |= RX_NEXT_ENABLED;
    }
    if ((captured_status & TX_COMPLETE) && h.tx_pong != UINT32_MAX) {
        TXDMASTAT(m) &= ~COMPLETE;
        if (DMAENNEXTCTRL(m) & TX_NEXT_ENABLED) return 9;
        h.tx_selected = h.tx_selected == h.tx_pong ? h.tx_ping : h.tx_pong;
        TXDMAADDRNEXT(m) = h.tx_selected;
        TXDMATOTCNTNEXT(m) = h.tx_bytes >> 2;
        DMAENNEXTCTRL(m) |= TX_NEXT_ENABLED;
    }
    if (captured_status & IPB) ipb_service(h);
    return 0;
}
// Original ISR 0x57a4d8, full notification remains outside this batch.
isr() {
    captured = interrupt_status(global_handle, enabled_only=true);
    interrupt_clear(global_handle, captured); // INTCLR=mask then read INTSTAT
    service(global_handle, captured); // returned9 deliberately ignored in stock
    if (captured & RX_COMPLETE) notify_0x53c6b2();
}
```

`opencfw_audio_i2s_irq_prefix()` is a new bounded source seam: executes status/clear/service and returns captured status. Bit4 means the stock caller would enter the actual notifier. It does not submit a queue message, implement a full ISR, or consume/free any buffer. Notify-present original execution stops at0x53c6b2 with a live ISR frame; returning ABI is checked only on actual returning paths. The source tests append a boundary observation from the seam result, not a fabricated notifier implementation.

| Register offset | Pinned header field | Stock action |
| --- | --- | --- |
| +0x200 | DMACFG | error helper writes0, without restarting it |
| +0x20c / +0x218 | RXDMASTAT / TXDMASTAT | error bit2, completion bit 1 |
| +0x21c | DMAENNEXTCTRL | RX-next bit0, TX-next bit 1; preserve other bits |
| +0x220 / +0x224 | RXDMATOTCNTNEXT / RXDMAADDRNEXT | word count then address fields; stock programs address before count |
| +0x228 / +0x22c | TXDMATOTCNTNEXT / TXDMAADDRNEXT | corresponding TX staging |
| +0x4c | IPBIRPT | snapshot branch tests bits19,17,18,16; fresh ordered RMW per selected bit |
| +0x300 / +0x304 / +0x308 | INTEN / INTSTAT / INTCLR | enabled status capture, clear, readback |

Base is0x40208000 + module*0x1000. Both instances0/1 are exercised. Handle RX ping/pong/selected/bytes are+0x3c/+0x40/+0x4c/+0x54; TX are+0x44/+0x48/+0x50/+0x58. Sentinel UINT32_MAX disables alternating rearm for that channel. The query/getter from the previous batch still borrows the selected pointer.

Error-helper direction is truncated to uint8; every direction clears DMACFG, direction 0 clearsRX status,1 clearsTX, others clear neither. Status/clear helpers check the low25 prefix bits against0x01125125 after reading module; malformed mapped magic returns2. Null/unmapped handles cannot be made safe by those checks because original preloads handle+4.
