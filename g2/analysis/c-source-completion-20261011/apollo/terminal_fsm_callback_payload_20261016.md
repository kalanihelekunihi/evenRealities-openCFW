# Terminal FSM callback payload ABI: stock Apollo Main

Pinned payload: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` after the 32-byte package header, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

The stock dispatcher `0x5e7b74` accepts the event in R0, and the direct, logging-disabled action path reaches:

```asm
005e7c1a  ldr      r2, [pc, #0x264]     ; table base
005e7c1c  ldrb.w  r3, [r6, #0x275]    ; state
005e7c2a  movs     r2, r5              ; event
005e7c2c  uxtb     r2, r2
005e7c2e  add.w    r8, r0, r2, lsl #3 ; table cell
005e7cb6  ldrb.w  r7, [r6, #0x275]
005e7cba  ldrb.w  r0, [r6, #0x275]    ; old state
005e7cbe  ldr.w    r2, [r8, #4]       ; callback
005e7cc2  blx      r2                 ; R1 is not assigned here
```

The callback at `0x5e6400` reads R1 as a packed parameter, passing `R1 & 0xf` and `R1 >> 4` to `0x5e4a6e`. The callback at `0x5e6410` passes R1 to `0x5e48b8`. The callback at `0x5e68b4` tests R1 against 1. These are evidence that the callback contract is at least `(old_state, event_payload)` on the direct path, although the current C table and dispatcher declare only `(old_state)`. The dispatcher also contains logging branches before `blx`; any claim that R1 is preserved there needs a separate trace.

**Open source gate:** correct the C dispatcher/table callback type to carry an explicit second argument and verify it against stock with varied R1 inputs before binding the payload-consuming callbacks. Audit receipts for the existing dispatcher/table must then be regenerated. Do not infer the payload value from the event number or old state.
