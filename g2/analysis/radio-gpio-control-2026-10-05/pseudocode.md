# Full GPIO interrupt control and radio integration

This is readable reconstruction, not decompiler output. Exact immutable body identities and static disassembly are in original/. The compiled HAL function/helper texts are unchanged pinned public SDK excerpts.

```c
uint32_t interrupt_control(uint32_t raw_channel, uint32_t raw_control, void *input) {
    uint8_t channel = raw_channel, control = raw_control;
    if (!input || control > 3) return 6;
    if (control < 2) {
        uint32_t pin = *(uint32_t *)input;
        if (pin >= 224) return 5;
        bank = pin / 32; bit = 1u << (pin & 31);
        address = 0x40010530 + bank*16 + (channel == 1 ? 0x70 : 0);
    }
    prior = save_and_mask_primask();
    if (control < 2) {
        modify_enable_word(address, bit, control == 1);
        if (channel == 2) modify_enable_word(address + 0x70, bit, control == 1);
    } else {
        if (channel != 1)
            for (bank=0; bank<7; ++bank)
                modify_enable_word(0x40010530 + bank*16,
                                   live_volatile_word(input, bank), control == 3);
        if (channel != 0)
            for (bank=0; bank<7; ++bank)
                modify_enable_word(0x400105a0 + bank*16,
                                   live_volatile_word(input, bank), control == 3);
    }
    restore_primask(prior);
    return 0;
}
// modify_enable_word always reads the old word then writes old|mask or old&~mask.

uint32_t radio_irq_enable(void)  { uint32_t pin=117; interrupt_control(0,1,&pin); return pin; }
uint32_t radio_irq_disable(void) { uint32_t pin=117; interrupt_control(0,0,&pin); return pin; }
void radio_pin136_command(uint32_t raw) {
    gpio_state_write(136, (uint8_t)raw ? 1 : 0);
}
// Exact contiguous GPIO-only shutdown slice4b49d8..4b49e6:
void radio_gpio_shutdown_phase(void) {
    radio_irq_disable();
    radio_pin136_command(0);
    radio_idle_pins(); // clear93 then configure138/raw3; prior batch implementation
}
```

## Interfaces, masks and lifetime

Individual input is one readable aligned32-bit logical pin. Mask input is seven readable aligned volatile32-bit words,28 bytes total. The API checks only nullness, control value and individual pin bounds; it does not validate pointer mapping/alignment or channel range. Callers supply valid storage that remains alive through the synchronous call. No allocation, asynchronous retention or ownership transfer occurs.

Both-channel mask control reads the caller's seven words twice, once per channel, rather than taking a28-byte snapshot. Tests observe every external input read and preserve input bytes/guards. They use stable, nonaliasing RAM; mutation, aliasing with the destination registers and asynchronous faults remain outside the fixture. Local pin117 in the two radio wrappers is borrowed only while HAL executes, so its stack lifetime covers the call.

The raw adapter explicitly truncates both enum arguments to bytes before entering the public C API. Shared channel type is the existing header's enum; normal callers use0/1/2. Invalid channel bytes have asymmetric stock behavior: individual control targets only channel0 unless channel==1 or2; mask control targets both channels whenever channel is neither0 nor1. Invalid controls return6 before input is dereferenced; null input returns6 even with an invalid pin. Valid individual pins are0–223; invalid pins return5 without changing PRIMASK or MMIO.

Every accepted operation executes saved PRIMASK masking, ordered enable-register read/modify/write, then restores the incoming mask. Both-channel individual control writes channel0 then1; both-channel mask control writes all seven channel0 banks before all seven channel1 banks. Pin117 is channel0 bank3, EN address0x40010560, bit21. Disabling this bit does not clear latched status, remove registered callbacks, disable NVIC or drain queued scheduler work.

Pin136 control writes bit8 to WTC4 at0x40010468 for byte-zero and WTS4 at0x4001044c for byte-nonzero. The full32-bit value256 therefore clears, while257 sets. This is an output command; electrical signal role/readiness is not established.

## Caller and hardware boundary

The tested shutdown slice begins after WsfTimerStop and ends before caller globals are cleared and transport handle release0x52df12 executes. Every callee in the slice runs actual source/original instructions without an executable stub. This does not make the whole HciDrvRadioShutdown source-complete or prove safe shutdown. Transport release depends on instance validation, IRQ-control, subordinate HAL disable/power/uninitialize and state flags. Boot0x4b48a6 also depends on open/configure/enable, controller protocol/setup and DMA/transport functions; those are separate source prerequisites.

Six immutable control-body bytes cannot execute with validated inputs:4 bytes4810ee..4810f2 handle a failed pin-index helper that always returns0, and2 bytes481126..481128 are the default switch jump after validation restricts control to0..3. They remain statically accounted for and receive no execution credit. No fault, trap or altered original code is used to manufacture coverage.

The two pin117 wrappers return the literal117 restored from their stack-local argument, not the HAL status. Observed boot/shutdown callers ignore it. Source preserves this exact callable return; pin136 gate and the GPIO-only phase have unspecified void return values.
