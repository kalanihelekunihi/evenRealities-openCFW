# GPIO state write and radio consumer reconstruction

Addresses refer to Apollo payload loaded at0x438000, with the32-byte OTA header excluded. Artifact and exact body hashes are in original/evidence.json. Pseudocode below is reconstruction; gpio_state.c retains the pinned public SDK function text and dispatch macros unchanged.

```c
// Stock0x480fd6,218 bytes. Return is success even for unknown operation.
uint32_t gpio_state_write(uint32_t pin, uint32_t raw_operation) {
    uint8_t operation = raw_operation;
    unsigned bank = (pin >> 5) & 7;
    uint32_t mask = 1u << (pin & 31);
    switch (operation) {
    case 0: WTC[bank] = mask; break;
    case 1: WTS[bank] = mask; break;
    case 2: {
        uint32_t prior = save_and_mask_primask();
        WT[bank] = WT[bank] ^ mask;
        restore_primask(prior); break;
    }
    case 3: ENC[bank] = mask; break;
    case 4: ENS[bank] = mask; break;
    case 5: {
        uint32_t prior = save_and_mask_primask();
        EN[bank] = EN[bank] ^ mask;
        restore_primask(prior); break;
    }
    default: break;
    }
    return 0;
}

// Stock0x52dd7c,24 bytes, called by shutdown-associated0x4b49ce.
// void return: do not interpret its incidental R0 as status.
void radio_idle_pins(void) {
    gpio_state_write(93, 0); // status ignored; WTC2 clear command
    gpio_pinconfig(138, load_word(0x78ee48)); // raw3; status ignored
}
```

## Register layout

GPIO base0x40010000; seven32-bit words per family. The primary pinned apollo510.h GPIO type orders RD,WT,WTS,WTC,EN,ENS,ENC. Offsets are RD404,WT420,WTS43c,WTC458,EN474,ENS490,ENC4ac. PINCFG has224words; PADKEY offset400. Pointer-pool values and stock PC-relative loads corroborate this layout.

State-write has no pin-range guard. The bank is only three bits, so logical bank7 aliases the next physical family: WT7→WTS0, WTS7→WTC0, WTC7→EN0, EN7→ENS0, ENS7→ENC0, ENC7→reserved4c8. Pin256 wraps to bank0/bit0. These are address-alias diagnostics, not valid-pin interfaces. Use configuration's validated logical range and independently established physical pin capabilities in applications.

## Ordered radio contract

The clear is a direct write of0x20000000 to0x40010460, with incoming PRIMASK unchanged. Then configuration138 validates raw3 and executes saved-mask critical section: PADKEY0x73, PINCFG138 at0x40010228=3, PADKEY0, restore prior mask. The sequence is not one atomic critical section. Register-model side effects are synthetic; physical output enable, electrical settling and complete shutdown safety are not established.

Injecting rejected configuration0x800 or0xffffffff for pin138 tests failure ordering: the pin93 clear still occurs, the setter returns7 without configuration/key writes, and the void consumer ignores it. Those values are memory perturbations in the test; authenticated stock data contains3. No actual firmware failure is inferred.

## ABI and ownership

Public operation type is a byte, so compiled C callers must supply ABI-valid converted values. opencfw_gpio_state_write_raw explicitly converts arbitrary32-bit operation inputs to model the stock entry's UXTB instruction. Configuration is a four-byte by-value raw word. No buffer allocation, queue transfer or asynchronous memory lifetime exists in this bounded chain. Stack-local config lives through the synchronous setter; the volatile original data word is explicitly loaded in the reconstructed consumer.

## Device fixture limits

Ordered MMIO and PRIMASK are observed from original instructions and source instructions. WTS/WTC effects on WT and ENS/ENC effects on EN are an explicit host device fixture based on register documentation. The fixture supplies an external output-active mask; it does not derive physical output enable from EN alone or from mux/PINCFG state. Command-register readback latches, invalid-bank aliases and injected config failures are synthetic diagnostics. Scheduler, clocks, NVIC, radio state machine and hardware timing remain outside this chain.
