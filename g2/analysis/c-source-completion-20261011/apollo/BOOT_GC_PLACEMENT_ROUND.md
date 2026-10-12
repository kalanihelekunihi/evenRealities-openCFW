# Boot source GC and placement frontier

The stock binary is SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
The current selected-source reference is
`boot-coplacement-fp-scale2-connected-bounded-round/receipt.json`:
374 selected units, 1,011 provider symbols, three explicit ROM imports, and
`PASS_BOUNDED_LINK`. All 379 source hashes recorded in this bounded receipt
match the current files; the primary coordinator receipt is also current.

Later source correction supersedes that opening reference: native formatter
`0x41e47a` calls exponent scaler `0x422700` with scale 28 in the hex-float
loop. Selected `float_render.c` now calls the already reconstructed
`opencfw_fp_scale2(fraction,28)` instead of adding 28 to the exponent field.
The source-coherent primary coordinator receipt is
`boot-coplacement-fp-scale2-connected-primary-round/receipt.json` (374 source
units, 1,011 providers, three ROM imports). The bounded ELF receipt is
`boot-coplacement-fp-scale2-connected-bounded-round/receipt.json`:
`PASS_BOUNDED_LINK`, file size 159,100 bytes, 4,708 bytes before the Main
preamble boundary. The refreshed GC map retains the scaler and discards 178
function sections/15,654 bytes. The source scaler matches locked native
raw-word output/errno in 16 bounded cases, including four scale-28 fraction
inputs; denormal multiply/FPSCR edge domains remain unqualified. The optional
coordinator `--include-experimental` variant has duplicate selected
printf/logger/MSPI symbols and is not an accepted receipt.

Full native bodies at `0x41c2d8`, `0x426484`, `0x41b572`, `0x4222a0`,
`0x4273dc`, `0x42e39c`, `0x42c6b6`, `0x42c420`, `0x41b4f6`,
`0x41f2c8`, and `0x430610`
were checked against locked Thumb instructions. The selected C respectively
performs the control descriptor/status query, MSPI INTEN mask clear,
unsigned/sentinel sorted-list splice, low-byte selector 4/5/6 dispatch,
SYSPLL disable, manager callback task creation/fault branching, IOM interrupt
status clear, IOM command-queue enable, port/SVC startup, the byte-output
callback loop with its high-word return, and IOM4 IRQ dispatch. The eleven
source bindings are in
`manual_body_bindings.json`. Their existing
selected source bodies are retained in the bounded ELF, except the standalone
MSPI interrupt-disable function, whose effect is performed through the power
control adapter's `interrupt_disable` callback after the parent's handle
validation. This is a source control-flow binding, not stock-byte identity.
The rooted header-only proof queue fell from 83 to 53 of 654 native rooted
catalogue entries; this queue does not count missing C bodies.
Native `0x42e4f4` matches the selected MRAM alignment dispatcher, and
`0x42ddae`/`0x42ddda` match the selected DFU thread init/deinit bodies.
Their exact bindings and the latest 53-lead crosswalk are recorded in
`manual_body_bindings.json` and
`boot-root-reachability-fp-scale2-connected-round.json`. The latest three
bindings cover private floor/round/ceil bit algorithms: a bounded Unicorn
comparison checks 810 native/source raw-bit cases across zero, subnormal,
finite, infinity, and NaN inputs. The stock tiny wrappers and selected public
hard-float functions still have a separate caller ABI qualification boundary.
Further full-body bindings cover the equal=1 volatile wait adapter, the
retained task-return terminal Thumb path, the exact unsigned clock popcount,
and storage-read callback `0x430a9c`. The latter was already registered in
scatter callback slot `0x200` through a retained Thumb veneer and selected
`storage_read_impl`; no duplicate implementation was retained.
The kernel state wrapper `0x416088` is also retained with native R7-to-R1
return carry, and its runtime-mode child `0x418b56` reads the two exact SRAM
words decoded from locked literal addresses `0x419228` and `0x41922c`.
The stage-one wait-index body `0x423da0` is also bound to retained
`opencfw_boot_shutdown_wait_slot`; the adjacent wait-clear and entry bodies
were already source-bound and now have explicit full-branch notes.
Filesystem allocator free `0x415558` is bound to the existing TLSF mutex/free
provider, and delayed-list next-unblock refresh `0x418b28` is bound to the
selected scheduler source with both stock SRAM literals decoded.
Tracing the largest apparent discarded LittleFS root corrected an earlier
binding: native `0x41527e` calls the `0x412fae` internal body on a missing
directory, whose `LFS_ERR_NOENT` and `LFS_ERR_EXIST` branches identify pinned
`lfs_mkdir_`. The previous manual association with `lfs_remove` was wrong.
Selected `ensure_directories` already calls retained `lfs_mkdir` on that same
branch. The corrected crosswalk removes a false 328-byte GC placement lead;
it does not require a source C edit.

