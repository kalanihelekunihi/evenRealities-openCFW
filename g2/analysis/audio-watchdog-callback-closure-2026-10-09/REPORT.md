# Actual audio watchdog callback and type6 behavior

**123 PASS original/source comparisons**, ELF `ce678646719f3a1203ca531c5a87f94d76d89b05b812dbd6d1d49809c8bd749f`. [Readable C/header](../../components/audio/watchdog_callback_offline/README.md), [pseudocode](pseudocode.md), [addresses/hash provenance](function-bindings.json), [results](results.json). Callback0x53C2A4 and emitter0x53CA10 are complete selected bodies; handler0x53C92E is reconstructed only with logging-mask0 at every read.

## Callback argument is unused

Stock timer callback0x53C2A4 ignoresR0. It zeroes a12-byte message on its stack, sets type6, and calls real publisher0x53C638. Tests use arguments0,1,0xCAFEBABE,0xFFFFFFFF and get identical message bytes `060000000000000000000000`. No argument memory is accessed. Thus the earlier auxiliary-reuse test's forwarded0xCAFEBABE argument does not demonstrate that this callback uses corrupted argument data. The adapter still reads callback/argument from its auxiliary allocation; overwritten callback pointers or other callbacks remain different cases, and live lifetime reachability is unverified.

Publisher uses control block0x20003F98: queue+12,thread+8. NULL queue returns. Actual CMSIS put0x449ABE is called with priority0,timeout0ticks. Empty queue receives a real12-byte copy and then reaches thread-flag set0x449238(thread,0x400000); tests stop before that entry, without fabricating its result or dispatching an audio task. Full queue fails through actual queue/CMSIS code, executes real mask getter with0, and produces no thread-flag call. Error logging is absent only under the explicit mask0 contract.

## Type6 counter check and next action

Authenticated startup table maps type6 to0x53C92E. If enabled byte0x2007502E is0, handler returns without clearing counter0x20074A9C. Otherwise it snapshots that counter and clears it immediately. Prior count<20 calls emitter0x53CA10(2), which publishes `{type0,mode1,value2}`. Prior count>=20 emits no control under mask0. This is a threshold on prior consumed-PCM counter observations, not20milliseconds; the earlier PCM consumer report identifies the increment. No physical sample cadence or complete DSP restart is inferred.

The type0 callback's subsequent action depends on role: role1 takes its nonzero DSP-enable/gate/I2S path; other role with value2 enters special control0x57A816(0). Those downstream actions remain the earlier explicit provider boundaries. Calling type6 is not itself proof producer-stop completion or successful restart.

Cases cover queueNULL/empty/full, enabled0/1/255, counters0/19/20/21/UINT32_MAX, ignored callback/handler arguments, and emitter byte aliases. Real publisher,getter,queue initialization/copy and CMSIS peers execute; no return stubs. Logger-enabled handler branches remain static unimplemented branches; no claim all-input handler equivalence. Timer start's documented2000 value is retained as ticks; this batch does not derive wall-clock units or scheduling. No firmware patch,hardware fault claim,commit or device write.
