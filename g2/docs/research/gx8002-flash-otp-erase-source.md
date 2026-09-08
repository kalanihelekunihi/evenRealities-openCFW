# OTP erase candidate

Recovered runtime_gx8002_flash_otp_erase.c from package0x15bec/runtime10023bd8.
Native macOS C-SKY compilation fits92/92 bytes. Not admitted.

It reads selected_device and its signed manufacturer halfword. Unsupported
manufacturers return0 without further reads or calls. For0x5e/0x85 it reads
OTP descriptor pointer(+20), then flags(+16), base(+0), stride(+4), in order.
It writes command[0]=0x44 before wait-ready and write-enable. It then invokes
the address encoder with the state address-width pointer, wrapped
base+(flags&7)*stride and command buffer. Command-write receives a fresh read
of command[0], command+1 and length3, then wait-ready runs and the function
returns0. All helper returns are ignored. Descriptor fields remain snapshots
across helper calls, while the command byte is intentionally reloaded.

Decoded ordering, wrap arithmetic, helper mutation and clobber, frame and
rejection qualification remain. No physical OTP erase was performed.

Decoded stock/source comparison passes2000 cases over supported and signed
unsupported manufacturers, all region selectors plus high flag bits, zero and
wrapping base/stride values, and two helper-clobber seeds. It checks ordered
reads and command initialization,20-byte saved frame, exact encode and write
arguments, final wait, and unconditional zero return. The modeled encoder
changes command[0], requiring a fresh load before command-write. Five
rejection tests pass. Prepared reviewed admission report; not yet registered.
Helper bodies and physical flash effects remain separately qualified/unproven.

OTP erase fully integrated:207 tests pass; macOS full package build and
verify-artifacts pass. Ownership7312 C,2040 data,80 metadata,302 fill,316358
retained;114 functions/130 code occurrences/16 data regions. Codec SHA:
e0e125de64f3ebd3f3cf510b9ad1cac594ee6c2d96759fdd9fee63b1dc1ae50f.
Package SHA:87f057ec9cae015378f8abd9dcc041fcd39e5bae35e8d49ae6e1afd25c0aa6f1.
Candidate pin is not vendor identity or physical qualification. Goal active.