`audit_boot_gc_placement.py` reads the selected linker map and emits
`boot-gc-placement-mutex-round.json`. GNU ld GC discarded 179 compiled
function sections totalling 15,912 bytes, nine read-only data sections
totalling 112 bytes, and two BSS sections totalling 1,208 bytes. Among
those, 65 function sections/4,666 bytes have manually bound stock bodies;
52 sections/3,754 bytes bind bodies in the **limited** 654-function direct
native graph rooted at vectors and decompressed startup callbacks. Some
functions are inlined or replaced by equivalent selected call paths, so
these counts are a proof and placement queue, not 52 missing functions.
Three high-value cases already have a concrete source-path explanation:
`opencfw_boot_memcmp` (336 bytes) is inlined into retained
`opencfw_boot_compare` (its compiled body contains the aligned word and tail
byte loops); `opencfw_boot_crc32` (382 bytes) is inlined into retained
`opencfw_boot_verify` (its compiled body contains the `0xedb88320` polynomial);
and `am_hal_mspi_interrupt_disable` (48 bytes) is expressed by the retained
power-control adapter callback. Those three sections total 766 bytes; CRC32
is outside the limited direct-rooted graph, while the other two account for
384 of its 3,754 discarded bytes without duplicate standalone sections.
The UART receive collector (94 bytes) is inlined into retained
`opencfw_boot_uart_rx_pump`, whose target disassembly calls the ring-add
child and has no collector call; the claim routine (80 bytes) is inlined
into retained `opencfw_boot_uart_rx_start`, whose target disassembly calls
the critical-save and pump children without a claim call. These two source
paths account for another 174 bytes. Runtime equivalence is still distinct
from this compile/link path evidence.
Three more sections have bounded selected-path explanations in
`boot-gc-reviewed-paths.json`: 196-byte PLL fractional calculation is
inlined into retained VCO generation; 52-byte SYSPLL disable is inlined into
class-6 release (target `0x412556..0x41257e` shows the token and two
ordered register clears); and 108-byte `memchr` is represented by the
formatter's bounded precision byte scan. The 152-byte port-timer
clock-configure body is inlined into retained port-timer configure, whose
target body calls the clock request/release children without a separate
clock-configure call. The selected format parser implements native
`strchr("hjltzL", byte)` as a direct switch including the NUL terminator;
the selected formatter handles native constraint dispatch via the typed
handler cell and abort path. Eleven reviewed sections/1,532 bytes are thus
accounted for as source call paths. The retained mutex take, runtime action,
and RTOS allocate/free bodies also inline their selected mutex-priority
inheritance, thread-state check, and free-list insert providers. Target
disassembly has no standalone calls to those three providers. The reviewed
total is fourteen sections/1,940 bytes across all discarded sections. CRC32
is outside the limited direct-rooted graph, so thirteen sections/1,558 bytes
are reviewed within the 52-section direct-rooted queue. The selected pinned
`plain_printf.c` retains its static shift/add divide-by-ten helper inside
`uint64_to_str`; this also accounts for the separately discarded 124-byte
`opencfw_boot_u64_div10` source section. Fifteen sections are reviewed in
total, fourteen of them directly rooted (1,682 bytes); 38 sections/2,072
bytes remain in that queue. Runtime and edge-domain equality are separate
gates.
Further retained target disassembly establishes three more inlined paths:
the 90-byte MRAM aligned lower is in `opencfw_boot_mram_dispatch`; the
112-byte Cortex-M initial frame builder is in `opencfw_boot_thread_initialize`
at `0x426e2e..0x426e6e`; and the 98-byte NOR busy status test is twice in
`opencfw_bl_nor_wait` at `0x421e22` and `0x421ea8`. The 86-byte UART IRQ
receive drain is in `opencfw_boot_uart_irq_row`, including its FIFO call,
callback, and count reset at `0x41d9b0..0x41d9c6`. The reviewed direct-rooted
queue is now 18 sections/2,068 bytes, leaving 34 sections/1,686 bytes.
The release-needed descriptor test is also inlined into retained
`opencfw_bl_mspi_mode_leave`: the compiled parent repeats descriptor-copy at
`0x422b8e` and branches through the group/register checks before its status
poll. This brings reviewed direct-rooted paths to 19 sections/2,148 bytes
and leaves 33 sections/1,606 bytes.
The id-zero request/release bookkeeping children are inlined into the two
retained clock dispatchers. Their compiled table arms at `0x4128fe..0x41293e`
and `0x41299a..0x4129dc` retain the user-bit test, PRIMASK save/restore,
and set/clear. The current reviewed direct-rooted total is 21 sections/2,276
bytes, with 31 sections/1,478 bytes still needing path/root review.
The next compiled-path tranche proves five more inlinings: mode-2 PCM timer
sequence (114 bytes) into timer service; UART DMA error classification,
receive stop, and disable (148 bytes combined) into IRQ dispatch; RTOS heap
first-use initialization (68 bytes) into allocator; and kernel tick delay
(64 bytes) into CMSIS delay. The retained target disassembly preserves the
associated MMIO writes, callback branches, heap sentinel initialization,
and scheduler calls. This brings the direct-rooted queue to 27 reviewed
sections/2,670 bytes and 25 open sections/1,084 bytes.
The storage callback's separate address validator (56 bytes) is expressed by
the retained range-valid logic in the three callback implementations; target
read/program bodies call device-info query and compare against `0x4000`.
The 52-byte radio callback-finish routine is inlined twice into class-2 clock
request, including active check, wait, PRIMASK save/restore and pointer clear.
The 36-byte thread-name getter is represented by the retained logger metadata
wrappers and their current-task/fatal path. The 16-byte LittleFS rewind call
in boot-count update is source-owned by `lfs_file_seek(fs,file,0,LFS_SEEK_SET)`;
pinned LittleFS defines rewind through the same internal seek, and the stock
caller ignores its return. Current queue: 31 reviewed sections/2,830 bytes,
21 open sections/924 bytes.
Two EasyLogger lock helpers are inlined into retained logger bodies, with
direct service wake/sleep calls and lock-state stores. Mutex take inlines
current-owner claim and timeout waiter-priority calculation. The timer's
three-read PRIMASK snapshot is directly present in retained `counter_read`
and `timer_compare`; the unmasked STIMER status read is directly present in
the vector handler. Current direct-rooted queue: 37 reviewed sections/2,978
bytes, 15 open sections/776 bytes.
Further target-path review bound the sampled class-2 radio mode, two power
callback slots, port timer gate set, INFO0 identity offset, folded TLSF
overhead, and UART's 32-byte drain path whose return is ignored by its
recovery caller. With the newly retained scaler and the newly bound DFU
deinit/stream-put entries in the refreshed map, 44 of 53 direct-rooted
discarded sections (3,086 of 3,590 bytes) have compiled-path explanations;
9 sections/504 bytes remain. The source-owned DFU callback table actually
relocates its deinit slot to retained `opencfw_boot_dfu_thread_deinit_native`,
whose target body at `0x4260e4..0x4260fe` preserves the two handle reads,
termination, clear, and zero return. This qualifies one newly bound duplicate
path, leaving 8 sections/474 bytes. The unresolved set is enumerated in the
refreshed `boot-gc-placement-fp-scale2-connected-round.json` and includes
qsort memmove, the TLSF generic FLS branch, two IAR memory helpers, the
ambient clockmux entry, the IAR thread pointer, and the stream-put helper.
Pinned TLSF's generic FLS and selected Clang builtin branch both compute
`bit_length(word)-1` (zero yields `-1`); `verify_tlsf_fls_branch.py` checks
100,006 deterministic values, and retained target TLSF bodies contain CLZ.
The selected ABI startup root calls the full clockmux C fragment at `0x42607e`
with explicit ambient carries, so its separate raw-register entry veneer is
not part of that selected call path. These two branch helpers and the veneer
reduce the refreshed direct-rooted queue to 5 sections/322 bytes. Native
formatter `0x41e47a` calls the TLS anchor `0x422874`, then reads the decimal
character through anchor `0x20000518` plus `0x24`; retained float-render C
reads that same volatile pointer slot at `0x2000053c`. The formatter is also
the only native caller of stream-put `0x41f2c8`; the visible one-byte padding
calls check its low status only, and selected engine `put`/`repeat` carries
the same callback-state/count sequence. Those bounded callsites close two
sections. Caller-by-caller fill review then finds 18 direct calls with ignored
returns and selected zero/space fills of the same byte ranges across LittleFS,
logger, allocator, RTOS, startup, UART, and DFU. This closes IAR fill for
ordinary RAM final-state semantics. The aligned-copy 29-call census maps 23
sites to pinned selected LittleFS bodies and six to source-owned
descriptor/command copies. A locked native execution oracle checks 256
nonoverlapping SRAM cases across 16 lengths and every 4x4 alignment pair;
final copied bytes and untouched guards match a forward C copy. This closes
aligned copy for valid nonoverlapping final-state calls. A fresh current-source
M4 sort differential executes both the stock and selected sort on 98
eight-byte-record fixtures (counts 1–256, reverse, random, duplicate-heavy,
and equal-key) and matches complete record output. The current selected
`qsort.c` SHA matches the bounded Boot receipt. This closes the qsort memmove
GC path at the initializer's operation-level final-record scope: all 53
direct-rooted discarded sections/3,590 bytes now have reviewed selected
paths. Exact intermediate write order, impure comparators, concurrent
observers, arbitrary record widths, physical formatter stack offsets,
overlap, and whole output remain unqualified.
These are selected compiled path receipts, not whole native runtime proofs.
The discarded 158-byte `opencfw_boot_memmove` follows stock qsort helper
`0x423928`. Selected qsort uses a different whole-record rotation algorithm
with a 128-byte scratch buffer. The 98-case differential establishes the
bounded complete-record output, not exact write order or an inlined copy.
The locked-decomp census in `boot-iar-helper-callsites-fp-scale2-round.json`
finds fill `0x41560c` at 18 direct callsites in 16 callers and aligned copy
`0x4156ac` at 29 callsites in 18 callers. All displayed sites ignore the
helpers' raw R0 returns. Fill and copy reviews are limited to final bytes in
ordinary RAM and valid nonoverlapping copy calls; exact write order and
unusual caller-provided MMIO aliases remain separate runtime gates.

