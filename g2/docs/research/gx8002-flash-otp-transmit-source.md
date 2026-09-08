# OTP byte transmit candidate

Recovered runtime_gx8002_flash_otp_transmit.c from package0x15e28/runtime10023e14.
Native macOS compilation currently184/164 bytes; not admitted. Default-Os,
-fno-shrink-wrap and-Oz give184; priority allocator188, disabled loop-invariant
movement196,-O2=200,-O1=192. Fitting and decoded qualification remain.

The routine waits idle; disables controller8; setsA0300090=2; clears4c and10;
sets0=0x407,4=length-1,18=0,f4=0,50=8,8=1. For each prefix byte it polls28&2
and writes a byte from state.command+i to60. It then writes controller10=1
before payload transfer. Each payload byte similarly polls28&2 and writes60.
It waits TX empty, disables8, writesA0300090=3 then1, enables8, waits flash
ready and returns0. Length zero still performs setup (length-1 wraps), mode
transition and cleanup. Prefix length zero skips only its transfer loop.

Both loops and unsigned pointer arithmetic are explicit; unbounded polling
matches stock. Requests extending beyond the command buffer or valid payload
storage are not certified by this reconstruction. No hardware transfer was
performed. Helper names are local source bindings to already qualified entries.

Separated payload pointer increment from dereference; default remains184.
Generated code uses r12 for the initial zero/prefix counter, lengthening
several stores, and emits extra byte-load/extension instructions. Additional
individual pass probes: -fno-ivopts=180, -frename-registers=224; disabling
schedule-insns, schedule-insns2, GCSE, tree PRE, expensive optimizations,
caller saves, tree TER, dominator opts or peephole2, or IRA region=one, stays
184. Probe sizes do not establish semantic equivalence and are not admission.
Current source/builder still default-Os184; fitting remains unresolved.

Added a source-authored LD.B intrinsic returning uint32_t, expressing CK804
zero extension without redundant compiler extensions. Both prefix and payload
loads use it; default build now180/164. This is explicit inline assembly in
otherwise C, not extracted instruction bytes. A separate LD.W status intrinsic
did not improve size and was removed. With the byte intrinsic, no-ivopts,
no-tree-loop-optimize and no-ivopts+priority allocator stay180; priority alone
184. Current candidate still needs16-byte reduction and decoded qualification.

Combined status LD.W and ANDI into one source-authored temporary-register
intrinsic; native size now176/164. It retains volatile memory ordering and
reads the same status word once per poll. Register-reservation probes had no
benefit. The local GCC constraints.md establishes constraint a as r0-r7; an
experimental low-register prefix-address intrinsic also stayed176 and was
removed. Current candidate keeps byte-load and status-mask intrinsics only.
Decoded qualification and remaining12-byte fitting are still outstanding.

Fitting resolved to160/164 bytes. Empty inline-asm read/write constraint first
forced the prefix counter into GCC's a (r0-r7) class, giving160 but growing
the frame16->20. Binding that counter to r0 with a matching empty +r operand
keeps160 and restores the original16-byte frame. The empty constraint emits
no code; it guides register allocation and makes the counter opaque to compiler
loop transformations. Counter instructions, register lifetime across helpers,
MMIO trace and byte transfers still require decoded verification. This is not
admitted based on fitting alone. Twelve further pass probes on the previous
176-byte source all stayed176.

OTP transmit decoded comparison passes1368 cases: prefix0..8, length0..33,
255/256/257/1024, ordinary and wrapping payload pointers, zero/two stalled
polls. Exact ordered MMIO/byte-read/helper traces and ABI returns match stock.
Reuses qualified word-I/O interpreter logic, adding decoded byte reads and
postincrement. Helpers modeled; synthetic wrap does not certify valid buffers.
Rejection tests and admission remain; current114-function package unchanged.

Seven focused tests pass: zero-length setup/cleanup, prefix/payload address
order including wrap, wrong frame, missing/extra effects, saved-register
corruption and unknown instructions. Checker now restricts the saved-register
set and requires16-byte frame at every helper call. All1368 comparisons pass
again. Reviewed admission adapter/report generated and registered; full codec
integration is running. Registration is not yet successful package admission.

OTP transmit fully integrated:214 tests pass; native macOS package build and
verify-artifacts pass.115 functions/131 code occurrences/16 data regions;
7472 C,2040 data,80 metadata,306 fill,316194 retained bytes. Codec SHA:
ff9b2c77bf14c3816086e4629cc1c81cd20bc1deae6a79f58feeadc60e20f1fe.
Package SHA:1cac2b2301ef15916da06e874b603401b5f3fde6cd48b6367627f90b0baad178.
Candidate pin is not vendor identity or hardware qualification. OTP write
also passes ten new overflow cases besides1344 baseline cases; rejection
checks and admission remain. Full source-only goal active; hardware untouched.
