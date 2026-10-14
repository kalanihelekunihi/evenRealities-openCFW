# Independent review: deferred event callback callable type

## Finding

Both reviewed negative-message consumers use a C function-pointer type incompatible with the actual callback functions they can receive. This is a source-language callable-contract defect, although the word-sized Cortex-M0 register layout matches in the current native path.

At `g2/components/case/startup_candidate_20261011/application_boot_timer_expired_candidate.c:23`, the indirect call casts the stored target to `void (*)(uint32_t, uint32_t)` and passes `message[2]`, `message[3]`. At `g2/components/case/deferred_consumer_offline/consumer.c:20`, the same signature is used for `m.arg1`, `m.arg2`. The registered event callback declarations and bodies instead have type `void (*)(void *, uint32_t)`: `g2/components/case/source_candidate_20261010/event_clear_callback.c:3-8` and `g2/components/case/startup_candidate_20261011/event_set_callback_candidate.c:7-12`. Calling a function through a pointer to an incompatible function type is undefined behavior in C, even where the target ABI places the same 32-bit bit patterns in the same registers.

## Native evidence and producer chain

I disassembled the locked official `firmware_box.bin` at the relevant ranges (its SHA-256 is `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`; the first 32-byte container header was removed for the raw code image).

- Native timer consumer `0x0800b0fc`: `0x0800b116` loads R2 from `[SP,#12]` (callback word, message[1]); `0x0800b118` loads R1 from `[SP,#20]` (message[3]); `0x0800b11a` loads R0 from `[SP,#16]` (message[2]); `0x0800b11c` executes `BLX R2`. Thus the actual native call is callback(message[2], message[3]), with the event handle/pointer in R0 and bit mask in R1.
- Native callback addresses are `0x0800bf84` (clear) and `0x0800bf8c` (set), with Thumb function-pointer values `0x0800bf85` and `0x0800bf8d`. Their bodies at BF84/BF8C forward R0 and R1 to the clear/set providers; they do not show a reversed or third argument.
- Native producer `0x0800c478` loads callback literal `0x0800bf85` from `0x0800c488` and tail-calls event dispatch `0x0800ce0c` with the event in R1 and bits in R2. Native producer `0x0800c568` similarly loads `0x0800bf8d` from `0x0800c578` and passes task/event and bits.
- At `0x0800ce0c`, the event-dispatch routine materializes four words `{0xfffffffe, descriptor, event, bits}` on the stack and calls scheduler/message-special `0x0800c7a8`. This is the negative-command callback message shape consumed at B0FC. The source reconstruction at `g2/components/case/startup_candidate_20261011/application_policy_event_scheduler_helpers_candidate.c:13-18` preserves that ordering. The separate offline producer `g2/components/case/deferred_event_offline/deferred.c:27-31` likewise stores `{ -2, callback, arg1, arg2 }`, and its callback producer declares the set callback as `void(void *, uint32_t)`.

The native R0/R1 ordering corroborates the source types. It does not make the current `uint32_t`/`uint32_t` indirect-call type compatible with `void *`/`uint32_t` at the C language level.

## Bounded repair guidance

Use the actual callback type in both consumer calls: `void (*)(void *, uint32_t)`. Convert the stored first argument through `uintptr_t` to `void *` at the call boundary, e.g. `(void *)(uintptr_t)message[2]` or `(void *)(uintptr_t)m.arg1`; pass the second word unchanged as `uint32_t`. This retains the native machine contract (R0=event pointer bits, R1=bits) and leaves the callback bodies' return/void contract intact. Do not change unrelated callbacks: only these negative-message slots are established as event set/clear callback slots here.

## Verification limits

This review confirms a source-level incompatible function type and the locked native register flow. It does not establish a runtime behavioral divergence, because the present 32-bit M0 convention carries the arguments in the same two core registers. It does not validate scheduler queue lifetime, timer/IRQ interleavings, physical IRQ behavior, or event-group provider semantics. Existing wave 056-058 checks that stop at callback entry do not prove the callback's C function type or body; those checks therefore cannot discharge this finding.
