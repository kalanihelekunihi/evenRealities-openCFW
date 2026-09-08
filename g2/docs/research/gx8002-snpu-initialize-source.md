# GX8002 SNPU caller initialization recovery

Stock package0xf280 / runtime0x10205cf4 contains a 64-byte instruction body
and 12 bytes of local literals. The pinned SDK snpu.o identifies gx_snpu_init.
The C candidate compiles to 76 bytes and preserves these ordered operations:

1. Call device_init with base0xa0c00000.
2. Store pointers at state+0x5c4=0xa0c00000, +0x5c8=0xa0300000,
   and +0x5cc=0xa0c00190.
3. Clear words +0x5b4 then +0x5b0.
4. Call task descriptor initialization.
5. Register ISR0x10205ce0 with null private data.
6. Store state2 and return0.

The recovered empty device_init signature now accepts its ignored base
argument. Its target bytes and behavior remain unchanged. The caller's
offset-only state view does not claim complete state understanding.

Qualification passes 201 cases and eight tests: helper mutations of observed
state at every call or the last call, conservative caller clobbers, ordered
stores, exact callback/base/private arguments, final state overwrite and
12-byte frame. TCB initialization and ISR behavior are separate obligations.
The caller is qualified and registered. Files use snpu_initialize /
snpu-initialize; reviewed report gx8002-snpu-initialize-verification.json;
admission artifact snpu-initialize.elf.

Integrated macOS candidate passes all 494 tests. Remaining helper recovery
is tracked separately; this does not establish complete source-only firmware.
