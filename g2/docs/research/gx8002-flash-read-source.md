# Flash read wrapper candidate

Source runtime_gx8002_flash_read.c reconstructs package0x15830/runtime0x1002381c.
It waits once even for length zero. While bytes remain, it selects the signed
minimum of the length bit pattern and65536, reloads the word-read callback
from shared state+28, calls it with address/destination/chunk, ignores its
result and advances all three counters. Pointer advancement is explicit
uintptr_t arithmetic; target integer/address wrap is retained.

For lengths below0x80000000 this splits at64KiB. Lengths with bit31 set are
passed unchanged in one callback invocation because the original MIN.S32
regards them as negative. This is a fidelity requirement, not a new validation
policy. The target GCC cast to int32_t produces the observed MIN.S32; an
explicit sign-bit-or-small predicate produced80 bytes instead of60. Native
candidate is60/60 bytes and uses the original28-byte saved-register frame.
The code is not byte-identical because register allocation differs.

Full decoded callback/read/argument/return and pointer-wrap verification is
pending. The callback must be valid for the request; ordinary word-I/O buffer
alignment requirements remain. No physical flash reads were performed, and
the candidate is not registered for firmware admission.

Decoded verification now passes177 cases with changing callback pointers,
two caller-clobber patterns, zero/sector-size/64KiB boundaries, high-bit lengths
and address/destination wrapping. The largest signed-positive length0x7fffffff
executes32768 callbacks to completion in both stock and source. All calls,
callback reloads,28-byte frame, preserved registers and return value match.
Five oracle/rejection tests pass. Callback bodies are modeled; synthetic
wrapping destinations do not imply valid physical buffers. Admission adapter
and integration remain next; no hardware was accessed.

Integrated through the reviewed admission adapter. All177 native macOS codec
tests, full package build and artifact verification pass. The complete60-byte
stock interval is now compiled C, without new fill. Physical buffer validity,
callback composition and whole-device execution remain unqualified.