The current bounded file is 159,100 bytes and the authenticated Main preamble
begins at offset 163,808: 4,708 bytes of current file slack. Adding all 53
direct-rooted discarded function sections at their compiled sizes would
consume 3,590 bytes before any linked rodata, padding, veneers, or further
indirect roots. This arithmetic makes a selective root/inline proof necessary;
neither retaining every discarded section nor treating GC as completeness is
supported. The actual bootable layout and ROM behavior remain open.

Current whole-image gates:

* Resolve each direct-rooted discarded provider as a retained C path,
  proved inlining, or authenticated unreachable stock path. The JSON
  records every section, source file, size, and bound stock address.
* Add runtime-installed task, registration, computed-dispatch, and external
  ROM callback roots to the selected-link audit; the 654 graph excludes them.
* Qualify complete source-owned scatter/load/absolute-reference placement,
  plus any compiler veneers and initialized-data adjacency.
* Keep the three ROM contracts external until their entry/ABI/hardware
  behavior is authenticated; no firmware image completion claim follows from
  the current bounded link.

## Record walker and next rooted source proof

Native `0x43299c` repeats until its callback-returned cursor equals the end
record. The selected `startup/record_dispatch.c` previously used `< end`,
which could stop before reaching equality. It now uses `!= end`; the callback
return remains the next record. The current source-coherent selected receipt is
`boot-coplacement-record-walker-equality-round/receipt.json`:
`PASS_BOUNDED_LINK`, 374 selected units, 1,011 providers, three ROM imports,
159,100-byte ELF, and 34 callback relocations. This is a source control-flow
correction, not proof of every native callback return or physical scatter.

