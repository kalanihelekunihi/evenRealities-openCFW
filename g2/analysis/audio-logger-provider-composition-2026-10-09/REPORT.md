# Logger startup and trace-provider composition

**New facts:** the logger callback and disable flag start at zero in the first startup zero-fill range. The disable children operate on ITM control and a trace reference counter. They do not establish a UART or BLE sink.

The locked main image's scatter loader0x5E42B4 uses table0x75D3C8. Its first handler resolves to0x5FA01E and zeroes **461,552 bytes** in `[0x20004558,0x20075048)`. Original instruction execution over an A5-prefilled synthetic mapping confirms the entire span is zero, including callback0x200742F0 and flag0x20074F4E. The next range and later decompression are not executed. This strengthens the initial-state conclusion without claiming complete startup.

**24 provider-composition cases PASS**, replacing the preceding batch's direct stubs at0x539254 and0x539304 with original bodies, including original0x53928C,0x5392F8,0x5392D4,0x5392AE and interrupt helper0x473940. Stock0x539254 clears SWOENA(bit4) and ITMENA(bit0) at ITM_TCR0xE0000E80. Its idle-helper result is ignored. Stock0x539304 decrements byte0x20074F7E under saved PRIMASK; if nonzero remains, returns3; otherwise clears byte0x20074F7D and releases a shared clock, translating release status3 to zero. Original MSR restores PRIMASK. An outer disable with initial count above1 enters the original fatal loop in these synthetic cases; live reachability is unproven.

Poll0x4807FC, delay0x4807A0, clock release0x4D3F78 and pin configuration0x480F0C remain explicit stubs. No actual trace FIFO drain, clock/pin change, scheduling or hardware behavior is inferred. These25 comparisons are original-provider evidence, not a new compiled source closure. No exact-build receipt is fabricated for this pseudocode-only successor.

## Source provenance and remaining leads

Existing AmbiqSuite3.2.0 `boards/apollo3p_evb/bsp/am_bsp.c` has an ITM printf disable family that calls ITM disable, clears the stdio callback and disconnects SWO. Its enable family installs am_hal_itm_print. This is a useful source-family analogue; its Apollo3 implementation is **not an exact source match** for the recovered main ITM/refcount bodies, and its enable path is not proof that main installs that callback. `mcu/apollo3p/hal/am_hal_itm.c` differs materially in loops/register sequence. Source hashes are recorded separately; no producing SDK version inferred.

A bounded exact-address literal search finds the disable flag only at0x4C306C and the callback at0x4448B8/0x47345C. The current decompiled corpus shows the setter's only caller passing zero. This does not exclude computed addressing, bulk initialization, callbacks, resident code or runtime mutation. A callback installed by the analyzed zero-fill record is ruled out; installation by later code is unresolved. Static searches are not globally exhausted.

Concrete next providers: poll0x4807FC and shared-clock release0x4D3F78 (whose known body manipulates MCU control0x40020250 and byte0x20074F5C), then runtime/constructor writes to the zero-initialized logger globals. Existing delay evidence in ambiq-critical-2026-10-05 should be reused rather than rediscovered. A runtime sink pointer/trace would resolve dynamic binding if static paths remain unclosed; no device activity is authorized or performed here.

Pinned raw SHA25619044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701, wrapped SHA25636c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863, rawload0x438000. Predecessor [formatter report](../audio-main-formatter-source-successor-2026-10-09/REPORT.md) retains exact-build receipt, scalar VFP-profile and synthetic-output-sink boundaries; no modification to it.

[Readable pseudocode](pseudocode.md), [24 composition cases](results.json), [original zero-fill test](initializer-results.json), [preservation](preservation.json).
