# GoMore variadic logger C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-log-c-review.md) records ownership consolidation and normal-build integration.

Stock logger `0x823d8` remains unresolved in production. The experimental
C candidate and fixtures are under `build/goal-r1-gomore-log-c/`; the
[receipt](gomore-log-c-investigation.json) binds REA, compiled source and replay.
No firmware source or source manifest changes at this checkpoint.

Stock clears 256 message bytes before reading configuration. It checks callback,
enabled byte, level mask and category mask in order. Register shifts use the low
eight count bits, with amounts 32..255 yielding zero; count 256 therefore selects
bit zero. The category mask is a halfword. Callback is reloaded after formatting,
so replacement by a lower provider affects the final call.

The prefix is `[GoMoRe]`. Formatting targets message+8 with size 248. A separate
four-byte sentinel immediately after the message is cleared after formatting.
Stock appends CRLF with strcat whenever the unsigned formatter result is below
248. Lengths 246/247 spill suffix bytes into the sentinel. The generic checked
u32 logger suppresses this spill and imposes different argument/shift guards;
it is not a direct stock-ABI provider.

A C struct groups the 256-byte message, sentinel and va_list. With Clang Oz the
frame totals 296 bytes, message is entry SP minus 292, and the variadic argument
pointer is entry SP minus four, matching stock. The first R3 argument and five
stack argument words are checked numerically. There is no inline assembly.
Compiler-private saved-register layout differs and is excluded; malicious lower
providers modifying those private slots are outside the current proof. Void R0
is excluded from the API result comparison.

**4,390 native/C cases** pass, each with independent gate and final-message
expectations. They cover enable/callback/mask combinations, large shift counts,
lengths 0/1/245/246/247/248/249/UINT_MAX, and formatter replacement of callback.
Stock clear/strcat execute on both paths; formatter and callback are modeled.
The full message, exact published pointers, adjacent sentinel effects,
configuration and completed-call saved integer registers/SP are checked.
Actual formatter behavior, doubles/alignment consumption and caller integration
remain pending rather than inferred from the modeled six-word argument view.

Configuration is 12 bytes at `0x20007cec`: enabled byte at zero, category halfword
at two, callback word at four and level mask at eight. Executing native RW startup
and independently decoding its compressed image both yield twelve zero bytes;
surrounding region guards are unchanged. A production owner has not yet been
added. Negative controls, generic-owner consolidation, production-object replay,
normal build and qualification remain required before promotion. Physical
execution, complete source-only link and byte identity remain unproven.
