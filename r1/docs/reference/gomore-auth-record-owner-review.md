# R1 shared GoMore authorization record

The locked application's SDK authentication parser at stock `0x8EA0C` writes
through a status pointer at `0x20007C50`. Runtime validation already had a
source owner for that address, but it declared only the first 12 bytes. The
parser also writes the word at offset 12 and increments a byte at offset 16.
`native_gomore_runtime_configuration.h` now declares one 20-byte owner for
both uses. The existing UTC offset and timestamp limit remain at their prior
offsets; no second RAM owner is introduced.

The ignored probe `build/r1-auth-record-owner-20261111/verify.py` executes the
locked application's actual startup decompressor at `0x286F4`. The initialized
20 bytes at `0x20007C50` match the current compiled C object's complete
`.r1.gomore.runtime.configuration` section byte for byte:
`00000000 ffff0000 00000000 00000000 00000000`. The same startup run
resolves the parser's three validation callbacks to `0x65051`, `0x65029`,
`0x65071` and four field parsers to `0x57B39`, `0x57C45`, `0x57C85`,
`0x74D0D` (Thumb pointers). The final parser at `0x74D0C` is executable
stock code even though the current Ghidra function inventory omits it.
Those callback bodies are still integration dependencies, not installed
function pointers in the C firmware.

The final field parser at `0x74D0C` now has a typed C implementation in
`gomore_primitives.c`. It checks the two-byte `S1` signature, increments the
shared field count, records `-1007` in the fourth status slot on mismatch,
and applies the existing status/random helper before updating the per-call
state. The helper now passes the status seed to a typed seed callback before
reading the random result, matching stock `0x6AAC0`; its former no-argument
callback could not represent this operation directly.
`build/r1-auth-record-owner-20261111/verify_final_field.py` compares
100 cases across the locked stock function, host C, and the actual production
Arm object. Returns and complete 20-byte state and 16-byte status records
match. Cases cover both signature outcomes, prior status errors and counts
zero through three, including the count-four clean-success seed and random
path. The callback is source-owned but not yet bound into the SDK parser.

The [SDK authorization adapter](health-sdk-auth-c-review.md) now binds these
callbacks and matches the stock cold token and two rejection paths. Its latest
R1 source receipt compiles 946 application and 82 bootloader units. The strict
application receipt has three Goodix calculation roots unresolved and uses
663,720 of 696,320 flash bytes with no overflow. The parser is not yet
validated on physical hardware, and the application still does not link.
