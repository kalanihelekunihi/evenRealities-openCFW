# UART power and configuration — reconstructed behavior

Stock: power0x58DBB8, configure0x58E09E, baud helper0x58DE38, interrupt clear0x58E7E4. Module at handle+40; reported baud+48; clock ID byte+280. Saved validity byte+4; eight saved words+8..36. Config16B: baud0; data/parity/stop bytes4/5/6; flow uint16+8; TX/RX threshold bytes10/11; clock byte12.

```c
power(handle, request, retain) {
    validate_handle();
    if (request == WAKE) {
        if (retain && !saved.valid) return 7;
        enable_peripheral(11 + module); // return ignored
        if (retain) {
            if (reported_baud > 1500000 && revision > 0x21)
                D2ASPARE |= 0x400000 << module;
            request_clock(clock_id, 11 + module); // return ignored
            restore(ILPR, IBRD, FBRD, LCRH, CR, IFLS, IER, DCR);
            saved.valid = false;
        }
    } else if (request == NORMAL_SLEEP || request == DEEP_SLEEP) {
        if (retain) { save_same_eight_registers(); saved.valid = true; }
        if (reported_baud > 1500000 && revision > 0x21)
            D2ASPARE &= ~(0x400000 << module);
        release_clock(clock_id, 11 + module); // return ignored
        clear_interrupts(0xffffffff);
        CR = 0;
        disable_peripheral(11 + module); // return ignored
    } else return 6;
    return 0;
}
configure(handle, cfg) {
    validate_handle(); CR = 0; CR.CLKEN = 1;
    if (cfg.clock > 1 || (cfg.clock == 1 && revision == 0x21)) return 6;
    clock_id = cfg.clock == 0 ? 4 : 6;
    bool high = cfg.baud > 1500000;
    if (revision > 0x21) update_gate(high);
    CR.CLKSEL = clock_id == 6 ? 6 : (high ? 5 : 1);
    request_clock(clock_id, 11 + module); // return ignored
    clear_UART_RX_TX_enable();
    status = baud_helper(module, cfg.baud, &reported_baud);
    if (status) return status; // no clock rollback in this body
    apply_flow_parity_data_stop_fifo_thresholds();
    enable_UART_RX_TX(); return 0;
}
baud_helper(module, desired, actual) {
    freq = {1:24000000,2:12000000,3:6000000,4:3000000,
            5:48000000,6:49152000}[CR.CLKSEL];
    if (clock_invalid) { *actual=0; return 0x8000002; }
    divisor = 16 * desired; // uint32; zero/overflow cases unvalidated
    integer = freq / divisor;
    fraction = ((uint64_t)freq * 64) / divisor - integer * 64;
    if (!integer) { *actual=0; return 0x8000003; }
    IBRD=integer; FBRD=fraction;
    *actual = freq / (16*integer + fraction/4); return 0;
}
```

Reported baud is integer-quantized software metadata, not measured waveform. HFRC request921600 reports923076; request1500001 selects48MHz and reports1548387. Power gate decisions later use this reported value.

Stock interrupt-clear validates first, writes IEC+0x44 and returns. Pinned source loads module before validation and adds volatile MIS+0x40 read. Valid mapped-handle fixtures agree in return/state but do not establish matching MMIO read side effects; NULL source call is excluded. Do not use selected source as a full behavioral replacement for this function.
