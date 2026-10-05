# Radio GPIO control foundation: full API and integrated shutdown slice

The existing GPIO source module now links the unchanged pinned Ambiq SDK interrupt-control function and pin-index helper with the actual radio pin 117 enable/disable wrappers, pin 136 byte-truth output command and contiguous GPIO-only shutdown caller slice. It extends previously specialized radio control to a reusable full both-channel/mask API. It is a software register contract, not a complete radio startup or safe shutdown implementation.

Source/interfaces are in g2/components/foundation/ambiq_gpio_config/gpio_interrupt_control.c, gpio_interrupt_control.h, gpio_control_compat.h and radio_control.c. Original identity/disassembly and static reachability evidence are under original/; readable reconstruction is in pseudocode.md. The same ambiq-gpio-config-simulator target builds the coherent module, now defaulting to build/foundation/radio-gpio-control-simulator. Both test report paths are configurable and exclusive-create.

## Newly recovered contract

Stock interrupt control at 0x4810b0 first validates input nonnull and byte-truncated operation 0–3. Invalid/null inputs return 6 before MMIO; individual pin bounds 0–223 are checked before masking, returning5 for invalid pins. It then saves/masks PRIMASK, performs enable-register read/modify/write and restores the original mask. Individual controls 0/1 disable/enable one bit; mask controls 2/3 disable/enable all seven banks selected by the channel. Two-channel operations visit channel 0 before channel 1 and preserve unselected bits.

Channel range is not validated. Invalid channel bytes target channel 0 only for individual control, but both channels for mask control. The raw adapter explicitly byte-converts both enum arguments to reproduce stock entry behavior while keeping normal C callers on the shared enum interface. This is not a checked safety adapter; callers use valid channels and provide valid readable memory.

Mask input is 28 bytes comprising seven volatile 32-bit words. The HAL borrows it synchronously and rereads it per channel, rather than copying a snapshot. It never retains or writes the input pointer/data. Tests check input reads, masks, unchanged bytes and guards under stable, nonaliasing RAM. Caller data must remain valid through the call; concurrent mutation and destination aliasing are outside this fixture.

The radio enable/disable wrappers configure channel 0/pin 117 through the full API. Their stock return is the literal 117 restored from a local stack argument, not HAL status. Observed callers ignore the value; reconstructed source now preserves it and comparisons assert it. Pin117 is bank3/bit 21, enable address0x40010560. Disabling its enable bit does not clear status, unregister callbacks, change NVIC or drain queued work.

The pin 136 helper tests the low byte of its argument: zero clears WTC4 at 0x40010468/bit 8, any nonzero byte sets WTS4 at 0x4001044c/bit 8. Thus 256 clears and 257 sets. Its electrical role is not established by this software evidence.

The actual shutdown GPIO slice0x4b49d8..0x4b49e6 runs: disable pin 117 interrupt, clear pin 136 output, clear pin 93 output, then configure pin 138/raw3. The pin 93/138 consumer remains status-ignoring and non-atomic. This caller slice begins after WsfTimerStop and ends before caller state clearing and transport release0x52df12. Each included callee runs real original/source instructions; no executable call is stubbed. The slice is explicitly not the full HciDrvRadioShutdown function.

## Provenance and corrections

CONTROL_PROVENANCE.json binds unchanged function/helper text to public Ambiq commit5efc0228528a8adce5eae0d226fac85d2551eb3b and the pinned source hash. Notices are retained. The compatible mask view preserves the seven volatile words and omits unused per-bit names; the sparse register view adds both seven-bank interrupt channels at offsets530 and5a0, stride10. Previous register/layout failure evidence and prior source/ELFs remain preserved.

The first new build exposed a missing AM_HAL_GPIO_MAX_PADS compatibility definition; the stock guard and public header both require224. The failed build log is retained. Initial source/model case comparisons matched, but the declared-byte coverage gate correctly stopped on six unreachable bytes. Static control flow accounts for four helper-failure bytes0x4810ee..0x4810f2 (the immutable helper always returns0) and two default-switch bytes0x481126..0x481128 (validation allows only0–3, all handled by prior comparisons). Failed diagnostics/verifier snapshots are preserved; no fabricated execution credit was assigned.

Independent review then recovered the wrappers' literal 117 return. The initial void-wrapper source/ELF and passing side-effect-only results remain preserved in prior-void-wrapper-source and the first result files. Rebuilt source and stronger comparisons now validate the callable return as well. Assertions on MMIO, masks, data and ABI were retained.

## Fresh validation

Final control-comparison-reviewed.json passes 6,648 stock/source/independent-model cases: all individual pins, operations and valid channels under both masks; multi-bank sparse/full/zero masks; invalid/null/control/pin precedence; raw argument aliases; radio wrappers; pin 136 byte-truth inputs; and the complete selected GPIO shutdown slice. Every reachable control-body byte executes (576 of 582), plus every byte of the 22-byte index helper, two 18-byte wrappers, 28-byte gate and 14-byte caller slice. Six statically unreachable bytes remain excluded. Together with reused callees the profile observes 854 unique original bytes.

The final config-state-comparison-reviewed.json separately passes all 16,108 prior GPIO get/set/state/consumer cases against this rebuilt ELF, observing 406 original bytes. Source manifests match current code. Both comparisons retain ordered MMIO, masks, complete modeled register state, call arguments/order, stack and callee-saved registers. The new suite also verifies borrowed input reads and immutable guards. Only register-device effects are fixtures; original instructions/callees are not replaced by external stubs.

Fresh affected Ambiq tests pass 22 methods. The 42-module aggregate passes 216 methods with 6 method skips and 1 separate setup skip:222 executed method tests,7 skip records, zero failures/errors. Build/source/result identities are in build-provenance.json; exact counts/limits are in validation-summary.json. Independent review passed with no remaining correctness blocker and a fresh 28-case native rerun, including literal 117 return checks. Artifacts are under review/.

Deduplicating payload identity plus runtime byte address against all previous passing evidence adds 480 bytes: 4,564→5,044 (touch 234, Apollo 4,810). Shared GPIO/critical/helpers/callers are not counted twice. Source/header count is 68, including four new files; prior source snapshots and all previous 59 baseline source hashes remain intact. File counts and bounded executed-byte evidence do not measure whole-firmware completeness.

## Remaining prerequisites

This connects a reusable HAL API to real radio boot/shutdown consumers and explains pending-interrupt/control-mask behavior. WTS/WTC and ENS/ENC effects remain synthetic device fixtures with externally supplied output-active masks. Physical GPIO level, pinmux, IRQ delivery, reset/ready timing, clock state, electrical settling and asynchronous controller/transport lifetime are not established.

The highest-value next software prerequisite is the transport startup/release family0x52dd94/0x52df12 and subordinate HAL initialize/configure/enable/disable/power/uninitialize bodies. Existing hardware references infer SPI; exact bus/HAL subtype should be confirmed against pinned public source before calling it IOM. Offline source/disassembly analysis can continue without hardware. Physical observations become necessary for timing and race-safety claims, not for the next software contract.

Resource/dependency distinctions are recorded in dependency-classification.json. Zero of six payloads is demonstrated source-complete; no source-built byte-identical bundle is proven. The optimized tick instrumentation-sensitive execution blocker and its failed artifacts remain unchanged. No commits, staging, flashing, deployment, device writes or security changes occurred.
