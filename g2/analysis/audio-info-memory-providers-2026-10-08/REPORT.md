# INFO1 cache, memory configuration and oscillator providers

Four complete native offline helpers pass **1,182 comparisons against the same final rebuilt ELF**:96 INFO1,664 memory,38 composed initializer,384 oscillator. [Exact build validation](exact-build-validation.json), [C and interfaces](../../components/audio/info_memory_offline/), [addresses and byte hashes](function-bindings.json), [instruction evidence](disassembly-evidence.txt). ELF SHA256 `4a81046ae3ddb64e443d3e9c6ab9c71bdad34fa09ed6a49ae76ecd47d97a89cc`.

## INFO1 cache and caller errors

Population0x47F954 requires OTP selection (SHADOWVALID bit3) and OTP power (DEVPWRSTATUS bit27), otherwise returns7. It performs nine actual original reader transactions: MRAM SBL versions; main/OTA pointers; eight OTP SOC ID words; patch tracker; temperature, ADC and audio ADC calibration; factory date. [Typed 128-byte layout](../../components/audio/info_memory_offline/info.h) at0x20071948 exposes the cache.

It writes fields as reads succeed, stops on first error, and installs0x1F01600D only on complete success. Failure does not clear an existing signature or roll back fields. The initializer discards the population status. In composed fixtures with selected read2/5/9 made unavailable, old valid signature permits continuation and status0; without it fallback reading returns9. This is synthetic OTP unavailability, not a measured device fault. First MRAM-read failure is reconstructed statically, not artificially injected.

## Memory side effects and discarded errors

MCU0x47F204 config is five bytes:ROM mode, active DTCM, retained DTCM, active NVM, retain NVM. It updates cached ROM mode before validation, disables unneeded memories, waits, calls actual power dispatcher, enables requested memories, waits again and checks status consistency. Stock discards dispatcher errors, unlike the pinned SDK. First wait failure can leave FORCEAXICLKEN bit0 set; second wait failure clears it before returning. Invalid retained-DTCM enum returns5 after earlier register changes.

SRAM0x47F46A config is five bytes:active, with MCU, with GPU, with display, retain. Raising invokes dispatcher before memory change; lowering after successful change. Both dispatcher returns are ignored. Active field is masked to3 bits for the write but the comparison uses the raw byte. Retention0/1/3/7 maps to low field7/6/4/0; other retention values leave that field unchanged. Status response is synthetic; no executing-memory placement or physical power safety is established.

## Oscillator control and ownership boundary

Controller0x4809C4 byte-narrows action and handles0..6. NULL/non1 boolean selects internal rather than external reference. Capacitance fields come from cached bytes/words. Normal32M action3 overwrites the trim with computed caps/defaults, dropping old masked bits unlike the public SDK. Kick uses actual delay API; no physical startup timing is proved.

Clock-output enable action5 first requests **clock2/user52** through actual clock manager0x4C44BC, propagates error, then validates drive0 or3..7 (NULL defaults4). Thus invalid drive can return6 after successful request, with no balancing release in this function. Action6 changes trim/control then calls actual release0x4C4530 and returns its status. This batch does not yet establish cached user-bit persistence or a naturally occurring hardware leak: the manager is the next source-backed lead. Retained reset flags and cached manager ownership are separate state.

## Validation and remaining dependencies

All original wait, dispatcher, INFO reader, delay and clock-manager providers execute without successful/error-return stubs. Manager internals can reenter original oscillator code. MMIO readiness, calibration words and availability changes are synthetic; provider execution does not establish physical readiness. This is an offline reconstruction/helper batch, not a full native firmware image or byte equality claim. Resident ROM, full M55/IRQ/scheduler behavior and physical calibration remain external boundaries.

Prior seals,110 audit inputs,four checkpoints and the current index match [preservation](preservation.json). Historical index change was concurrent committed/staged work and was not undone. No commit, production edit or device write was performed.