The direct-root conservative header-only proof queue is now 40/654. Thirteen more
whole-body bindings are reviewed: list unlink `0x41b5a8`, four-word descriptor
copy `0x41b8f8`, device mode gate `0x421548`, FPU startup `0x432958`, active-clock wait `0x4216b2`, CMSIS delay `0x416378`, fresh queue helper
`0x419d68`, SysTick `0x41b428`, startup runtime entry `0x43297c`, scatter record walker
`0x43299c`, indexed register read `0x41d90e`, and static mutex initialization
chain `0x419d8a`/`0x419dc2`. The fresh-queue helper native ambient R3 return is discarded by both
authenticated direct callers: `0x419c9c` overwrites R0 with the control block
after BL, and `0x419d08` overwrites R0 with the allocation. Its arbitrary
external caller ABI remains unqualified. The earlier 53/53 discarded direct-root section path
review remains bounded final-effect/retention evidence. Native indirect and
ROM callback producer equality, full data/scatter placement, and physical
runtime behavior remain separate gates.

## Clock descriptor direction correction

Native `0x422416` uses fixed source literal `0x422464`, independently decoded
as SRAM `0x2000007c`, then writes 20 bytes to its argument. The previously
selected source copied the caller argument into that fixed SRAM address. The
source now reads fixed SRAM into the caller's mutable volatile descriptor;
`startup_alternatives.c` retains its local destination as writable volatile
storage. Target disassembly confirms loads from `0x2000007c` and stores to R0.
`boot-coplacement-clock-descriptor-direction-round/receipt.json` is current,
`PASS_BOUNDED_LINK`, 374 selected units, 1,011 providers, three ROM imports,
159,100-byte ELF, and 34 callback relocations. The exact IAR aligned-copy
intermediate write pattern and physical SRAM producer are separate gates.

Fresh direct-root crosswalk/root reports 37 header-only proof leads among 654
reachable catalogue entries and zero machine-unattributed direct roots. Other
reviewed source paths include queue-empty critical read, C11 constraint
dispatch with named ambient-return Thumb wrapper, nullable power callback
through slot `0x20026e3c`, and dynamic mutex construction. Indirect native
callback producer/consumer equality remains unproven by this direct-root
count.

Further rooted body bindings reduce that proof queue to 31/654. Native
`0x41b55a` list append, `0x41b6e2` STIMER wrapper, and `0x41b3ba` port FPU
register enable map to selected whole bodies. The native nullable post-hook
`0x41cdfa` reads installed slot `0x20026e60`; its effect is source-owned by
`mode_notify_hook` inside selected `runtime_transition.c`, with the callback
producer and arbitrary callback behavior still external. Existing C11
constraint and power callback bindings were corrected to point at their
actually selected ASM/C units, rather than duplicate or core-only units.

The latest rooted full-body proof queue is 25/654 after another six bindings:
first-task SVC transfer, nullable boost callback, PendSV write with barriers,
reset stack-limit entry, idle task memory outputs, and IAR semihost terminal.
Authenticated literals fix the reset limit at `0x2007d000` and idle output
addresses at `0x20026970`/`0x200250d0`. Their target instructions and selected
source bodies are attributable; exception/semihost hardware and installed
callback producer behavior remain unqualified.
