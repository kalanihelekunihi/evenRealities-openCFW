# Peripheral C source completion checkpoint

## Changes and evidence

- Added isolated EM9305 `QEQueue_init` C source candidate from the retained official QP/C v6.5.1 `qf_qeq.c` at commit `416dcec8820b9cdb5827497e645d0d9375db53c6`. The 32-bit compilation asserts all seven observed stock field offsets 0, 4, 8, 9, 10, 11, 12. Apple clang emitted a 32-bit ARMv4T Mach-O object; this is **not ARCv2 EM/EM7D target compilation**. Native semantic test passed seven qLen cases (0, 1, 2, 254, 255, 256, 65535), checking ring/front, conditional head/tail writes, narrowing and wrap. No original ARC execution comparison or application link exists.
- Promoted the preexisting `codec_irq_service` source projection to `g2/components/audio/uart_irq_source_candidate/irq_service.c`. It compiles as Cortex-M55 ELF EABI with six unresolved typed child imports. The prior fixture's 360/360 stock/source cases cut those children; this round adds no new behavioral oracle. The object is not admitted to the selected archive.
- The 13 unclosed active power branch families in the prior power ledger still include GPU mode/clock ownership, CRYPTO NVM idle, OTP PTM/revision, DEBUG trace MMIO, other audio domains, other shared groups, and composed elapsed-time delay. The existing power fixture returns an explicit sentinel outside proved paths, so it cannot be turned into a full provider by renaming it. Pinned generic Ambiq source identifies the APIs, but product callback/state and branch mapping are not fully attributable.
- The GX8002 retained result remains ten C-SKY DSP C units compiled and linked with zero undefined symbols, but zero of five selected C sections byte-equal stock; seven assembly sources produce nine exact sections. No new DSP unit or product source was found in this pass.

## Completion flags

| Lane | C candidate compiled | Target image linked | Byte-equal firmware |
| --- | --- | --- | --- |
| Apollo UART IRQ | yes, Cortex-M55 | no, six child contracts | no |
| EM9305 queue | yes, 32-bit ARMv4T host ABI model | no ARC compiler/port/config | no |
| GX8002 DSP | prior ten C-SKY units | standalone library only | no |

## Remaining minimum contracts

Apollo UART IRQ has **six** named lower imports plus callback/MMIO composition. Apollo power has **13** active branch families, representing at least the seven unresolved power aliases in the audio archive; a reliable duration is unavailable without product state and time oracles. EM9305 has at least the producing ARC port/config, compiler/runtime, product application callbacks/data, EM-Core/Packetcraft controller sources or qualified libraries, and linker/record placement; the queue unit is only 24 stock bytes of a 210,888-byte application record. GX8002 still lacks product application/configuration and private driver/speech source, ROM/API contracts and placement. These are source/data/tool gates, not tasks completed by synthetic stubs.

No official blob, canonical gate, image package, selected source archive, or flash output changed. Generated candidate objects are isolated in this analysis directory.

## Continued source implementation

- Added the full generic Ambiq power enable/disable branch graph as an
  experimental C unit (`power_vendor_candidate/power.c`), compiled for
  Cortex-M55 EABI. It preserves 15 external product/lower contracts rather
  than inventing an enum, MMIO address or callback implementation. Known
  stock divergence in SPOT callback failure handling and product domain
  indices is recorded in the component README. The prior 96 power cases do
  not validate this full unit.
- Added two firmware-specific GX8002 app helper bodies at XIP child
  `0x1020975c` and `0x10209770`, with their actual typed lower call ABI and
  28-byte request field layout. Retained GCC 6.3.0 built the C unit for
  `ck804ef` hard-float. Product global and lower consumer semantics remain
  unresolved; no runtime oracle or final placement is claimed.
- Repaired Audio builder archive exclusions to match stable object suffixes
  rather than source-list numeric indices. Fresh builder run compiled 113
  admitted audio and 94 provider/foundation units and selected 160 archive
  members; `arm-none-eabi-nm` found zero duplicate strong global definitions.
  The experimental power/UART directories are excluded from the selected
  archive glob. Root separately ran the combined Apollo link/collision check.

## UART child composition

All six lower names of `codec_irq_service` now have experimental C definitions:
three pinned/stock-corrected DMA and error helpers, RX abort, read state
machine, and a TX bridge to selected source. RX FIFO and TX static functions
require isolated inclusion of their selected translation units; these bridge
objects are mutually exclusive with ordinary archive members. The isolated
Cortex-M55 partial link succeeds. Its only remaining imports are
`am_hal_queue_init`, `am_hal_queue_item_add`, `am_hal_queue_item_get`, and
`audio_delay_us`, each defined in the admitted 160-member archive. This is
source-level symbol composition, not a complete original/source IRQ oracle,
real interrupt delivery, or a flashable image.

## Deterministic UART link receipt

`g2/components/audio/uart_irq_source_candidate/build_experimental.py` now
compiles the eight source files and runs `arm-none-eabi-ld -r`. RX/TX bridge
public symbols are locally namespaced; static state-machine bodies retain
their source implementation. A fresh whole-archive link against the admitted
160-member Audio archive passes with **zero multiple definitions**. The
standalone IRQ object has five imports (`am_hal_queue_init`, item add/get,
`am_hal_uart_fifo_read`, `audio_delay_us`), all resolved by the Audio archive.
The resulting combined object has **53 undefined names**, the existing
Audio frontier, with no new IRQ child import. Full source/object/archive
hashes and exact unresolved list are in `uart-build/receipt.json`. The root
Apollo+Audio object available during this check predates the experimental
directory exclusion and still contains `codec_irq_service`; relinking that
stale object produces a duplicate, so it must be regenerated before a valid
three-way link check.

## Scheduler delay candidate and ARC tool availability

Added an experimental source-backed CMSIS `osDelay` plus FreeRTOS
`vTaskDelay` composition with three same-entry caller aliases:
`audio_delay`, `codec_delay`, and `codec_delay_tick`. Cortex-M55 compilation
and relocatable links against both the admitted 160-member Audio archive and
root's fresh Apollo candidate pass without duplicate symbols. Against Audio,
undefined names decrease **53 to 51**; the remaining new import is the
noreturn product assertion for a suspended scheduler. This retains the
actual 33 and `UINT32_MAX` tick paths rather than replacing them with a
success return. The candidate is outside the selected Audio builder and
awaits a joint original/source scheduler-state oracle before admission.

A local tool search found no `ccac`, `arac`, ARC GCC or ARC-target Clang on
PATH, in `g2/build`, retained local-vendor paths, Homebrew/local bin, or
installed Docker image names. ARC objdump/disassembly remains available;
this search is not proof that no installable ARC toolchain exists. The EM9305
queue candidate therefore remains a 32-bit host-ABI model, not a target
compile. Minimum ARC gate is a qualified EM7D compiler with the required
port/config and runtime; availability/acquisition duration is unknown.

The remaining Audio graph after the experimental delay composition is **51
undefined names**, including one new assertion contract. This is a link
count, not 51 independent source bodies: several names are same-entry aliases.
Power's 13 active branch families, timer/daemon scheduler state, file pool
and logger bodies still need source and joint oracles. A reliable completion
time estimate cannot be derived from this count; the earlier bounded power
fixture alone was estimated at multiple focused days and has not yielded a
complete product binding.

## Fresh delay and classify oracles

`verify_delay_bounded.py` passes **64/64** locked-stock/source comparisons
for Apollo `osDelay` across ISR, PRIMASK, BASEPRI, ticks 0/1/33/UINT32_MAX,
and controlled resume outcomes. The selected source IRQ-context, suspend, and
yield bodies run; delayed-list insertion and resume are named child cuts with
observed ABI arguments. Results compare public status, ordered child events,
selected memory writes, suspension count and SP. This is a meaningful outer
entry oracle, but does not compose the delayed-list/resume children or the
suspended-scheduler fatal path. See `delay-oracle-results.json`.

The retained `audio_platform_classify` C body was compared against the
hard-float stock entry `0x5a1e8c`: **24/24** finite/boundary/Inf/NaN bit
patterns return the same range. A separate **24/24** check compares the
stock S0 ABI to an experimental softfp R0 wrapper that calls the selected C
body. This resolves the historical direct-alias ABI concern for this bounded
entry, with FPSCR and full platform callback integration still open. See
`classify-oracle-results.json` and `classify-adapter-results.json`. The new
adapter compiles as Cortex-M55 and links with root's fresh combined Apollo
candidate with no duplicate symbol. Linking that candidate plus delay and
classify candidates reduces unresolved names **88 to 85**; the new
`audio_delay_scheduler_assert` product fatal contract remains.

Both units remain experimental and outside the admitted Audio builder.
Their source-supported behavior advances the candidate graph but does not
close the remaining image, hardware, or byte-equality gates.

## Main logger runtime helper chunk

Added isolated `extended_log_runtime_candidate/runtime.c` and `locks.c`.
Cortex-M55 compilation and `ld -r` against root's current Apollo candidate
pass with no duplicate definitions. The three register/fatal helpers reduce
root undefined names **85 to 82**; the two lock wrappers reduce **82 to 80**
using the already selected Audio mutex acquire/release definitions. The
selected Main archive is unchanged.

`verify_log_runtime.py` passes **24** CONTROL/IPSR architectural combinations:
`g2_log_is_privileged() ? (g2_log_exception_number() & 0x1ff) : 0` equals the
stock outer logger's direct IPSR check. This is an expression oracle because
stock has no separate privilege helper entry. It also passes **four** stock
fatal-prefix comparisons at `0x44ab24`, matching the first AIRCR write over
initial register values 0, 0x700, 0xffffffff and 0x12345678. Execution stops
before hardware reset and the nonreturning loop.

`verify_log_locks.py` passes **24** stock/source wrapper comparisons for
enter/exit, null/nonzero/tagged handles and three controlled child returns.
It compares the CMSIS mutex child ABI, observed events, SP and mutex cell.
The nested mutex implementation and real concurrency are outside this test.
`log-runtime-results.json` and `log-locks-results.json` carry hashes/cases.

## Main logger transport outer entries and exact lower frontier

`extended_log_runtime_candidate/transport.c` now supplies stock-derived
`g2_log_transport_submit` (`0x448d4e`) and `g2_log_transport_signal`
(`0x4495e4`). `event_get.c` supplies the selected `xEventGroupGetBits`-shape
child (`0x47ed64`). All three compile for Cortex-M55 with warnings as errors.
The linked current Apollo candidate has no duplicate strong definitions.
Against the pre-transport candidate's 80 undefined names, submit/signal
first resolve two names and expose eight typed lower/data names; event-get
then resolves one, leaving **85** undefined names in the whole image. This
is a graph count, not a count of absent independent source bodies.

The bounded original/source comparisons pass **34/34** submit cases
(enable, zero/nonnull source, length boundaries, default level, allocation
and enqueue outcomes), **8/8** signal cases (invalid arguments, task and ISR
paths, PendSV), and **16/16** event-get cases (BASEPRI and bits variants).
Submit executes stock `memcpy`; its allocator/queue/fatal children are named
cuts. Signal cuts event-group mutation children. Event-get executes the
selected `audio_mask_save/restore` source. Results are in
`log-submit-results.json`, `log-signal-results.json`, and
`log-event-get-results.json`; these do not establish queue delivery or
concurrency equivalence.

The exact seven new imports are:

| Import | Stock address / typed contract | Missing composition |
| --- | --- | --- |
| `g2_log_transport_node_allocate` | `0x448a0c`; returns writable node of at least 269 bytes or null | free-list CAS using head cell `0x20074574`, stats `0x2007342c`, pool ownership and initialization |
| `g2_log_transport_node_enqueue` | `0x448af0`; accepts node, returns zero on failure | pending-head CAS at `0x2007413c`, stats and consumer coordination |
| `g2_log_transport_node_free` | `0x448a8e`; accepts node | free-list CAS and ownership |
| `g2_log_transport_queue_failure` | `0x4733ee`; accepts message pointer | diagnostic/fatal body and its dependencies; cannot return inert success |
| `g2_log_transport_queue_failure_message` | stock literal points to `0x71e990`; string address | product data/string provenance and placement |
| `g2_log_event_set_task` | `0x47ed76`; handle and 24-bit event bits, returns updated bits | FreeRTOS event-group waiter list, scheduler and task notification path |
| `g2_log_event_set_isr` | `0x47ee4a`; handle/bits/woken pointer, returns success flag | FreeRTOS deferred daemon queue and wakeup path |

The retained queue pseudocode identifies atomic read/CAS and node flag/next
children at `0x448938`, `0x448940`, `0x4488ec`, `0x448930`, with bounded
retry loops. Those child ABIs, pool node layout and producer/consumer
concurrency are not yet composed as C. The product data cells are enabled
byte `0x20074fc0`, default-level byte `0x20004546`, event-handle cell
`0x20074570`, free head `0x20074574`, pending head `0x2007413c`, and stats
`0x2007342c`. Initial values, pool capacity and event-handle creation are
still missing. A node requires 13 header bytes plus at most 255 payload
bytes and a NUL terminator, hence **269 writable bytes**. These data
requirements prevent an honest completed firmware link even though the
outer transport entries are implemented and bounded-tested.

## Queue node and event setter C composition

The three node children are now implemented in
`extended_log_runtime_candidate/transport_queue.c`. The source preserves the
stock 1000-attempt free-list and 10000-attempt pending-queue bounds, node
state transitions 0/1/2, atomic head/next compare-exchange and stock stats
offsets. Node offsets are next 0, state 4, length 8, level 10, mode 12,
payload 13. The C type has a 272-byte stride with 269 useful bytes.
`verify_log_queue.py` passes **4/4** original/source uncontended transitions:
empty allocation, one-node allocation, free to empty head, and enqueue to
initialized sentinel. It compares result, heads, links, state, and twelve
stats words. It does not cover CAS contention, producer/consumer races,
failure retries, queue initialization, or node lifetime; the candidate is
experimental.

`event_set.c` binds task and ISR event-set contracts to the retained pinned
FreeRTOS V10.5.1 `event_groups_subset.c` and `timer_pend_subset.c` bodies.
Those implement waiter-list traversal, clear-on-exit, deferred ISR daemon
command and the 16-byte message. Both source bodies and the adapters compile
for Cortex-M55 with warnings as errors. Linking them and `transport_queue.c`
with the current Apollo candidate and earlier logger helpers passes with no
duplicate strong symbols. Whole candidate undefined names change **85→83**.
The direct frontier is now product failure handler and its message, plus
`vTaskSuspendAll`, `xTaskResumeAll`, and
`vTaskRemoveFromUnorderedEventList` needed by the event setter. The selected
Apollo graph already provides `opencfw_event_queue_send_isr`. The selected
Audio scheduler children may supply the first two through ABI adapters, but
no joint event-group scheduler/list oracle has established those bindings.
The message at `0x71e990`, initialized pool/free head, pending sentinel and
event-group handle still require product data provenance. No target image or
hardware completion follows from this compilation and bounded oracle.

The selected Audio `audio_suspend` and `stock_scheduler_resume` providers
correspond to stock `0x454d7c` and `0x454dcc`; the new
`event_scheduler_adapters.c` binds the pinned event-group API to these typed
entries. Cortex-M55 compilation and integrated `ld -r` pass, reducing
undefined names **83→81** without duplicate symbols. This leaves exactly
three direct logger-transport imports: `g2_log_transport_queue_failure`,
`g2_log_transport_queue_failure_message`, and
`vTaskRemoveFromUnorderedEventList`. The last stock child is `0x45547c`;
its waiter-list removal and task ready-list effects are not yet C-composed.

`event_unblock.c` now composes this last child from the pinned FreeRTOS
algorithm and selected `uxListRemove`, `vListInsertEnd`, and
`audio_resume_next_unblock` source providers. Its stock entry is `0x45547c`.
`verify_log_unblock.py` passes **4/4** bounded original/source initialized
waiter transitions, comparing event/delayed/ready list links and counts,
TCB item value, top ready priority, yield flag, and the next-unblock child
call. That child is cut; multiwaiter scheduling and invalid-state assertion
paths remain untested. Cortex-M55 Werror compile plus integrated `ld -r`
passes without duplicates; undefined names **81→80**. Exactly two direct
logger transport imports now remain: product queue failure handler and its
message string. The whole Apollo candidate still has 80 undefined names,
and the logger's product queue/event initialization remains unresolved.

## Authenticated failure output and queue initialization

Stock literal `0x448fd0` points to `0x71e990`, whose NUL-terminated bytes are
`error!!!!!!elog_async_ext_output: enqueue_log failed\n`. The new
`transport_failure.c` defines that exact string and the `0x4733ee` variadic
wrapper. Its callback cell is `0x200742f0`, output buffer `0x2006b930`, and
the formatter call goes to stock `0x473036`. The formatter is retained as a
typed C import `g2_log_transport_vformat_unbounded`; no format implementation
is guessed. `verify_log_failure.py` passes **3/3** original/source cases for
callback absent/present, argument save area, buffer/format ABI, callback order
and return. Formatter/callback bodies are named child cuts.

The retained initialization entries `0x44895e`, `0x4489e8`, and `0x448c74`
are now in `transport_init.c`. Original literals prove pool base
`0x202d3fc8`, 272-byte stride, 254 chained free nodes, node 254 terminal,
node 255 pending sentinel at `0x202e4eb8`, free head `0x20074574`, pending
head/tail `0x20074138/0x2007413c`, 48-byte stats region `0x2007342c`,
default-level byte `0x20004546`, and enabled byte `0x20074fc0`. The source
zeroes and publishes exactly those cells. `verify_log_init.py` passes **2/2**
original/source tests for disabled and already-enabled entry, comparing the
complete 256-node pool hash and all mentioned cells. The source does not
invent a product pool count or sentinel address. It still needs an actual
boot-order caller and concurrency analysis for production.

Both new files compile for Cortex-M55 with warnings as errors and link with
the current Apollo candidate and preceding logger units without duplicate
symbols. Whole candidate undefined names **80→79**. The sole direct
transport import is now the stock `0x473036` unbounded formatter body. The
whole firmware still has substantial source/data/target-link work; these
bounded source comparisons do not establish a flashable image.

The fresh integrated `nm -u` census has **79 symbolic imports** grouped by
name: 31 Audio/receiver/UART, 23 power/platform, 9 logging, 7 flash/FAL,
4 codec, and 5 other kernel/runtime. This grouping is a planning aid only:
aliases may collapse to one body, while one imported body may require many
dependencies and product data. Concrete whole-body C still needed includes
the unbounded transport formatter `0x473036`, Main bounded formatter
`g2_log_vformat`, Audio event/thread/daemon/file/I2S/power controls,
platform power calls across 13 active branch families, and codec allocation
and voltage callbacks. Product tables/strings and hardware initialization
are distinct from those bodies. The current `ld -r` is a partial ARM object
link, with no final placement, startup closure, ARC/codec target image, or
physical G2 execution.

## Pinned Main formatter composition

The existing selected `audio_heap_formatter` body in
`audio/main_formatter_offline/format.c` is the Ambiq utility adaptation whose
authenticated Main entry is stock `0x473036..0x4733ee`. Its interface is
`(char *destination,const char *format,va_list)` on ARM32. The prior
`audio-main-formatter-source-successor-2026-10-09` receipt passes **88**
original/source cases across literal, integer, string, long-long, finite
float, and selected log paths. `transport_formatter_adapter.c` binds
`g2_log_transport_vformat_unbounded` to this selected C body. The Main
FlashDB print wrapper passes the same three R0–R2 words to stock `0x473036`;
the same file provides `g2_flashdb_vformat` with its existing integer-word
prototype. A Cortex-M55 ABI check shows **one direct `R_ARM_THM_JUMP24` branch
to `audio_heap_formatter` for each adapter**, with no argument reshuffle.
The combined partial link passes without duplicate symbols; undefined names
drop **79→77**. No arbitrary-float or complete printf grammar claim follows
from the 88 fixtures; malformed formats, capacity, callback registration,
and physical output remain separate. The four-argument capacity-bearing
`g2_log_vformat` targets Main `0x44b76c` and cannot share this direct ABI
adapter without its own formatter proof.

`main/full_formatter_outer_candidate/vformat.c` now implements that stock
`0x44b76c` capacity-bearing outer body and its stock `0x439c8a` output
callback. It preserves the ARM32 argument cursor, increments the unbounded
output count, writes at most `capacity-1` bytes, terminates when capacity is
nonzero, and returns the formatter's negative result on failure. Its
original-byte/compiled-C oracle passes **24/24** bounded callback and
wrapper cases with the core cut. The general IAR formatter at stock
`0x481836` (3256 bytes) remains a typed `g2_iar_general_format` import;
this is not full `%` grammar or floating-point source coverage. The
Bootloader IAR engine has a similar interface but a distinct stock body,
so an alias is not yet justified.

The later Main formatter candidate adds `general_format.c`,
`float_bridge.c`, `float_render.c`, and `fp_primitives.c` beside the
outer wrapper. This is an independent `g2_iar_general_format` C body:
it parses flags, dynamic width/precision and length modifiers, consumes
ARM32 argument words, emits integer/string/character/`%n` results through
the actual callback ABI, and dispatches floating formatting into a
separate record renderer. The float renderer is adapted from the
repo's pinned IAR Bootloader source reconstruction with the Main
`0x20004488+0x24` locale slot and Main VFP helper operations; its
cross-image equivalence is an experimental hypothesis. All five Main
formatter units compile for Cortex-M55 with warnings as errors and
partial-link with only the compiler's `__aeabi_memclr4` import. The
stock-byte/source nonfloating oracle passes **27/27** literal, integer,
string, width, precision and mixed cases. The first `%f` stock oracle
reaches a native VFP helper at `0x4d435c` that Unicorn's available
Cortex-M7 model rejects as an invalid instruction. Floating grammar,
large precisions, secure-format failure callbacks and whole-image
behavior remain unqualified. The candidate should not replace the
selected production formatter until that comparison is resolved.

A stronger separate native candidate now lives in
`main/full_formatter_native_candidate`. Its seven engine/parser/integer/
floating C units adapt the pinned IAR model only after a deterministic
instruction comparison: the Main `0x481836` and Boot `0x41e47a` cores each
contain **1270 Thumb instructions at identical relative offsets**;
the **23** differing instructions are all `BL` calls to corresponding
Main lower targets. The cores share **3188/3256** raw bytes. The private
double-precision helper island is **110/110 bytes identical**; the
emitter is **46/46 bytes identical**. The integer renderer has only two
relocated division-helper calls among its 114 instructions. The mapping
and source hashes are reproducible with
`verify_main_formatter_structural.py` and
`main-formatter-structural.json`.

Main-specific product state is explicit: constraint-handler pointer
cell `0x20074f10`, decimal separator pointer cell `0x200044ac`.
`termination.c` follows the decoded stock `0x541b74→0x585120`
semihosting exit path; `memclr4.c` implements the actual ARM EABI zeroing
effect. All **nine** native candidate C units and the separate
`vformat.c` compile for Cortex-M55 with softfp and warnings as errors;
their combined relocatable object has **zero undefined symbols** and no
duplicate definitions. The original-byte/source Main core oracle passes
**27/27** nonfloating cases with stock output callback and pinned data.
This proves those cases and a strong static operation correspondence,
not all grammar or float equality.

The floating execution checks have concrete emulator limits. Unicorn
rejects a stock VFP instruction at `0x4d435c`; an M55 QEMU harness
starts but reports an instruction-bus fault (`CFSR=0x100`) at the Main
stock entry `0x481836`, outside that board's executable memory map.
`verify_main_float_qemu.py` records this as
`SKIP_UNMAPPED_MAIN_STOCK`, not a pass. The native Main candidate stays
experimental until a mapped stock floating oracle or equivalent
qualified operation-level proof is available.

## Thread, event wait, and file close source round

Eight further experimental Cortex-M55 C translation units compile with
`-Wall -Wextra -Werror` and partially link with the preceding Main/Audio
candidate without duplicate definitions. `thread_new.c` implements the
stock `0x4490e2` CMSIS thread-create outer entry and dispatches to the
static/dynamic constructors. `dynamic_create.c` (`0x4548ba`) allocates the
stack and 0x70-byte TCB through selected heap providers; `static_create.c`
(`0x454820`) initializes caller storage. `schedule_tcb.c` (`0x4549fc`)
inserts the task into the ready list under the selected critical section,
and `list_init.c` (`0x45568c`) initializes 61 authenticated lists and the
delayed-list pointer cells. The full TCB initializer and assertion behavior
remain typed lower contracts. Bounded original/source comparisons pass
21/21, 12/12, 3/3 valid-path, 5/5, and 1/1 respectively. Invalid static
constructor inputs are outside the executed oracle and retain the original
nonreturning assertion contract.

`event_wait.c` implements the stock `0x44969c` CMSIS wait outer body with
the authenticated handle/mask/ISR checks and forwards the actual wait to
the typed `g2_event_wait_bits` FreeRTOS lower; 288/288 bounded stock/source
cases pass with that lower cut. `backend_close.c` implements the stock
`0x4cfad0` file close wrapper with typed lfs open/close and error callbacks;
4/4 bounded cases pass with those children cut. This does not validate
filesystem side effects or concurrent waiter behavior.

`bounded_formatter_adapter.c` exports only
`g2_log_vformat_bounded_candidate`, scanning the measured integer/string
syntax before invoking the selected bounded formatter. Unsupported syntax
dispatches to a returning, typed `g2_log_general_vformat` contract. This
candidate does **not** define the stock `g2_log_vformat` symbol or complete
its general-format behavior. The fresh partial object has **79 undefined
names** versus 77 before this round, because source-defined outer bodies
expose child implementations and data; this is not a source-completeness
percentage. The Audio selected-archive builder excludes all three new Audio
candidate directories by stable path and still selects 113 baseline source
files, preventing duplicate inclusion with the root experimental manifest.

## Newly exposed lower source bodies

`mlist_isopen.c` implements the complete stock `0x4cb082` LittleFS open-list
membership loop. A ten-case stock/source execution oracle covers null,
head, middle, tail and absent nodes. `file_close.c` implements stock
`0x4cdce4`: sync, remove from the open list, conditionally free the cache,
and return the sync result. Four stock/source cases compare the ordered
lower ABI calls and return with children cut. The new typed contracts are
`g2_lfs_file_sync`, `g2_lfs_mlist_remove`, and `g2_lfs_free`.

`wait_bits.c` implements the pinned FreeRTOS event-group wait algorithm at
stock `0x47ebf8`, including the ready, zero-timeout, blocked, resumed, and
control-bit paths. Its Cortex-M55 source compiles and partially links.
Ready and zero-timeout paths pass **20/20** stock/source executions with
selected scheduler calls cut; blocked-list placement and postresume task
paths remain unvalidated. Typed task-list/item/assertion lowers are explicit.

`initialize_tcb.c` implements stock `0x454938` TCB setup, including the
0xa5 stack fill through a selected equivalent provider, 8-byte top
alignment, 32-byte task name, priority/list item fields and port stack
initialization. Nine stock/source cases pass with stack-fill and port
stack child effects cut. All four new files compile for Cortex-M55 with
warnings as errors and link with the previous integrated candidate without
duplicate definitions. The local partial link has **82 unresolved names**:
new whole bodies expose their own lower dependencies, rather than
completing the image. The firmware-specific port stack initializer,
event-list task transition, LittleFS sync/remove/free and semihost error
delivery still require source/data/hardware qualification. Stock file-error
entry `0x4d09b4` uses semihost BKPT 0xAB and a failure child; no synthetic
trap or success implementation has been added.

Two more LittleFS lowers are source-defined. `mlist_remove.c` is the
stock `0x4cb0a0` unlink loop, with **10/10** bounded original/source list
transition comparisons. `lfs_free.c` is the stock `0x4ca812` one-call
wrapper to the exact unresolved `audio_file_heap_free` entry `0x474d16`;
the Cortex-M55 object emits one Thumb branch relocation to that provider.
This does not implement the mutex-protected file-pool free body. Both C
objects compile with warnings as errors. The local partial link including
all six lower-pass files has **80 unresolved names**, down from 82 after
the first four; no duplicate definitions were reported.

`initialize_stack.c` now implements the complete 18-word initial Cortex-M
task frame at stock `0x44215a`. The authenticated task-return PC is
`0x44207d`; the frame includes xPSR, entry/argument words, callee register
markers, exception return and stack base. **8/8** bounded original/source
frame comparisons pass over synthetic aligned stacks. Cortex-M55 Werror
compile and combined partial link pass. The seven-file lower round leaves
**79 unresolved names** in the local integrated object, with no duplicate
definitions. The remaining direct lowers from these bodies are event task
placement/reset/assertion, LittleFS sync and semihost error delivery, the
mutex-protected file heap free, and thread assertion behavior. Neither a
full image link nor hardware scheduling/filesystem behavior is proven.

`reset_item_value.c` now reduces stock `0x455aca`: it returns the current
task's old event-list item word and restores its value to 56 minus task
priority. The current-task cell and TCB offsets are authenticated.
**12/12** bounded stock/source cases pass for three priorities and four
old values. Cortex-M55 Werror compile and partial link pass; the eight-file
lower round now leaves **78 unresolved names** in this local candidate.

`place_unordered.c` implements stock `0x4552ae`: under suspended scheduler,
it marks the current TCB's event item, inserts it before the indexed list
node, increments the list length and delegates delayed-task placement to
the selected `audio_block_ticks` API. **9/9** bounded original/source
single-list transitions compare list/TCB bytes and child ABI. The invalid
list and unsuspended-scheduler paths keep a typed assertion contract and
were not executed. Cortex-M55 Werror compile and partial link pass;
symbolic unresolved count remains **78** because one event-place contract
was exchanged for one assertion contract.

The next Audio file heap and LittleFS pass adds two more experimental
translation units. `file_heap_free_candidate/file_heap_free.c` implements
the stock `0x474d16` mutex-owned free wrapper, using the authenticated
mutex/pool RAM cells and selected mutex acquire/release providers. It
retains typed pool-free, failure-log and semihost diagnostic children.
**6/6** bounded stock/source cases cover acquisition success/failure and
null/non-null buffers; child effects remain cut. `file_sync_candidate/file_sync.c`
implements stock `0x4cdf74` LittleFS sync, including file-error/dirty/inline
flags, flush, pair-null check, block sync, CTZ versus inline metadata tags,
dir commit and error propagation. **20/20** bounded original/source cases
compare return, flag writes, ordered lower calls and metadata tags, while
normalizing only temporary stack addresses; disk and allocation effects are
cut. Both compile for Cortex-M55 with warnings as errors. The local
partial link has **83 unresolved names** because these whole bodies expose
their real nested filesystem and allocator dependencies. Audio's selected
archive builder excludes both new directories by stable path and still
selects 113 baseline C files.

`file_pool_free_candidate/pool_free.c` implements the stock `0x4d0808`
TLSF outer free composition from the pinned allocator: null guard,
block-from-pointer, already-free diagnostic, mark-free, previous/next
coalescing, and free-list insertion. The diagnostic string/file/line are
authenticated stock literals. **4/4** bounded stock/source call-ABI cases
pass with TLSF helper and semihost diagnostic effects cut. It compiles for
Cortex-M55 with warnings as errors and partially links without duplicates.
The local unresolved list rises to **88** as the body exposes six real
TLSF helper contracts. The selected Audio builder excludes the new
candidate directory by stable path.

Further post-snapshot helpers reduce TLSF and LittleFS leaves. `tlsf_leaf.c`
implements `block_from_ptr` at `0x4cfe04` and `block_is_free` at
`0x4cfdb4`, using the authenticated TLSF configuration-word addresses;
**48/48** controlled original/source cases pass. `tlsf_mark_free.c`
implements stock `0x4cfe96` block/next flags and physical backlink;
**6/6** cases pass with block-next cut. `tlsf_block_next.c` implements
stock `0x4cfe44` physical neighbor calculation and last-block diagnostic;
**8/8** cases pass with semihost diagnostic cut. `file_sync_leaves.c`
implements stock `0x4cadd0` pair-null and `0x4cb000` CTZ little-endian
conversion; **10/10** cases pass. All four files compile for Cortex-M55
with warnings as errors and partially link without duplicate definitions.
The local unresolved count drops from **88 to 83** after these helpers.

`file_sync_candidate/bd_sync.c` reduces stock `0x4cabbc` LittleFS
block-device sync: flush the read cache, program the pending cache, invoke
the configured device sync callback at config offset `0x10`, and preserve
the authenticated positive-error diagnostic. **12/12** bounded
original/source cases match ordered child ABI and return with the lower
effects cut. It compiles for Cortex-M55 with warnings as errors and
partially links without duplicates. The local import count becomes **84**
because two deeper block-device operations are now explicit contracts.

`tlsf_merge.c` implements stock `0x4d02d6/0x4d033a` previous/next
coalescing outer bodies, with their real diagnostic strings and child
contracts; **4/4** bounded ABI comparisons pass. `tlsf_merge_leaves.c`
adds previous-free, last-block, and physical-predecessor checks at stock
`0x4cfddc`, `0x4cfda0`, and `0x4cfe1e`; **18/18** cases pass. `tlsf_absorb.c`
implements stock `0x4d0294` block size absorption and relink; **8/8**
cases pass with size/link children cut. These C units compile for
Cortex-M55 with warnings as errors.

`semihost_error_candidate/error.c` now represents actual stock `0x4d09b4`
and fatal `0x541b74→0x585120` architectural behavior: BKPT `0xab` with
R0 operation 24, R1 selector `0x21010`, and R2 pointing to the ordered
file/line/message words. A zero result enters the repeated BKPT SYS_EXIT
`0x20026` path. **3/3** bounded original/source cases intercept the BKPT
and compare both return and fatal-prefix transitions. This is the decoded
semihost contract, not a fabricated panic stub; no physical debugger or
hardware reset behavior has been tested. The Audio selected builder excludes
the experimental semihost directory by stable path. A local partial link
including these units has **84 unresolved names**, with no duplicates.

`assert_failure.c` defines the shared source form of stock FreeRTOS
assertion failure: selected BASEPRI-save call, volatile zero write to
`0xffffffff`, and the infinite tail. It resolves three typed assertion
imports and passes one bounded stock/source invalid-event-wait prefix
comparison through the attempted write. This is not a success stub; the
physical fault is not executed. `tlsf_absorb_leaves.c` adds block size
and physical-next-link helpers at stock `0x4cfd70/0x4cfe88` (**12/12**
bounded cases). `tlsf_lists.c` adds size-class remove/insert wrappers at
stock `0x4d0178/0x4d019a` (**6/6** cases with list mutations cut). All
compile for Cortex-M55 with warnings as errors and partially link with
no duplicate definitions. The latest local unresolved count is **80**;
the new TLSF list mutation and mapping helpers remain real lower work.

`tlsf_mapping.c` now implements the authenticated `0x4cfd66/0x4cff6c`
bit-index and size-class mapping, using the pinned TLSF geometry (128-byte
small-block threshold, 32 second-level bins). The retained original-byte
Unicorn mapping oracle passes **3,560/3,560** size cases. `tlsf_free_lists.c`
implements stock `0x4d003a/0x4d00d0` list removal/insertion with the
authenticated pool layout: null sentinel at pool base, FL bitmap at
offset `0x10`, SL bitmap at `0x14+4*fl`, heads at `0x74+128*fl+4*sl`,
and block next/prev at offsets `8/12`. Its assertion diagnostics use
literal addresses read from the authenticated stock literal pool and
the real semihost call. `tlsf_align.c` implements stock `0x4cfe10` block
payload pointer and `0x4cff18` pointer alignment, using the actual
configuration word at `0x78f4c0`. A new original/source Unicorn oracle
`verify_tlsf_free_lists.py` passes **15/15** insert/remove transitions,
including head/non-head, empty/nonempty, and bitmap updates. The three
new units compile for Cortex-M55 with warnings as errors and partially
link with no duplicate definitions; local unresolved count is **77**.
The oracle covers valid bounded transitions, not malformed allocator
state, all possible indices, or a complete firmware image.

`file_sync_candidate/cache_drop.c` closes the stock `0x4ca81a` leaf:
it writes `LFS_BLOCK_NULL` (`UINT32_MAX`) to the cache's first word.
Pinned LittleFS and direct disassembly identify the body as
`lfs_cache_drop`; the C symbol is now `g2_lfs_cache_drop`, and its
caller has been updated. It compiles for Cortex-M55 with
warnings as errors; local partial link is duplicate-free with **76**
unresolved names. The actual block-device program/flush lower at
`0x4caafa` remains open.

`file_sync_candidate/bd_flush.c` now reduces that stock `0x4caafa`
body, corresponding to pinned LittleFS `lfs_bd_flush`: it rejects null
and inline blocks, checks the filesystem block bound, rounds program
length, calls the configured program callback, optionally invalidates
the read cache and compares written bytes, then zeroes the program
cache. Its C symbol is now `g2_lfs_bd_flush`, matching the pinned
source attribution and the updated caller. Original-byte
and compiled-C child ABI/return oracle passes **36/36** bounded cases
over cache states, validation flags, callback errors, and compare
results. `bd_flush_leaves.c` adds stock `0x4ca708/0x4ca714`
align-down/up and `0x4ca822` cache zero; `cache_fill.c` implements the
actual reverse-fill byte behavior of stock `0x43c0e4`. Their original/C
oracle passes **63/63** bounded sizes and cache states. All three units
compile for Cortex-M55 with warnings as errors and link without
duplicate definitions. The local unresolved count is **76**, with the
full `g2_lfs_bd_cmp` lower body and other filesystem dependencies open.

`file_sync_candidate/bd_cmp.c` then reduces stock `0x4caa04` pinned
LittleFS `lfs_bd_cmp`: it reads and compares in eight-byte chunks and
maps a nonzero `memcmp` result to LittleFS compare codes 1 or 2.
Original-byte/compiled-C child ABI and return checks pass **24/24**
bounded cases, including zero-length, multi-chunk, read errors and
comparison signs. It compiles for Cortex-M55 with warnings as errors
and links without duplicate definitions. Its real `lfs_bd_read` and
`memcmp` child contracts increase the local unresolved count to **77**.

`file_sync_candidate/byte_compare.c` now supplies stock `0x4751c8`
memcmp behavior, preserving the source body distinction between exact
byte subtraction on unaligned paths and sign-only results for differing
aligned words. An original-byte/compiled-C exact-return oracle passes
**640/640** cases over all four address alignments, ten lengths and four
mismatch variants. It compiles for Cortex-M55 with warnings as errors
and reduces the local unresolved count to **76** without duplicates.

`file_sync_candidate/bd_read.c` reduces the pinned LittleFS `lfs_bd_read`
body at stock `0x4ca83c`: program-cache priority, read-cache hits,
direct block callback, and cache refill are all represented, with the
observed filesystem/config/cache offsets and authenticated diagnostic
literals. Original-byte/compiled-C bounded state-machine comparison
passes **40/40** cases across the four cache paths, five sizes, and
callback success/error. It checks ordered child calls, cache state,
output bytes, and return value. The source compiles for Cortex-M55 with
warnings as errors and partially links without duplicates. Local import
count remains **76** because the whole-body read replacement exposes a
real `memcpy` lower contract. This oracle does not exhaust all read
offsets, wraparound inputs, or concurrent cache mutation.

`file_sync_candidate/byte_copy.c` supplies the forward-copy memory
effects consumed by `bd_read` from stock `0x439be4`. The original
optimized assembly leaves a path-dependent incidental R0 value, while
the observed LittleFS caller discards R0. The C function therefore has
`void` return and is qualified only for this caller contract. An
original-byte/compiled-C oracle compares destination bytes for
**256/256** lengths/address alignments. The source compiles for
Cortex-M55 with warnings as errors. The block-cache trio now exports
source-matched names `g2_lfs_cache_drop`, `g2_lfs_bd_flush`, and
`g2_lfs_bd_sync`; both prior sync/flush bounded oracles pass after the
rename. This naming correction does not change stock address mapping.

`file_sync_candidate/file_flush.c` now reduces stock `0x4cde54` from
the pinned LittleFS `lfs_file_flush` body: reading cache drop, inline
position normalization, noninline byte copy through flushed-read/write,
program-cache flush with corruption relocation, and final metadata
updates. The source uses the decoded file offsets and the authenticated
read-only template value, expressed as C initialization. It keeps the
actual relocation debug call as a typed lower contract. Original-byte/
compiled-C state and child-call oracle passes **30/30** bounded cases
over read/write modes, copy/no-copy paths, and flush success/errors.
It compiles for Cortex-M55 with warnings as errors. The deeper
flushed-read/write, relocation, and debug logging bodies remain open.

`file_sync_candidate/file_flushedread.c` now reduces stock `0x4ce042`
from the pinned LittleFS source: EOF/size clamp, ctz lookup or inline
block setup, inline directory or block-device reads, and position/offset
updates. Its typed lower calls expose real ctz and directory-read
work. Original-byte/compiled-C child ABI and file-state comparison
passes **24/24** bounded cases over inline, already-reading and ctz
paths, short reads, EOF, and child errors. The unit compiles for
Cortex-M55 with warnings as errors.

`file_sync_candidate/file_flushedwrite.c` reduces stock `0x4ce1a0`
from pinned LittleFS: inline outline threshold, ctz lookup and
extension, cache zero, programmed writes, corrupt-block relocation,
and file flag/position updates. Original-byte/compiled-C child ABI
and state comparison passes **24/24** bounded cases over inline,
already-writing and new noninline paths with success/error results.
The unit compiles for Cortex-M55 with warnings as errors. Its ctz,
block-program, outline, and allocation-checkpoint children remain
real lower work.

`file_sync_candidate/alloc_checkpoint.c` closes stock `0x4cb0e0` by
copying the filesystem block count into the allocation checkpoint;
`file_outline.c` reduces stock `0x4cde2c` position-to-offset,
checkpoint, relocate, and conditional inline-flag clear. Original/C
bounded state comparison passes **4/4** success/error transitions.
Both compile for Cortex-M55 with warnings as errors; relocation remains
a real lower body.

`file_sync_candidate/file_relocate.c` reduces stock `0x4cdd0e` using
the pinned LittleFS allocation/erase/read/program loop, cache transfer,
and file block/flag update. The corrupt-block path retains typed debug
logging with its authenticated source line and cache-drop retry.
Original-byte/compiled-C bounded child and state comparison passes
**12/12** zero/one-byte, inline/noninline, allocation/erase error cases.
The source compiles for Cortex-M55 with warnings as errors. Allocator,
erase/program, directory read, and debug formatter are deeper lowers.

`file_sync_candidate/bad_block_debug.c` binds the corrupt-block debug
call to the existing `g2_log_transport_queue_failure` wrapper. Its
format and LittleFS source-path literals were byte-checked against
authenticated stock addresses `0x754e54` and `0x70c264`; callers pass
the original source line 3329 or 3408 and the block number. It compiles
for Cortex-M55 with warnings as errors. Actual logger formatting and
output remain qualified by that wrapper's separate contracts.

`file_sync_candidate/bd_erase.c` closes stock `0x4cad2e` block-bound
assertion, configured erase callback at offset `0x0c`, and
positive-error diagnostic. Its diagnostic strings were authenticated
against stock literals. Original-byte/compiled-C callback and return
comparison passes **12/12** bounded in/out-of-range and callback-result
cases; it compiles for Cortex-M55 with warnings as errors.

`file_sync_candidate/bd_program.c` reduces stock `0x4cac04` cached
block programming from pinned LittleFS: bounds diagnostics, cache-hit
copy/occupied-size update, eager flush, and new cache alignment. An
original-byte/compiled-C child/state/byte oracle passes **16/16**
bounded hit/miss, size, and flush-error cases. It compiles for
Cortex-M55 with warnings as errors. The configured device write remains
inside the separately reduced `bd_flush` body.

`file_sync_candidate/alloc.c` reduces stock `0x4cb186` pinned LittleFS
lookahead allocation: free-bit scan, circular block selection, eager
next/checkpoint advance, scan refresh, and no-space return. Original/C
bounded bitmap/position/checkpoint state and return oracle passes
**25/25** cases with scan failure and no-space paths. It compiles for
Cortex-M55 with warnings as errors. The scan and no-space log bodies
remain deeper source work.

`file_sync_candidate/alloc_scan.c` now reduces stock `0x4cb0e6` drop,
`0x4cb0f6` lookahead visit, and `0x4cb12e` scan: it advances the
window, clears and marks the bitmap, traverses the filesystem and drops
the window on error. Original/C callback/scan state oracle passes
**23/23** bounded cases; the real filesystem traversal remains a lower.
`no_space_log.c` binds the allocator diagnostic to authenticated stock
format bytes at `0x74a5dc`, source path `0x70c264`, and line 706 via
the existing logger wrapper. Both units compile for Cortex-M55 with
warnings as errors. `cache_fill.c` now uses explicit volatile byte
stores to avoid introducing a compiler-generated `__aeabi_memset`
dependency; its **63/63** earlier cache oracle still passes.

`file_sync_candidate/ctz_index.c` and `ctz_find.c` reduce stock
`0x4cd6e4` and `0x4cd728`: pinned LittleFS block-index arithmetic and
CTZ link traversal through `bd_read`. Original/C offset, return and
child ABI oracle passes **25/25** bounded index and zero/single/
multi-block searches with read success/errors. Both units compile for
Cortex-M55 with warnings as errors.

`file_sync_candidate/ctz_extend.c` reduces stock `0x4cd7d2` from
pinned LittleFS: allocate/erase, empty file, incomplete last-block
copy, CTZ link append, and corruption retry with authenticated debug
line 3013. Original-byte/compiled-C child, result and output-block/
offset oracle passes **12/12** bounded size and lower-error cases.
It compiles for Cortex-M55 with warnings as errors. Full allocator,
directory traversal, and block-device runtime contracts still apply.

`file_sync_candidate/dir_getread.c` reduces stock `0x4cb3f0`
LittleFS inline directory read/cache behavior, including program/read
cache hits and directory-slice refill. Original-byte/compiled-C
state/byte/child-call oracle passes **30/30** bounded cache-path,
size, and slice-error cases. It compiles for Cortex-M55 with warnings
as errors. The actual `g2_lfs_dir_getslice` lower remains.

`file_sync_candidate/dir_getslice.c` reduces stock `0x4cb23a` pinned
LittleFS reverse metadata lookup, including synthetic move adjustment,
backward tag walk, splice/delete handling, slice read and trailing zero
fill. Original-byte/compiled-C bounded tag, child-call and output
oracle passes **32/32** no-tag, match/mismatch, output-length and
read-error cases. It compiles for Cortex-M55 with warnings as errors.
The global-state hasmovehere helper is now its direct lower.

`gstate_hasmovehere.c` reduces stock `0x4caf5c` with pinned LittleFS
tag-type and pair-overlap semantics; original-byte/compiled-C oracle
passes **90/90** bounded cases. `fs_traverse.c` and
`ctz_traverse.c` reduce stock `0x4cf284` and `0x4cd974` respectively:
metadata-pair, orphan, open-file, and CTZ block visitation with actual
callback and block-read effects. These three are source-defined,
target-compiled experimental candidates. `ctz_traverse.c` passes
**36/36** bounded original-byte/compiled-C callback, read ABI,
return and error cases. `fs_traverse.c` passes **6/6** bounded
original-byte/compiled-C first-pair callback and fetch-error cases;
deeper metadata and open-file paths remain unvalidated.
`tortoise_detectcycles.c` reduces stock `0x4cef18` pair/cycle state,
including its authenticated warning format, path and line routed to
the existing logger wrapper. Original-byte/compiled-C return, state,
and log-call oracle passes **20/20** bounded cases.

`dir_fetch.c` implements pinned LittleFS `lfs_dir_fetchmatch` at stock
`0x4cb968`, plus the `0x4cbedc` fixed no-match wrapper. It includes block revision
selection, tag/CRC scanning, directory count/tail/split/erased state,
seed update and authenticated corruption logging. Original-byte/
compiled-C oracle passes **9/9** invalid-pair and read-error cases
and **1/1** synthetic valid CCRC commit case, comparing child calls,
return and all 32 metadata bytes. A matched-tag synthetic CCRC oracle
passes **4/4** callback return cases. Other tag sequences and FCRC are
still unvalidated.

`dir_commit.c` reduces stock `0x4cd388` wrapper: it invokes real
orphaning commit, then deorphans if needed. Original-byte/compiled-C
child ABI and return oracle passes **20/20** bounded cases. Its two
large lower bodies remain explicit typed contracts.

`fs_deorphan.c` reduces stock `0x4cf7ac` two-pass half/full orphan
repair, parent/pair checks, state stealing, commits and final orphan
count update. It retains authenticated debug formats, path and line.
Original-byte/compiled-C oracle passes **12/12** no-orphan, fetch-error
and empty-directory two-pass cases; repair branches remain unvalidated.

`dir_orphaningcommit.c` reduces stock `0x4ccf7c`: open inline-file
outline/flush, relocating/drop state, root and open-list pair updates,
parent/predecessor repair, move/orphan bookkeeping and authenticated
diagnostics/assertion. Original-byte/compiled-C oracle passes **15/15**
initial failure, success, dropped and simple relocated/no-parent cases;
deeper parent/predecessor/move branches remain unvalidated.

`fs_state_helpers.c` reduces stock prepmove `0x4cf5ec`, preporphans
`0x4cf570`, and dir_getgstate `0x4cbefc` with actual gstate tag/pair,
assert and disk-state XOR effects. Original-byte/compiled-C oracle
passes **23/23** bounded cases. `fs_pred.c` reduces stock `0x4cf40a`
predecessor pair walk with cycle and directory-fetch effects; oracle
passes **12/12** bounded match, cycle, fetch-error and end cases.
`fs_parent.c` reduces stock `0x4cf4da` parent directory search using
the source-defined general fetchmatch callback and block pair
comparison. Its bounded original-byte/compiled-C dispatch oracle
passes **8/8** cycle, no-match, match, and error cases; deeper callback
and on-disk paths remain to qualify.

`dir_relocatingcommit.c` reduces stock `0x4ccb80` pinned LittleFS
attribute count/tail updates, dropped directory, erased commit and
global-state delta, compact fallback, and active metadata list repair.
Original-byte/compiled-C oracle passes **30/30** bounded attribute,
drop, traverse/CRC error and compact cases. Deeper active-list and
global-state delta paths remain unvalidated.

`dir_commitattr.c` reduces stock `0x4cc200`/`0x4cc23c` commitprog
and commitattr, including cached programming, CRC/offset update,
tag encoding and memory/disk payloads. Its original-byte/compiled-C
oracle passes **36/36** bounded fit, write/read error and payload
cases. `bd_crc.c` reduces stock `0x4caa88` chunked block CRC with
**21/21** bounded original-byte/source cases. `dir_commitcrc.c`
reduces stock `0x4cc2f2` CCRC/FCRC finalization, cache flush and
readback verification; its oracle passes **6/6** bounded read,
attribute, program and CRC error branches. A full successful CRC
round trip remains unvalidated.

`dir_splittingcompact.c` reduces stock `0x4cc9a0` split-size search,
metadata cap, split fallback, superblock expansion guard and compact
dispatch. Its original-byte/compiled-C bounded oracle passes **72/72**
split size, split-result and compact-return cases; deeper disk effects
remain with its lower bodies.

`fs_size.c` reduces stock `0x4cfa12` reachable-block count through
the source-defined traverse callback; original-byte/compiled-C
oracle passes **12/12** bounded size/error cases. `dir_traverse.c`
reduces stock `0x4cb5ac` bounded explicit-stack metadata and attribute
traversal, duplicate filtering, move/user attribute handling and
disk references. Its oracle passes **36/36** bounded in-memory
attribute, filter, callback and error cases. Disk and move recursion
paths remain unvalidated.

`dir_alloc.c` reduces stock `0x4cc502` pair allocation, previous
revision read, cycle alignment and metadata defaults. Its original-byte/
compiled-C oracle passes **80/80** bounded allocation and read outcomes.
`dir_split.c` reduces stock `0x4cc600` allocation and compaction of a
tail pair, tail/root updates and split state. Its oracle passes
**24/24** bounded success, relocation and failure cases.
`dir_compact.c` reduces stock `0x4cc6ca` metadata block erasure,
revision write, unique-tag traversal, tail and global-state attrs,
CRC finalization, metadata pair swap and bad-block relocation.
Its original-byte/compiled-C oracle passes **24/24** bounded error,
corruption, superblock, successful compaction and successful
relocation-after-allocation cases. Nonempty attribute traversal and
global-state effects remain unvalidated.

All **49** C units currently in `file_sync_candidate` compile for
Cortex-M55 with warnings as errors and link together into one
relocatable object without duplicate definitions. The source-only
object has exactly two unresolved names: `g2_file_close_error`
(implemented in the separate semihost candidate) and
`g2_log_transport_queue_failure` (implemented by the Main logger
candidate). This closes the currently selected LittleFS source-only
dependency graph, not a complete target image link or full filesystem
behavior qualification.

## Main private audio watchdog start

`codec_i2s_start_candidate/start.c` reduces the **368-byte** stock
`0x005904ce..0x0059063d` I2S start lower reached by the init body.
It validates the authenticated handle magic, checks channel status,
sets direction/control by mode 0/1/2 and programs TX/RX DMA address,
word count and activation registers in stock order. Peripheral base
`0x40208000` and magic `0x01125125` come from native literals, not
invented configuration. `verify_audio_codec_i2s_start.py` passes
**192/192** stock/C comparisons across modes, status, valid/invalid
handle, missing TX/RX descriptors and two channel banks. It compares
R0 status, ordered MMIO/RAM writes and final handle bytes. Null handle
fault behavior and actual DMA/peripheral operation remain unvalidated.
The C compiles M55 Werror; composition with the older Main/private
candidate passes without duplicates and reduces undefined names
**89→88** by binding `g2_codec_i2s_start`.

`codec_i2s_irq_candidate/irq.c` reduces three actual I2S-init
children: `__NVIC_SetPriority` at `0x0057a4b0` (**40 bytes**),
`__NVIC_EnableIRQ` at `0x0057a46c` (**30 bytes**), and the
`MRS PRIMASK; CPSIE I; BX LR` global IRQ helper at `0x00473934`
(**8 bytes**). The C uses authenticated NVIC architectural addresses,
signed 16-bit IRQ interpretation, byte priority shift and set-enable
word/bank writes. `verify_audio_codec_i2s_irq.py` compares stock
instructions and compiled C for **82/82** signed/boundary IRQ,
priority and PRIMASK cases, including write address/width/value and
saved interrupt return. Cortex-M55 Werror compilation and older Main
composition pass without duplicate symbols; the experimental graph's
undefined count falls **92→89** as these three real children bind.
Real controller interrupt behavior and product IRQ-number ownership
remain separate validation gates.

`codec_i2s_init_source_candidate/init.c` reduces the full
**216-byte** stock `DRV_Gx8002_I2SInit` outer body at
`0x0057a65c..0x0057a733`, exported as `audio_i2s_enable`.
It preserves the already-initialized branch, sets the state byte,
then invokes the observed clock, handle acquisition, disable,
configuration, preparation, DMA descriptor, IRQ priority/enable,
global IRQ and start children in stock order before logging. Five
product data contracts remain explicit: state byte `0x20074fb7`,
handle cell `0x2007450c`, config pointer `0x20000000`, DMA descriptor
`0x20000740`, and IRQ halfword `0x78f558`. The source does not supply
their declarations or contents. `verify_audio_codec_i2s_init.py`
compares the stock body with compiled C for **21/21** empty, initialized
and changing logger-flag cases, including full ordered child calls,
arguments, state, acquired handle and authenticated log literals.
Child functions are controlled cuts in this oracle; this is an outer
body reduction, not a native driver completion. Cortex-M55 Werror
compile and relocatable composition with older Main plus the private
chain pass without duplicates, exposing actual I2S child/data imports.

`pcm_unregister_source_candidate/unregister.c` reduces the complete
**296-byte** stock `SVC_PcmAppUnregister` at
`0x0057acd0..0x0057adf7`. It indexes the 12-byte registration row by
the low input byte, handles empty/matching/mismatched app entries,
emits the authenticated extended/simple logs, clears all 12 bytes on
a matching unregister, and returns 0 or −1 as stock does. The row base
at stock `0x20073c20` is a typed external data contract; its count,
producer and initial contents are not inferred. New
`verify_audio_pcm_unregister.py` original-byte/C comparison passes
**216/216** cases across three entry states, four indices including
truncation, app IDs and changing logger flags. It compares return,
all 12 row bytes, ordered calls and literal/argument contents. M55
Werror compilation and composition with the older Main graph and
other private-audio additions pass with zero duplicates. The graph
keeps **78** undefined names: `audio_unregister` is replaced by the
product row symbol `g2_pcm_registration_rows`. Registration concurrency,
row count and production logger state remain outside the oracle.

The fresh older-graph `nm -u` after these private-audio units leaves
**six** direct I2S code contracts (`g2_codec_clock_enable`,
`g2_codec_i2s_acquire`, `g2_codec_i2s_disable`,
`g2_codec_i2s_configure`, `g2_codec_i2s_prepare`,
`g2_codec_i2s_dma_configure`) and **nine** product data names across
watchdog timer, codec power/shared mask, PCM rows and the five I2S
slots. The complete older Main candidate has **88** undefined names;
the 15 named here are this private-audio chain's direct local frontier,
not the whole-image gap count. Timer expiry, GPIO/I2S hardware and
logger transport remain independent validation work.

`os_timer_start_alias_candidate/alias.c` binds the native CMSIS
`osTimerStart` name at stock `0x00449498` to the already selected
`audio_timer_start` full 64-byte C body. Both use `(timer,ticks)` and
the selected body performs the stock ISR rejection, null/zero-tick
validation, command-4 publication and status mapping. The existing
`verify_timer_start_provider.py` original/source suite passes **48/48**
fresh cases. The M55 alias compiles as a single `R_ARM_THM_JUMP24`
tail branch to `audio_timer_start`; composition with the older Main
graph and the other new private-audio units passes without duplicates.
That local graph now has **78** undefined names, one fewer than before
the alias. Timer-daemon consumption, expiry, cancellation and real tick
timing remain outside the bounded oracle.

`codec_gpio_selector_candidate/gpio.c` now reduces the full
`0x00509024..0x00509131` selector (**270 stock bytes**) and the actual
`0x00473940..0x00473947` PRIMASK save/disable lower (**8 bytes**).
It also reduces the `0x0053a5be..0x0053a5df` pin-write wrapper
(**34 bytes**), normalizing its value byte and HAL success/error result.
The separate `codec_gpio_selector_candidate/hal.c` reduces the complete
`0x00480fd6..0x004810af` HAL body (**218 bytes**): six authenticated
GPIO MMIO register aliases, eight-bank pin/bit selection, direct
write modes 0/1/3/4, and PRIMASK-guarded XOR modes 2/5. These MMIO
addresses are stock instruction literals, not inferred product tables.
Native instructions establish the selector's otherwise ambiguous
return ABI: its entry pushes incoming R3 to a stack slot and pops that
slot into R0 on ordinary channels, while shared channels 6/9 overwrite
it with the prior PRIMASK returned by `MRS; CPSID I`. The C signature
therefore carries R2/R3 explicitly, returns incoming R3 on ordinary
channels and prior PRIMASK on 6/9, and performs the native `MSR
PRIMASK` restoration. It covers 1/2/3/4/7/8 pin mapping and 6/9
shared-mask updates with exact low-byte value tests. The product mask
at stock `0x2007436c` is a typed external data contract.

`verify_audio_codec_gpio.py` compares actual stock and compiled C for
**240/240** selector cases across all branches, value truncation,
shared-mask values and starting interrupt masks, **2/2** direct
critical-save cases, **45/45** direct pin-wrapper cases, and **112/112**
full HAL MMIO cases across six modes, two interrupt states and bank
boundaries. Result R0, ordered pin/HAL calls, mask and final
PRIMASK agree. Cortex-M55 Werror compile and composed relocatable link
with watchdog/reboot/power pass without duplicates; the older graph
now has **79** undefined names. Relative to the prior graph, all four
selector/critical/pin/HAL source bodies bind locally, leaving only the
codec state byte and shared-mask data as new imports. Physical GPIO
timing/electrical behavior and those product initializers remain outside
this source proof.

`codec_power_source_candidate/power.c` reduces both GX8002 power
children called by the reboot body: `DRV_Gx8002_PowerOn`
`0x0057a508..0x0057a5bb` (**180 stock bytes**) and
`DRV_Gx8002_PowerOff` `0x0057a5bc..0x0057a655` (**154 stock bytes**).
The C retains the product state byte at stock `0x20074fb6` as a typed
external data contract, ordered GPIO 6/7/8 transitions, 5/20 tick
on delays, and both already/transition log branches with authenticated
strings and line numbers. `verify_audio_codec_power.py` compares real
stock bytes with compiled C for **56/56** state/flag/branch cases,
including changed state and ordered child calls. Cortex-M55 Werror
compile and link of the older integrated Main graph plus watchdog,
reboot and power units pass without duplicate definitions. The local
graph remains at **79** undefined names: `g2_codec_power_off/on`
disappear, while `g2_codec_gpio_write` and product byte
`g2_codec_power_state` become explicit. The later selector source above
reduces the GPIO routing body; physical pin effects and product state
initialization remain to reduce or
qualify. Together the reboot/power chain now has three full C bodies
covering **424** stock bytes; this is a source-body extent, not a
firmware completion percentage.

`codec_reboot_source_candidate/reboot.c` additionally reduces the
**90-byte** stock `DRV_Gx8002_Reboot` at
`0x0057a816..0x0057a86e`, exported as the existing unresolved
`audio_special_control` name. It performs power off, delay 100, power
on, optional delay 1,500 for a zero low input byte, and authentic
extended/simple success logs with their exact literals. The two power
children at `0x0057a5bc` and `0x0057a508` are separate typed imports;
the existing `audio_delay` and logger flag/simple providers bind to
selected C. The `verify_audio_codec_reboot.py` original-byte/compiled-C
oracle passes **42/42** cases over zero/nonzero/truncated mode and
changing logger flags. Cortex-M55 Werror compile and relocatable link
against the older integrated candidate plus watchdog body pass with no
duplicate symbols. The latter graph has **79** undefined names:
`audio_special_control` disappears, two codec power child names appear.
Actual power sequencing, GPIO/MMIO effects and logger installation
remain unqualified. This unit is a source candidate, not a complete
codec reboot stack.

`watchdog_start_source_candidate/start.c` now reduces the complete
**94-byte** stock `AUD_CodecAudioCheckTimerStart` entry at
`0x0053c2be..0x0053c31a`. It reads the typed timer pointer cell,
starts the timer for 2,000 ticks, and on failure checks the stock logger
flag bits and sends the authenticated module/file/function/line/format
arguments to the actual extended and simple logger contracts. It does
not infer a useful return value from Ghidra's ambient R5/R6 `undefined8`;
its known caller declares the routine `void`.

The candidate compiles for Cortex-M55 with `-Wall -Wextra -Werror`.
`verify_audio_watchdog_start.py` compares original Thumb bytes with
compiled Cortex-M4 C over **42/42** timer-null, timer-return and changing
logger-flag cases, including ordered calls and literal string contents.
Relocatable composition with the root Main/Audio candidate at
`final-checkpoint/apollo_main/candidate.o` passes with zero duplicates:
`audio_watchdog_start` is resolved, while the product timer cell
`g2_audio_codec_check_timer` and `osTimerStart` are newly explicit;
`audio_log_extended` already remained unresolved in that older graph,
while the flag getter and simple logger bind to existing source providers.
The combined undefined count is 78 versus 77 before this body: the
`audio_watchdog_start` import is replaced by the timer and product data
imports. Product cell initialization/placement, logger
installation and physical timer behavior remain unqualified.

For a bounded body-inventory crosscheck, the retained
`open-2026-09-29/functions-000.jsonl` has **8,853** unique Main function
entries; `decomp/functions.jsonl` has **7,449** entries, all present in
that open inventory, leaving **1,404** without a retained decompilation
record. In the private-audio address window `0x53c000..0x55ffff`, the
counts are **638** native entries, **526** retained decompilations and
**112** entries without one. This is an inventory of stock entries, not
an unreduced-C denominator: C translation units can contain multiple
stock entries or split one stock entry, and source provenance is not
encoded as a complete address-to-provider table. The concrete selected
graph crosscheck is the older `final-checkpoint` candidate with **739**
global definitions and **77** undefined names; composing this watchdog
unit yields **740** definitions and **78** undefined names, with the
exact import set delta stated above. The earlier Audio 54-import source
audit at `remaining54-source-corpus-audit.json` classified eight names
as lacking attributable source, 38 as needing joint fixtures, and eight
as source-backed actionable at that snapshot. Later experimental power,
logger and watchdog C reductions make that classification historical;
it cannot serve as a current completion percentage.

## Main whole-image continuation boundary

The full native formatter candidate adds **nine C units** and the
separate outer `vformat.c` body. Its stock Main core and the pinned Boot
model have the same 1,270 relative instruction positions, with **23**
relocated BL instructions; this corrects earlier source-header comments
that said 25. All eleven affected comments now say 23. The bounded
nonfloating and outer comparisons remain 27/27 and 24/24. A qualified
Main floating execution comparison is still unavailable: the QEMU M55
board faults on instruction fetch at the stock high flash address.

The startup-specific omitted-body audit yielded **zero additional source bodies**.
The official wrapped Main vector at offset 32 contains initial SP
`0x2007fb00` and Thumb reset entry `0x005e4233`. The retained startup
receipt executes the stock zero constructor at `0x005fa01e` on its
actual descriptor and the low-RAM decompressor at `0x0043a11e`.
Their C bodies already exist in selected `iar_runtime_candidates_20261010`
and `startup_unpack_offline`, respectively. Adding a second copy would
duplicate providers. The decoder's original stream reproduces 17,752
bytes in the evidence fixture, but that compressed payload has no
source-owned producer or section placement. The reset entry and vector
table are address observations; no retained production linker map or
complete reset C body supports a source-owned Main startup yet.

Remaining concrete Main work is product FAL device/partition objects,
the FlashDB 256-row initializer, logger output/lock state and runtime
format producers, full formatter floating/abort path qualification,
complete reset/initialized-data/link layout and hardware effects. These
are independent of the currently closed LittleFS source graph and the
experimental native formatter link. Main whole-image completion is
**false**; body/provider counts do not measure whole-image coverage.

## I2S lower continuation: power and prepare

The outer `audio_i2s_enable` stock call at `0x590648` is the already selected
`audio_i2s_power_selected` complete source body. New
`codec_i2s_power_alias_candidate/alias.c` supplies the missing
`g2_codec_i2s_disable` calling ABI and returns the selected body's result.
This is a call alias, not a second independent implementation. The outer
translation now declares its actual 32-bit return.

`codec_i2s_prepare_source_candidate/prepare.c` reduces the complete stock
`0x590b92..0x590c61` body. It checks the marker and already-prepared bit,
acquires clock 4, optionally acquires the requested source clock, configures
`0x40208000 + instance*0x1000 + 0x100`, sets handle bit 25, and releases
clock 4 on secondary acquisition failure. The immediate `0x40208000` and
marker `0x01125125` are authenticated at stock literal slots `0x590d34`
and `0x590d38`. The native dereference of handle+4 precedes its NULL check;
the candidate contract therefore requires a mapped handle. Four real lower
calls remain named as selected source graph providers/contracts rather than
inventing effects.

`verify_audio_codec_i2s_prepare.py` compares original bytes with the C body
for 32 valid/invalid marker, started/idle, source-on/off, success/failure,
and channel 0/1 combinations. It records return, ordered child calls,
RAM/MMIO writes, and final handle/register words. **32/32 pass** under
controlled child returns. This does not test physical clock sequencing or
unsupplied product initialization. Both sources compile Cortex-M55 with
`-Werror` and partially link with the prior 88-import Main snapshot without
duplicate providers; the resulting snapshot has 86 unresolved names. The
remaining direct outer I2S code contracts are clock enable, acquire,
configure, and DMA configure; nine product data contracts stay typed externs.

`codec_i2s_acquire_source_candidate/acquire.c` reduces complete stock
`0x59005e..0x5900cd`: validates instance/cell, checks the occupied bit,
performs the native three ordered writes to the 100-byte handle row,
stores the row pointer and returns status. The two-row product pool at
`0x20071114` is a typed external object; its initializer is not inferred.
`verify_audio_codec_i2s_acquire.py` stock/C **32/32 pass** including the
ordered writes, status, final row, and output cell. It compiles Cortex-M55
`-Werror` and links with the two earlier I2S lower objects, no duplicates.
The 86 unresolved-name count stays flat because a code contract became a
product data contract. Direct code contracts now remain clock enable,
configure and DMA configure.

## I2S direct-call completion and remaining lower contracts

`codec_i2s_clock_enable_source_candidate/enable.c` reduces native
`0x4c3074..0x4c3135` to the 0/1 group and low-byte mode pin dispatch.
The nine referenced descriptor words are typed externs at authenticated
`0x20000114..0x20000134`; the actual pin-function child at `0x480f0c`
remains an explicit code import. `verify_audio_codec_clock_enable.py`
compares ordered pin calls in **20/20** stock/C cases. The native epilogue
restores a saved R7 into R0, and the outer caller ignores R0, so the C
contract is `void` and the oracle compares its observable pin calls.

`codec_i2s_dma_configure_source_candidate/dma.c` reduces complete native
`0x590a24..0x590b6b` across descriptor copies and all four transfer-mode
branches. `verify_audio_codec_i2s_dma.py` compares return, ordered MMIO
writes, complete handle/config words and MMIO state in **60/60** cases.

`codec_i2s_configure_source_candidate/configure.c` reduces native
`0x590104..0x5904cd`, including slot validation, frame computation,
register construction, delay, source-clock selection and double-precision
fraction setup. Its six-word slot-width table matches the authenticated
read-only table pointed to by literal `0x590cf0`; the silicon revision
register remains a typed `volatile const` external at `0x4002000c`.
`verify_audio_codec_i2s_configure.py` compares return, controlled delay
and clock calls, ordered writes, and complete handle/MMIO state for
**192/192 nonfloating cases**. The complete body compiles Cortex-M55 with
DP VFP under `-mfpu=fpv5-d16` and `-Werror`.

`codec_i2s_float_convert_source_candidate/convert.c` reduces the integer-only
runtime conversion helper at stock `0x59823c` used by configure's double
path. Its direct original-byte/C oracle passes **15/15** positive-domain
cases, including fractional and large values. Native execution of the
whole configure double path remains unqualified because Unicorn's M4 model
rejects its double-precision VFP instruction; static source correspondence
and standalone helper equality are the current limits. Silicon timing,
actual pin state and DMA operation are untested.

All six direct outer I2S code contracts now have C definitions in the worker
candidate graph. Cortex-M55 compilation and partial linking with the prior
Main snapshot pass without duplicate definitions, leaving **94** unresolved
names in that experimental snapshot. This count rose while code names were
replaced by genuine product descriptor and chip revision data contracts.
The pool, pin descriptors, config and DMA objects remain product-owned
initializer contracts; no values were fabricated for them. The pin-function
child and the already existing `audio_power_reconfigure` child still need
source reduction or qualified provider selection before whole-image closure.

## I2S clock mux provider graph

`codec_pin_function_source_candidate/pin.c` reduces complete native
`0x480f0c..0x480f89` with authenticated generic capability masks,
PRIMASK save/restore and ordered unlock/config writes. Its stock/C oracle
passes **2724/2724** cases across 227 pin IDs, six configurations and
both interrupt states. The masks are explicit source tables transcribed
from native `0x768ba8`/`0x768bc4`, not product configuration values.

`codec_i2s_reconfigure_source_candidate/reconfigure.c` reduces complete
native `0x58fdbc..0x59005d` for the I2S source and divider register
paths. It exports same-body `audio_power_reconfigure` and
`audio_i2s_reconfigure`. `verify_audio_codec_i2s_reconfigure.py` passes
**350/350** cases comparing ordered register writes and controlled
mux child calls. The latter is source-defined by
`codec_i2s_source_mux_candidate/mux.c` for native
`0x58fd7e..0x58fdbb`, with **15/15** controlled child-call cases.

`codec_clock_mux_request_source_candidate/request.c` reduces native
`0x539bbc..0x539c99`: it resolves source group/setting, computes the
prior and requested gate masks, updates the authenticated clock control
MMIO register `0x400204e8`, delays, and drops the transitional gate.
`verify_audio_codec_clock_mux_request.py` passes **108/108** controlled
child-call, ordered MMIO and return comparisons.

Its four read-only lookup children are source-defined in
`codec_clock_mux_tables_source_candidate/tables.c`; the explicit typed
maps match authenticated read-only addresses `0x784c40`, `0x784c50`,
`0x784c60` and `0x78c98c`. Their original-byte/C oracle passes
**56/56** entries over accepted source IDs 0..15 and group IDs 0..7.
The current-source query `codec_clock_mux_prepare_source_candidate/prepare.c`
reduces native `0x539c9a..0x539d75`, with **80/80** stock/C cases.
The request aggregator `codec_clock_mux_gate_source_candidate/gate.c`
reduces native `0x44b0d6..0x44b157`, preserving all five ordered
control writes and PRIMASK effects; its oracle passes **504/504** cases.
The six mutable request bytes at `0x200740ec` remain a typed product RAM
initializer contract. Each source compiles with Cortex-M55 `-Werror` and
partially links without duplicate providers. A fresh 14-object recompilation
against the prior Main snapshot has **91** unresolved names after this set;
graph counts remain dependent on
which product data objects the coordinator selects.

The configure double path remains a complete C candidate with native DP
instruction correspondence, a directly verified conversion helper and no
whole-path stock execution oracle on the available M4 emulator. The Main
firmware still lacks product initialization/layout and full device effects;
this component-level source graph does not imply a flashable image.

## PDM source graph

`codec_pdm_init_source_candidate/init.c` reduces both native public
initializers, production `0x57b4a8..0x57b585` and alternate
`0x57b770..0x57b86b`; its bounded stock/C oracle passes 42/42 cases.
The ten production/alternate configuration, descriptor, IRQ and mutable
state cells remain typed product data imports. The PDM pin cells at
`0x2007421c/0x20074220` and four handle rows at `0x200718c8` are
likewise explicit external product data.

Eleven source files now define the public initializers and their native
PDM code graph: clock enable `0x4c31d8`, handle acquire `0x591fac`,
DMA prepare `0x592556`, disable/power `0x592046`, clock prepare
`0x592462`, IRQ prepare `0x592230`, clock classifier `0x591d14`,
descriptor stride `0x59233c`, start `0x59235e`, configure `0x5920cc`,
clock mux adapter `0x591d56` and clock select `0x591d7a`.
The stock/C bounded oracles pass respectively 15/15, 48/48, 32/32,
360/360, 32/32, 216/216, 27/27, 144/144 for stride/start,
24/24 for configure, and 512/512 for mux/clock select. The
configure and start comparisons include ordered MMIO writes and their
handle memory effects. Clock selection tests cover revisions 0..3,
sources 0..3, field values 0..7, both enable states and two instances.

All eleven files compile for Cortex-M55 at `-O2 -Werror` and partially
link against the prior Main candidate snapshot with zero duplicate
providers. The resulting `/tmp/g2-main-pdm-eleven.o` has 102 unresolved
symbol names, up from 91 before this source expansion because PDM product
data cells are now explicit. The PDM graph has no remaining direct code
imports; all `g2_pdm_*` unresolved names are typed product data. This
is candidate source coverage with bounded software oracles, not native
peripheral operation or whole firmware completion.

## PCM registration public body

`pcm_register_source_candidate/register.c` reduces complete native
`SVC_PcmAppRegister` `0x57ab78..0x57accf`. It validates the low-byte
mode and callback, overwrites an occupied 12-byte row in native word
clear order, publishes owner/mode/callback, and preserves all three
observed logging sites with authenticated native strings and levels.
The prior unregister candidate uses the same typed external registration
row base (`0x20073c20`); its producer and initial contents remain a
product data contract. `verify_audio_pcm_register.py` passes **288/288**
original-byte/C cases over invalid and valid modes, empty/occupied
rows, callback values, owner IDs and changing logger flags. The oracle
compares return, all row bytes, ordered logger calls and arguments.
The source compiles Cortex-M55 `-O2 -Werror` and partially links with
`/tmp/g2-main-pdm-eleven.o` without duplicate providers. It adds a
private whole-body provider; the experimental graph still has **102**
unresolved names. Logger children are controlled oracle cuts, and
registration concurrency is not established.

## Codec heap allocation and release

`codec_heap_allocate_source_candidate/allocate.c` reduces native
`codec_allocate` `0x474cd2..0x474d15`: it acquires the authenticated
file mutex for 1000 ticks, allocates from the TLSF pool, releases the
mutex, or executes the source-owned error logging and fatal-reporting
calls on acquisition failure. The two product RAM cells at
`0x200748f8` and `0x20074abc` are typed external data. Its controlled
stock/C comparison passes **30/30** mutex-success/failure, size and
allocation-result cases, preserving ordered calls and exact failure
literals and return values.

`file_pool_allocate_candidate/pool_allocate.c` reduces the complete
native `0x4d0722..0x4d0743` TLSF composition: adjust requested size
at alignment four, find a suitable block, then prepare allocation.
Its controlled original-byte/C child-call oracle passes **48/48** cases.
Three deeper TLSF helpers remain explicit code contracts:
`g2_tlsf_adjust_request` `0x4cff42`, `g2_tlsf_find_suitable`
`0x4d0484`, `g2_tlsf_prepare_allocation` `0x4d04e6`.
`codec_heap_release_source_candidate/release.c` binds the public
`codec_release` name to the source-defined `audio_file_heap_free`
body at the same native entry `0x474d16`; that body retains the
mutex and pool-free effects.

All three sources compile Cortex-M55 `-O2 -Werror` and partially link
with the prior Main candidate without duplicate providers. The local
experimental snapshot now has **107** unresolved names, reflecting
explicit heap cells, three deeper TLSF helpers and file free/error
children absent from this older base snapshot. The bounded allocation
oracle cuts at real lower functions; it does not prove TLSF mutation,
concurrent memory ownership or runtime exhaustion behavior.

## TLSF allocation lower closure

`tlsf_adjust_request_candidate/adjust.c` reduces native size adjustment
`0x4cff42` and alignment child `0x4cfec2`. The ROM TLSF limits are
verified as 12 and `0x40000000` at `0x78f4c4/0x78f4c8`; the
non-power-of-two alignment assertion uses the authenticated original
message. Direct original-byte/C comparison passes **168/168** cases.

`tlsf_locate_free_candidate/locate.c` reduces mapping search
`0x4cff9a`, bitmap search `0x4cffc2` and free-block locator
`0x4d0484`. It reuses selected TLSF mapping, block-size and
free-list-removal source functions with their actual call ABI.
Direct bitmap search compares **312/312** cases, including current class,
next class and no block; controlled outer locator compares **130/130**
valid/empty and class-boundary cases. Helpers remain separate
`noinline` functions so the outer test observes their actual call ABI.

`tlsf_prepare_allocation_candidate/prepare.c` reduces preparation
`0x4d04e6`, free-block trimming `0x4d039e`, mark-used `0x4cfeac`
and previous-free flag setter `0x4cfde8`. Its controlled outer
native-byte/C child-order oracle passes **8/8** cases. The mark-used
and trim helpers retain real block header and list effects in C, but
full concurrent allocator behavior is not qualified by this oracle.
`tlsf_split_block_candidate/split.c` reduces can-split `0x4d01bc`,
split `0x4d01d4` and size setter `0x4cfd84`; direct bounded oracles
pass **140/140** size/predicate cases and **112/112** full split
memory plus mark/error child cases, using selected C block-size,
pointer and alignment functions.

All new allocation files compile Cortex-M55 `-O2 -Werror`. Partial
linking them with all previously selected `file_pool_free_candidate`
and `file_heap_free_candidate` sources produces no duplicate symbols
and **103** unresolved names in `/tmp/g2-main-codec-heap-selected.o`.
There are no remaining `g2_tlsf_*`, file-pool or codec allocator code
imports in that local composition. The two codec heap mutex/pool RAM
cells are typed product data imports. Global unresolved counts are
snapshot-specific and include unrelated Main/Audio domains.

## Private audio voltage and clock routing

`callback_voltage_source_candidate/voltage.c` reduces native
`0x5a423c..0x5a4323`. It selects the observed five-bit fields from
four product RAM words at route-table base `0x2005665c` (typed
external) or existing MMIO, then updates register fields at
`0x40020344` and `0x40020358` in native order. Selection 8 forces
route 7; source values outside 0..7 use the native default branch.
`verify_audio_callback_voltage.py` passes **120/120** original-byte/C
cases for all branches, three selector values and four RAM/MMIO
seeds, comparing ordered writes and the final register page.

`audio_clock_stop_source_candidate/stop.c` reduces native
`0x4c3138..0x4c31d5`, applying the exact ordered pin-function calls
for clock groups 0 and 1, with the low-byte mode controlling the
fourth pin. The authenticated read-only pin configuration word at
`0x78ee48` remains typed product data. Its controlled original-byte/C
oracle passes **30/30** group/mode cases.

`thread_flags_public_alias_candidate/alias.c` binds
`audio_flags_set` to the already selected full
`audio_thread_flags_set` C body for the identical native entry
`0x449238`; the earlier stock comparison covered 1,440 cases.
This binding does not introduce a new flag algorithm. All three new
files compile Cortex-M55 `-O2 -Werror` and partially link without
duplicate providers. The local candidate has **102** unresolved names:
three code imports were replaced by two typed product cells.
Voltage routing, GPIO state and task notification remain subject to
hardware and runtime qualification.

## FreeRTOS task notification body

`task_notify_source_candidate/notify.c` reduces the native task-context
`xTaskGenericNotify` body `0x455c48..0x455db9` as `audio_notify_task`.
It preserves the valid index-zero task path: critical entry/exit,
optional previous-value publication, five notification actions,
state transition to received, event-list removal, ready-list insertion,
top-priority update, next-unblock maintenance and conditional yield.
The four scheduler state cells/list roots at `0x20074a34`,
`0x20074a38`, `0x20074a20` and `0x2006a49c` remain typed external
product RAM. The invalid task/index/assert branches contain the
native decoded BASEPRI read, invalid-address write and terminal loop;
these fault paths are excluded from the execution oracle and are not a
runtime success substitute.

`verify_audio_task_notify.py` passes **324/324** original-byte/C cases
for valid tasks across prior states 0/1/2, all five actions plus an
assert-disabled invalid action, value/previous pointer variants, and
relative task priorities. It compares return, 112 TCB bytes, event and
ready list memory, optional previous value, top priority and ordered
critical/next-unblock/yield calls. Scheduler children are controlled
cuts, so integrated scheduling and interrupt preemption remain
unqualified. Cortex-M55 `-O2 -Werror` compilation and partial link with
the prior Main graph pass without duplicate providers. The local graph
has **105** unresolved names: the code import is replaced by four
typed scheduler data contracts, net +3.

`receiver_notify_alias_candidate/alias.c` binds two receiver imports to
their exact native entries now represented by selected C:
`receiver_notify` uses task notify `0x455c48`, and
`receiver_notify_wait` uses notification wait `0x455b84`.
The latter selected source remains qualified only for index-zero and
bounded nonblocking paths; no claim is made for completed scheduler
blocking or timeout delivery. Cortex-M55 `-O2 -Werror` and partial
link pass without duplicates. The local graph's unresolved names fall
**105→103** for these two same-entry bindings.

## Audio thread message submission

`audio_submit_source_candidate/submit.c` reduces the complete native
`AUD_SendMessage` body at `0x53c638..0x53c6b1` as
`stock_audio_submit`. It validates the message and queue, calls the
selected CMSIS queue put implementation, signals the audio task with
flag `0x400000` on success, and emits the native conditional extended
and simple log calls on failure. The queue/task dispatch object at
`0x20003f98` remains typed external product RAM; module, source path,
function, line and failure strings are authenticated stock literals.
`verify_audio_submit.py` passes **96/96** original-byte/C cases across
null inputs, queue status and all three log flag bits. It compares
ordered child calls and literal/argument values; queue, flag and logger
implementations are controlled cuts. Cortex-M55 `-O2 -Werror`
compilation and partial linking with the selected Main candidate pass
without duplicate providers. The local graph has **103** unresolved
names: one code import is replaced by one product RAM contract.
Integrated task scheduling, logging transport and device behavior remain
unqualified.

`pcm21_classify_source_candidate/classify.c` reduces native PCM2.1
classifier `0x5a0a70..0x5a0ae7`: the exact `-273`, `-20`, `0`, `50`,
and `1000` float thresholds and fallback range 4, including unordered
NaN behavior. The selected PCM2.1 caller passes a softfp R0 argument;
stock accepts S0. `verify_pcm21_classify.py` explicitly supplies the
same input bits through those respective ABIs and passes **24/24**
finite, boundary, infinity, NaN and subnormal cases. Cortex-M55
`-O2 -Werror` compilation and partial link pass; the local graph drops
to **102** unresolved names. This is a bounded classifier proof, not
whole PCM2.1 controller or physical temperature-range validation.

`ton_adjust_alias_candidate/alias.c` binds the transition callers'
`stock_ton_adjust` name to selected `callback_voltage`, which the
retained address mapping places at the same native `0x5a423c` entry.
The latter's 120/120 original-byte/C routing cases are the behavioral
evidence; the alias introduces no new voltage algorithm. It compiles
and partial-links without duplicate providers, reducing the local
unresolved count **102→101**.

`audio_queue_new_source_candidate/new.c` reduces native CMSIS
`osMessageQueueNew` `0x449a32..0x449abd`. It preserves ISR rejection,
count/size guards, exact CMSIS attribute offsets, static control block
size 80, wrapping 32-bit queue byte count, dynamic fallback and invalid
attribute rejection. `verify_audio_queue_new.py` passes **144/144**
original-byte/C cases, comparing return and ordered lower call arguments
for ISR, null/valid/invalid attributes and static/dynamic paths. The
static and dynamic FreeRTOS constructors remain explicit child imports;
the selected archive already contains `xQueueGenericCreateStatic` for
the first one, subject to an exact ABI binding. Cortex-M55 `-O2
-Werror` compilation and partial link pass without duplicates. The
local graph has **102** unresolved names because one outer import is
replaced by two deeper constructors. Queue allocation and scheduler
effects remain below the controlled cut.

`queue_static_alias_candidate/alias.c` maps the static child to the
already selected `xQueueGenericCreateStatic`, whose native entry is
`0x4415ca` and whose five-argument ABI matches. The dynamic child is
now a complete native/pinned FreeRTOS 10.5.1 source reduction in
`queue_dynamic_source_candidate/create.c` for `0x441636..0x441695`,
including count/size overflow guards, allocation of the 80-byte
control block plus storage, dynamic marker, queue layout initialization
and selected `xQueueGenericReset`. Its decoded invalid-input path calls
the retained `offline_assert` contract and performs the native fatal
invalid-address store/terminal loop; that path is not exercised by the
valid outer constructor. `verify_audio_queue_dynamic.py` passes
**72/72** original-byte/C valid cases for count, size, queue type,
allocation success/failure, ordered malloc/reset arguments and the
80-byte control block. Both files compile Cortex-M55 `-O2 -Werror`
and partial-link without duplicates. The local unresolved count is
**100**, with `offline_assert` still an original fatal contract. The
real allocator, scheduler reset and fatal path remain outside these
bounded tests.

`transaction_send_source_candidate/send.c` reduces native
`gx8002_send_and_wait_response` `0x57c512..0x57c60f` with seven
arguments: null descriptor rejection, protocol init, narrowed packet
construction, cleanup on every failed stage, response exchange,
response extraction, and the conditional authenticated response log.
The transport root `0x2007397c` remains typed external product RAM;
five genuine protocol children are explicit imports. The exact
module/source/function and response strings come from stock literal
targets. `verify_audio_transaction_send.py` passes **16/16** controlled
original-byte/C cases across null/success/three failure stages and
argument narrowing. It compares return and ordered lower calls with
logging disabled; protocol children and log-enabled formatting are not
composed by this oracle. Cortex-M55 `-O2 -Werror` compilation and
partial link pass, zero duplicate providers. The local graph has
**105** unresolved names because one outer code import exposes five
protocol code contracts plus one product RAM root.

`transaction_session_source_candidate/session.c` reduces native
`gx8002_host_init` `0x57ba88..0x57baeb` and release wrapper
`0x57baec..0x57baf3`. The init body opens the UART session, performs
native conditional failure logging, and configures the authenticated
115200 baud argument on success; release closes the session. The three
UART lower operations remain explicit code contracts.
`verify_audio_transaction_session.py` passes **6/6** original-byte/C
controlled cases for success, positive/negative open failure and
cleanup call order, with logging disabled. Cortex-M55 `-O2 -Werror`
compilation and partial link pass without duplicate providers. The
local graph has **106** unresolved names after replacing two wrapper
imports with three actual UART children; hardware UART behavior and
log-enabled formatting remain unverified.

## GX8002 UART session lower bodies

`uart_session_full_candidate/session.c` reduces native
`codec.porting` UART resume/suspend bodies
`0x58fb52..0x58fca7`. It retains one-time ring and callback
registration, a resumed-state guard, channel enable/disable, error
returns and all authenticated conditional log branches. The ring,
storage and two state bytes remain typed product RAM at `0x20073ed4`,
`0x200731b0`, `0x20075014`, and `0x20075015`. Existing selected
`codec_ring_initialize`, `codec_channel_callback`,
`codec_channel_enable/disable` and `codec_uart_baud` provide the lower
body implementations; the callback source is already selected as
`codec_rx_callback`. `verify_audio_uart_session.py` passes **16/16**
original-byte/C cases over initialized/resumed states and channel
success/failure, comparing return, ordered child ABI calls and product
state bytes. Logging is disabled in this oracle, so exact rendered logs
are not yet validated. Cortex-M55 `-O2 -Werror` compilation and partial
link pass without duplicates. The local graph has **107** unresolved
names: the three UART code imports are replaced by four typed product
RAM contracts. Physical UART and power state remain unverified.

`transaction_construct_source_candidate/construct.c` reduces native
`gx8002_send_message` `0x57c0d6..0x57c1fb`: narrowed packet fields,
the typed TX buffer at `0x2007399c`, packet packing, hex dump,
UART send, failure returns and authenticated conditional logs.
`verify_audio_transaction_construct.py` passes **9/9** original-byte/C
controlled cases for pack and send failures, success and argument
narrowing. It compares ordered lower calls and return with log flags
zero. The deeper packet packer and dump formatter are explicit code
imports. `uart_send_alias_candidate/alias.c` maps native
`0x58fb38..0x58fb51` to the already selected `codec_uart_tx` wrapper
with the same channel-3 status conversion. Both files compile
Cortex-M55 `-O2 -Werror` and partially link without duplicates. The
local graph has **109** unresolved names; packet packing, dump output,
product TX buffer and UART hardware still require integration or data.

`packet_pack_alias_candidate/alias.c` binds the native packet packer
`0x57bb0a` to selected `codec_pack` for its payload/CRC algorithm and
implements the native oversized-body and successful-packet extended
and simple diagnostic branches. The retained
`audio-codec-request-tx-2026-10-09` receipt reports **80** direct
stock/source algorithm fixtures in its log-disabled domain.
`verify_audio_packet_pack_logs.py` adds **35/35** original-byte/C cases
across overflow/success/null pointers and log masks 0/1/2/4/7. It
compares return, 40 packet bytes, output length, sequence mutation,
ordered log calls, source strings and every variadic argument. This
qualifies the exercised diagnostic branches while deeper packet sizes,
payload permutations and full logger rendering remain outside the
bounded fixture. Cortex-M55 `-O2 -Werror` and partial link pass with no
duplicates, reducing the local unresolved count **109→108**.

`transaction_exchange_source_candidate/exchange.c` reduces native
`gx8002_read_uart_data` `0x57c442..0x57c511` with capacity/pointer
guards, selected `codec_response_read` framing loop, success length
publication, authenticated failure/success diagnostic branches and
receive hex dump. `verify_audio_transaction_exchange.py` passes
**25/25** original-byte/C cases across invalid input, negative and
nonnegative read results, and log masks 0/1/2/4/7. It compares
return, length bytes, ordered lower calls, strings and variadic
arguments. The framing loop is a controlled child cut in this oracle;
its prior selected source evidence remains separate. Cortex-M55
`-O2 -Werror` compilation and partial link pass without duplicates.
The local unresolved count falls **108→107**; `audio_dump_hex` remains
the actual lower code import.

`transaction_extract_source_candidate/extract.c` now reduces the full
native `gx8002_unpack_message` body `0x57bd06..0x57c0d5`, including
the pinned header/CRC/owned-payload algorithm, seven return statuses,
all native diagnostic branches, the success summary and optional body
dump. It uses selected `codec_crc32`, `codec_allocate`, and
`codec_release` lower bodies. On body-CRC failure, it logs before
freeing the payload and clears the owned pointer while retaining the
length, as the original does. A first wrapper around selected
`codec_unpack` failed an ordered-call comparison because that child
freed before diagnostics; the final source includes the actual packet
algorithm to preserve native order. `verify_audio_transaction_extract.py`
passes **50/50** original-byte/C cases covering null inputs,
magic/length/header CRC/body size/allocation/body CRC failures,
header-only and owned-payload success, each under log masks
0/1/2/4/7. It compares return, 26 descriptor bytes, owned bytes,
ordered allocation/free/log/dump calls, authenticated strings and
variadic arguments. The CRC implementation and allocation/free effects
remain controlled or separately selected source; live codec traffic is
unverified. Cortex-M55 `-O2 -Werror` compilation and partial link pass
without duplicates. The local unresolved count falls **107→106**.

### Audio hex dump 0x43dacc (2026-10-11 continuation)

`g2/components/audio/audio_dump_hex_source_candidate/dump.c` reconstructs the full native dump loop: logger enable/token gate, guard entry/exit, 1024-byte shared buffer, `D/HEX %s: %04X-%04X: ` header, two-digit hex cells, three-space missing-byte padding, extra separator every eight bytes, printable ASCII or dot, newline, and raw transport submission. The selected formatter lower is `g2_log_vformat`; the selected append, token, guard, and transport providers are reused. Product objects remain typed imports at RAM 0x20070be8 (`g2_audio_dump_log_state`, >=0xf2 bytes) and 0x2006bd30 (`g2_audio_dump_buffer`,1024 bytes).

`verify_audio_dump_hex.py` compares native 0x43dacc and Cortex-M4 compiled source with identical controlled formatter/append/sink cuts. PASS 24/24 cases span 0/1/8/9/17/32 bytes and enabled/level/token gates, comparing child call order, exact submitted strings, and shared buffer bytes. Cortex-M55 -O2 -Wall -Wextra -Werror compile and relocatable link with prior candidate archive pass with zero duplicate definitions. This is a bounded code and ABI proof; it does not qualify the full native formatter implementation, initialized product RAM, transport hardware, or the whole firmware image. The local unresolved set gains two product RAM cells and consumes the `audio_dump_hex` code import.

### Timer daemon full command drain 0x47e97a (2026-10-11 continuation)

The latest unified Main archive still imported `audio_daemon_drain_commands` and `stock_timer_drain_commands`; both name the native FreeRTOS command-drain entry at 0x47e97a. `g2/components/audio/timer_drain_full_source_candidate/drain.c` now defines that single body with an alias for both imports. It handles negative pending callbacks, start/reset command IDs 1/2/6/7, stop IDs 3/8, change-period IDs 4/9, delete ID 5, and unknown IDs. It uses already selected queue receive, list remove, time sample, timer insertion, reload, and heap-free providers. The queue handle at 0x20074ab0 remains an explicit typed data import. The existing `offline_assert` import retains the native zero-period failure boundary.

`verify_audio_timer_drain_full.py` passes 33/33 original-byte/C one-command comparisons covering all command IDs above and three status/list/insert conditions each. The oracle compares ordered child calls and all 44 timer-prefix bytes; it exposed and corrected native reload-before-callback ordering and single-shot active-bit clearing. Cortex-M55 -O2 -Wall -Wextra -Werror compilation and relocatable link with the latest unified Main archive pass with no duplicate definitions. That archive's unresolved-symbol count falls 101 to 100: two code names consumed and one typed product queue cell exposed. Multi-command tick-wrap and live scheduler execution remain unqualified.

### Short audio packet formatter 0x43cb84 (2026-10-11 continuation)

The retained, already stock-qualified `audio-dsp-frontier-20261010/short_formatter.c` was promoted to `g2/components/audio/audio_log_format_source_candidate/format.c` as the unresolved production-facing `audio_log_format` ABI. It encodes the 44-byte compact log packet, checks flags and category level, advances the sequence byte, records tick/context/token fields, scans the supported format grammar, copies string tails, converts double arguments to float payloads, and passes the packet to the native emit lower. `helpers.c` binds native level 0x43d0da, CMSIS tick 0x4490cc, and string length 0x44a43c to existing selected source providers. The promoted source compiles with `-mfpu=fpv5-d16 -mfloat-abi=softfp`; the default single-precision FPU flag would introduce a new `__aeabi_d2f` import, so the double-precision setting should be source-specific in the unified builder.

`verify_audio_log_format.py` recompiles the promoted source and compares the actual original 0x43cb84 body across 6,926 cases, including supported/adversarial format grammar, category gates, sequence wrapping, 64-bit and float bit patterns, and FPSCR modes. PASS 6,926/6,926. The stock body and this source share controlled lower cuts for flags, level, tick, context, string length, and emission. This does not qualify initialized product RAM, downstream emission or RTC hardware.

`context.c` reconstructs native 0x44a1c6 and passes 35/35 controlled stock comparisons for signed timezone quarters; `epoch.c` reconstructs native 0x44a108 and passes 3,600/3,600 valid-calendar comparisons. `snapshot.c` reconstructs the one-child wrapper 0x47ef10. Cortex-M55 -O2 -Wall -Wextra -Werror compile and partial relocatable link with the current unified Main archive pass without duplicates. The exposed true-code lower frontier is `audio_log_emit` 0x43ca50 and `audio_rtc_read_calendar` 0x4d3c0a; product data are `audio_log_sequence` byte at 0x20074f9f and `g2_audio_log_timezone` pointer cell at 0x200036fc. The full formatter source itself consumes the `audio_log_format` code import.

The short-log graph was continued through the remaining actual code. `emit.c` reconstructs native 0x43ca50..0x43cb83 ring insertion, wrap copy, overflow thresholds, lock, and wake logic; `verify_audio_log_emit.py` passes 1,920/1,920 original/C controlled cases comparing ordered calls, ring state, and all 256 buffer bytes. `wake.c` reconstructs native 0x443484, 0x4487ac, and 0x448f7c with typed RAM cells and the already selected event signal provider; `verify_audio_log_wake.py` passes 432/432. `rtc_read.c` reconstructs native 0x4d3c0a BCD calendar read from authenticated RTC registers and PRIMASK restore; `verify_audio_rtc_read.py` passes 384/384 with controlled latch/critical children. `rtc_latch.c` reconstructs native 0x4d3b9a MMIO capture transaction, counter-change wait, and 10-us delay; `verify_audio_rtc_latch.py` passes 72/72 MMIO write/delay traces under controlled counter updates. `helpers.c` maps the RTC delay call at 0x4807a0 to already selected `audio_delay_us`.

All nine `audio_log_format_source_candidate` C units compile for Cortex-M55 with `-O2 -Wall -Wextra -Werror`; `format.c` uses `-mfpu=fpv5-d16 -mfloat-abi=softfp` to preserve the native double-to-float instruction path and avoid adding `__aeabi_d2f`. Linking them into the current unified Main relocatable archive passes with no duplicate definitions. The archive's unresolved count changes 101 to 107: one genuine code import is consumed while seven typed product RAM/config cells are exposed. The new cells include the packet sequence byte 0x20074f9f, timezone pointer 0x200036fc, ring state 0x200004c8, wake enable 0x20074f2c, transport bits 0x20075043, alternate transport byte 0x20072730, and event handle 0x20074570. The existing `audio_log_lock_state` and `audio_log_policy_byte` cells are also required. Source-owned lower code for this compact formatter is now closed against selected providers; RTC hardware and initialized RAM remain outside the bounded oracles.

### Extended log and thread termination (2026-10-11 continuation)

`g2/components/audio/audio_log_entries_source_candidate/compressed.c` instantiates the previously selected full simple-log C implementation under the stock `compressed_log_output` entry name, both mapping to 0x43ce9e. `verify_compressed_log_output.py` passes 162/162 controlled original-byte comparisons for policy, interrupt context, lock, and formatting branches. `extended.c` binds the separately selected experimental Main extended logger body to `audio_log_extended` at 0x43d574; it compiles and links without duplicate symbols, but inherits that body's bounded early/one-bit evidence limit and remains an experimental code candidate rather than full stock equivalence.

`g2/components/audio/thread_terminate_source_candidate/terminate.c` reconstructs CMSIS `osThreadTerminate` 0x4491fe and passes 36/36 original-byte/C cases with controlled IRQ, task-state, and task-delete children. `state.c` reconstructs FreeRTOS `eTaskGetState` 0x454b88, including critical-section reads, both delayed lists, suspended/notification distinction, terminated list, and current task. `verify_audio_task_state.py` passes 72/72 original-byte/C cases spanning current/noncurrent, six containers, task notification state, and notify byte, including ordered critical calls. All four files compile Cortex-M55 `-O2 -Werror` and partial-link without duplicate definitions against the current Main archive. The remaining genuine termination lower is `audio_task_delete` 0x454aae. The four task/list RAM cells remain typed unresolved product data. Native task deletion, live scheduler behavior, and complete extended logging are not yet qualified.

`delete.c` now reconstructs FreeRTOS `vTaskDelete` 0x454aae..0x454b4b, including removal from ready/event lists, deletion count, self-task terminated-list insertion, other-task count/cleanup, next-unblock reset, and scheduler yield/assert conditions. `verify_audio_task_delete.py` passes 12/12 original-byte/C controlled-child comparisons over self/other task, event-list membership, scheduler off/on, and null/self handle; it compares child call order and task counters. Cortex-M55 `-O2 -Wall -Wextra -Werror` compile and partial link pass without duplicate definitions. The remaining true code lower is `audio_task_cleanup` 0x455836; task counters, scheduler cells, and terminated list stay typed product RAM contracts. Scheduler-suspended fatal path and live task teardown remain unqualified.

`cleanup.c` completes native `prvDeleteTCB` 0x455836..0x455875, honoring allocation modes 0 (free stack and TCB), 1 (free TCB), and 2 (externally owned). It reuses the selected vPortFree provider as `audio_heap_free`; `verify_audio_task_cleanup.py` passes 3/3 original-byte/C valid-mode comparisons. Cortex-M55 `-O2 -Werror` compile and partial link with `delete.c` pass, zero duplicates. Invalid allocation mode remains a genuine native assert path represented by the existing nonreturning `offline_assert` contract. The termination source-owned code frontier now closes against selected providers; initialized kernel RAM and live scheduler effects remain unqualified.

### UART service thread and power frontier (2026-10-11 continuation)

The latest unified Main archive imported `uart_thread_handler` 0x5417d6 and `audio_power_peripheral_on/off` 0x47f5b8/0x47f7ae. The latter already have an experimental pinned Ambiq full-branch projection in `g2/components/audio/power_vendor_candidate/power.c`, but its README records stock differences for ordinary/audio SPOT callback failures and unresolved product configuration. It is not yet a valid direct native provider.

`g2/components/audio/uart_thread_source_candidate/thread.c` reconstructs the 600-byte service-thread outer flow: event/mutex/transport initialization and error logs, readiness check, service setup sequence, event wait/clear, command-byte dispatch, UART receive loop with 32 iteration or 32 KiB ceiling, and event bits 2/4. Its native data cells are typed externs for event/mutex/transport handles, callback, command, receive buffer, and log strings. The lower application and transport calls remain genuine code imports, with native addresses annotated. Cortex-M55 `-O2 -Wall -Wextra -Werror` compilation and partial link against the latest unified Main archive pass without duplicate definitions. `verify_audio_uart_thread_init.py` passes 4/4 original-byte/C controlled initialization cuts (event, mutex, transport, readiness failure), comparing call order and three handle cells. The infinite service loop, logger side effects, downstream drivers, and product data initialization remain unqualified. This is an experimental whole-body source projection, not a stock-equivalent admission.

The pinned Ambiq power projection was corrected for one authenticated stock difference: native enable 0x47f660/0x47f67c and disable 0x47f8e4/0x47f8fe ignore the ordinary/audio SPOT callback return and continue. `power_vendor_candidate/power.c` now does so and compiles Cortex-M55 `-O2 -Wall -Wextra -Werror`. This is static native branch correspondence, not an oracle for the complete 314/350-byte power bodies; product descriptor/configuration, other active domains, and physical MMIO timing still prevent direct stock provider admission.

The UART oracle was extended to 8/8 cases. Four additional cases pass through successful initialization and one event-loop iteration with masks 0/2/4/6, comparing ordered service setup, event wait/clear/processor calls, and handle cells. This caught and fixed a real source projection error: the native handler waits and clears on the mutex/event aggregate stored at 0x20074b10, not the first handle at 0x20074b18. The receive-data and command-bit paths remain untested; the candidate remains experimental.

A local unresolved-symbol census against `auxiliary-transition-audio-formatter-integrated-round/apollo_main/candidate.o` changes 107 to 147 after this single UART thread is added: the top-level `uart_thread_handler` import is consumed and 41 previously hidden contracts become visible (22 lower code names, 19 product RAM/ROM/callback names). Existing `audio_event_wait` and logger providers are reused. These counts are candidate-graph exposure, not completed component or target firmware coverage.

### UART constructor/command/event lowers (2026-10-11 continuation)

The authenticated native catalogue identifies 0x44971c as `osMutexNew` and 0x449590 as `osEventFlagsNew`. The UART source was corrected to name those functions and handle cells accurately: mutex at 0x20074b18, event flags at 0x20074b10. Stock literals at 0x75c180/0x75c1a4 confirm the respective failure messages. The UART thread oracle still passes 8/8 after this correction.

`uart_thread_source_candidate/cmsis_new.c` reconstructs both constructors with IRQ gating, attribute storage/size validation, recursive mutex flag, dynamic/static allocation dispatch, and tagged recursive handle. `verify_audio_uart_cmsis_new.py` passes 96/96 original-byte/C controlled cases. `event_clear.c` reconstructs osEventFlagsClear 0x449642, including parameter validation, ISR versus task clear, prior bits, and SCB ICSR PendSV on ISR success; `verify_audio_uart_event_clear.py` passes 40/40 controlled original-byte/C cases including exact MMIO. `command_mode.c` reconstructs the 6-byte product mode getter 0x4abe60 and passes all 256 byte values. The byte at 0x200038f1 remains a typed product data contract.

`transport_new.c` reconstructs the ring constructor 0x57df7c, validates the real capacity/storage prerequisites, normalizes zero element size, selects mode 2/3, invokes the genuine 0x57e3a4 initialization lower, sets descriptor flag bit 1, and returns the descriptor. `verify_audio_uart_transport_new.py` passes 96/96 valid original-byte/C cases comparing seven child arguments, return pointer, and descriptor flag byte. Native assert paths use the existing nonreturning `offline_assert` contract. All four files compile Cortex-M55 `-O2 -Wall -Wextra -Werror` and partial-link without duplicate symbols. Deeper allocator/event implementation, transport initialization/receive, and application service children remain open.

`ring_init.c` reduces native ring initializer 0x57e3a4 and the source-owned fill semantics of native 0x43c0e4. It fills storage with 0x55, clears 36 descriptor bytes, writes storage/capacity/element size/mode at their native offsets, and preserves unused trailing bytes. `verify_audio_uart_ring_init.py` executes the original memset helper and passes 24/24 original-byte/C cases across capacities, element widths and modes, comparing 64 descriptor and 256 storage bytes. `service_small.c` reduces 0x45a570 service-mode getter (all 256 values match native) and 0x5417c4 three-child sync reset wrapper, with callback address 0x5417a5 kept as a typed code contract. Both compile and partial-link without duplicate symbols. These five new UART lower files expose deeper allocator/event and application children; they are source graph progress rather than whole-image completion.

`event_lower.c` reconstructs static/dynamic FreeRTOS event-group creation 0x47eb94/0x47ebd8 and task clear 0x47ed10, using the exact 0x45607c list initializer layout and already selected `pvPortMalloc`/critical providers. `verify_audio_uart_event_lower.py` passes 72/72 original-byte/C cases, comparing full 40-byte event object and ordered allocation/critical calls. `mutex_lower.c` reconstructs 0x4416d6/0x4416f0 dynamic/static mutex wrappers and 0x4416b8 setup, reusing the selected FreeRTOS queue constructors at 0x441636/0x4415ca. `verify_audio_uart_mutex_lower.py` passes 12/12 controlled original-byte/C cases, comparing queue child ABI, return handle and 80-byte mutex object. Both compile Cortex-M55 `-O2 -Wall -Wextra -Werror`, partial-link without duplicate symbols. The queue-send child 0x4417ee, ISR event-get/clear, transport receive, and application service children remain true code contracts.

The native 0x5fa0a4/0x5fa0ba pair was reidentified as BASEPRI mask/restore with DSB/ISB, rather than a generic assertion. `event_get_isr.c` reconstructs native 0x47ed64 using those architectural operations around the event word read. `verify_audio_uart_event_get_isr.py` passes 16/16 original-byte/C cases comparing returned bits and restored BASEPRI across four initial masks. This correction applies to the ISR getter; invalid-argument branches elsewhere still need their full native fatal-store behavior modeled through an explicit contract, not a blanket mapping of 0x5fa0a4 to `offline_assert`.

`event_clear_isr.c` reconstructs native ISR-clear wrapper 0x47ed52, timer-pend bridge 0x47eb4a, and 0x47ee28 callback. It queues the four-word message `{-2, callback, event, flags}` through the already selected `opencfw_event_queue_send_isr` (native 0x441952) and the existing typed daemon queue handle at 0x20074ab0. `verify_audio_uart_event_clear_isr.py` passes 8/8 original-byte/C comparisons for queue argument, normalized callback pointer, full message, wake/position parameters, and return. Cortex-M55 `-O2 -Wall -Wextra -Werror` compilation and partial link pass without duplicates. ISR event clear and getter lower code now close against selected queue/mask providers; daemon queue initialization and interrupt runtime remain unqualified.

`process_receive.c` reconstructs native 0x45d4dc `SyncModuleReceivedDataHandler`: it forwards buffer/length to the product module handle at 0x200749c4 when initialized, and otherwise emits authenticated extended/compressed diagnostics under the native flag checks. `verify_audio_uart_process_receive.py` passes 40/40 controlled original-byte/C cases for handle present/absent, five log masks and four lengths, comparing ordered calls and genuine argument registers. Cortex-M55 `-O2 -Wall -Wextra -Werror` compilation passes. The module handle and five diagnostic strings are typed product imports; the module receive child 0x491b9a remains a true code contract.

`process_event4.c` reconstructs native 0x45d4b8 semaphore drain: zero-time take on the typed handle at 0x200749d4, followed by module pump on the typed handle at 0x200749c4 until take returns nonzero. `verify_audio_uart_process_event4.py` passes 5/5 controlled original-byte/C sequences spanning zero to five successful takes and comparing ordered lower call arguments. Cortex-M55 `-O2 -Wall -Wextra -Werror` compile passes. Semaphore take and module pump remain real lower code contracts; live loop progress depends on external scheduler/hardware state.

`service_handshake.c` reconstructs native 0x584e94: builds the 10-byte local packet with six transmitted bytes `55 04 12 34 56 78`, sends channel 0xff with size 6, flags 0 and timeout 5 through the genuine 0x465480 child. `verify_audio_uart_handshake.py` passes its original-byte/C comparison of the entire 10-byte packet and all child arguments. Cortex-M55 `-O2 -Wall -Wextra -Werror` compile passes. The send child's hardware/protocol implementation remains a distinct code contract.

`sync_callback.c` reconstructs native 0x5417a4 receive callback: writes incoming bytes through the transport handle at 0x20074b14 with zero timeout/wake word, then sets event bit 1 on the handle at 0x20074b10 through the already selected 0x4495e4 provider. `verify_audio_uart_sync_callback.py` passes 5/5 controlled original-byte/C comparisons over lengths 0–1024, including write child register/stack arguments, initialized wake word, and signal arguments. Cortex-M55 `-O2 -Wall -Wextra -Werror` compile and partial link pass. The transport write lower 0x57e05e remains a true code contract.

The combined local UART source graph (thread plus all current lowers) partial-links with the latest unified Main candidate without duplicate definitions and has 154 unresolved names, versus 107 before the UART thread was exposed. Twenty are currently named UART true-code lower contracts: handshake send, module pump/receive, event2 processor, queue send, readiness, semaphore take, seven remaining service-prepare calls, three sync-reset calls, and transport receive/write. The rest are existing Main imports and newly exposed typed product data. Counts are hash-bound to this local partial link and are not a target image link or complete firmware estimate.

`service_announce.c` reconstructs native 0x4ac828 UART service announcement: zeroed eight-byte packet and four-byte nonce, version-dependent mode byte, checksum/copy into packet tail, then channel 0x81 send with size 8/flags 0/timeout 5. `verify_audio_uart_service_announce.py` passes 12/12 original-byte/C cases spanning command/version branches with controlled nonce/checksum providers, comparing child call order and the complete transmitted packet. Cortex-M55 `-O2 -Wall -Wextra -Werror` compilation passes. Three genuine lower code calls remain: version 0x45a568, nonce 0x4ac776, checksum/copy 0x439be4, plus the already exposed handshake send 0x465480.

The announcement version child 0x45a568 reads the exact same product byte at 0x20075024 as the already reduced service-mode getter 0x45a570. `service_small.c` now defines `audio_uart_service_version` from that typed cell; `verify_audio_uart_service_version.py` passes all 256 byte values against the original body. Cortex-M55 `-O2 -Wall -Wextra -Werror` compile passes. The announcement version child is closed; nonce, checksum/copy, and send remain.

`service_nonce.c` reconstructs native 0x4ac776 four-byte copy from typed product RAM at 0x20074928, including null-output `UINT32_MAX`; `verify_audio_uart_service_nonce.py` passes 8/8 original-byte/C cases. `byte_copy.c` supplies the caller-used byte effects of native compiler helper 0x439be4; `verify_audio_uart_byte_copy.py` passes 224/224 alignment/length cases for destination bytes. The UART caller ignores r0, and native r0 varies by alignment path, so the candidate declares this helper `void` and does not claim its full return-register equivalence. Both compile Cortex-M55 `-O2 -Wall -Wextra -Werror`; the announcement's nonce/copy children are closed for its call domain, while packet send remains open.

A fresh compile of all 18 C files in `uart_thread_source_candidate` with Cortex-M55 `-O2 -Wall -Wextra -Werror`, followed by relocatable link against `auxiliary-transition-audio-formatter-integrated-round/apollo_main/candidate.o`, passes without duplicate providers. The current local graph has 154 unresolved names; 19 are still named `audio_uart_*` lower code contracts, including transport receive/write, readiness, queue send, semaphore take, application module receive/pump/event2, six remaining service preparations, three sync-reset children, and handshake send. These are dependency frontier counts, not whole-image completion.

`ring_available.c` now reconstructs native ring used-byte helper 0x57e38c and writable-space helper 0x57e028, including wrap arithmetic, one-byte vacancy, and the stable-head retry. `verify_audio_uart_ring_available.py` and `verify_audio_uart_ring_space.py` each pass 64/64 original-byte/C index/capacity cases. Both compile Cortex-M55 `-O2 -Wall -Wextra -Werror`. The writable helper's null-descriptor fatal branch remains the existing nonreturning `offline_assert` contract; concurrent producer/consumer mutation is not exercised by the static fixtures.

## UART ring copy and transfer source reduction (2026-10-11)

`uart_thread_source_candidate/ring_copy.c` reduces native Apollo helpers
0x57e268 and 0x57e2f6 to C, preserving the descriptor capacity at +8,
storage pointer at +24, split wrap copy, and returned index. The valid-input
original-byte/C oracle `verify_audio_uart_ring_copy.py` passes 496 comparisons
of return value, source and destination buffers. It does not exercise native
fatal invalid-input paths or concurrently mutating ring state. The selected
byte-copy C provider implements caller-observed byte effects; native R0 on
some copy paths is deliberately outside its void signature.

`uart_thread_source_candidate/ring_transfer.c` reduces native helpers
0x57e0f0 and 0x57e220, including the framed four-byte length header and
index commit. `verify_audio_uart_ring_transfer.py` passes 102 valid original
byte/C comparisons of return, descriptor, and buffers. Framed read is not
qualified because available retained test fixtures decode a native header
length beyond the valid ring payload range; creating an attributed valid
header fixture is still required. The C source is experimental, not an
unqualified stock equivalent.

All 21 UART candidate C files currently compile with Clang Cortex-M55,
`-O2 -Wall -Wextra -Werror`. A partial relocatable link with the latest
available root Apollo candidate succeeds with zero duplicate strong symbols
and 154 unresolved names; the root base has 107. New typed children and
product state account for part of the increase, so unresolved symbol count
is not a count of remaining independent bodies. The outer transport send and
receive wrappers, UART module pump/receive and semaphore paths, product data
initializers, target image placement, and live hardware still remain open.

## UART transport wrappers and notify-state lower (2026-10-11)

`uart_thread_source_candidate/transport_io.c` reduces original Apollo
0x57e05e write and 0x57e136 receive. It composes the selected ring-space,
ring-transfer, and ring-available providers; it preserves write threshold
notification, receive timeout registration, conditional scheduler blocking,
and read-side task notification. Authenticated child addresses bind to the
already-selected C providers `uart_notify_isr` (0x455dc0),
`audio_notify_task` (0x455c48), `audio_notify_wait` (0x455b84),
`receiver_current_task` (0x45589c), and scheduler/port entries. The new
`notify_clear.c` implements 0x455f5e using the native 0x6c task-state byte
and selected critical sections. The sync callback declaration was corrected
to the native four-argument write ABI; its five original-byte cases still
pass.

`verify_audio_uart_transport_io.py` passes 112 original-byte/C comparisons
of return value, descriptor, and buffers, with zero timeout, controlled ring
states, threshold branches and bounded notification child cuts. Actual
scheduler blocking, nonzero timeout, notification side effects in the full
selected children, concurrent ring mutation and framed read are not covered.
`verify_audio_uart_notify_clear.py` passes all 256 task-state byte values
with explicit task handle and critical-section children cut at their native
entry. Both source files are experimental reductions, not full firmware or
hardware equivalence claims.

All 23 UART candidate C units compile Cortex-M55 `-O2 -Wall -Wextra -Werror`.
Partial relocatable link with the latest available root Apollo candidate
passes with zero duplicate strong names and 152 unresolved names. The
remaining `audio_uart_` named code frontier in that snapshot is 18 lowers:
handshake send, module pump/receive, event2, queue send, ready, semaphore
take, service prepare 0/4/5/6/7/8/9, and sync reset 0/1/2. It excludes
non-UART lower imports and typed product cells, so it is not a full-image
remaining-body count.

## UART framed read and TinyFrame queue/timer chunk (2026-10-11)

A valid TinyFrame frame header fixture showed that `ring_transfer.c` had
mistakenly reused the header output word as the previous ring-available
count. It now keeps the pre-header count separately, then limits copied
payload bytes by the decoded header and requested size. Native-byte/C
comparisons pass 126 ring-transfer fixtures and 136 outer transport
fixtures, including framed reads whose four-byte header crosses the ring
boundary. These remain bounded: timeout blocking, live notification effects,
and hardware are outside the fixture.

The native queue-send entry 0x4417ee is the selected pinned FreeRTOS
`xQueueGenericSend` body; `queue_send.c` exposes its UART caller name with
the same four-argument ABI. The CMSIS semaphore-acquire entry 0x44994e is
the selected full `audio_semaphore_acquire` C body; `semaphore_take.c` exposes
the UART caller name with its two-argument ABI. Prior queue and semaphore
closure receipts qualify their selected bodies; these bridges add no new
independent implementation claim.

`module_tick.c` reconstructs the full loop of native TinyFrame feed0x491b9a
and timer pump0x492288. The pump's saturating 16-bit tick at +0x12,
8-bit slot count at +0x7158, 24-byte timer stride, active/countdown fields,
callback, and expiry child correspond to the native body. The bounded
`verify_audio_uart_module_tick.py` original/C oracle passes42 cases,
comparing feed calls, counter bytes, and timer-expiry call order. Callback
non-null execution and actual expiry child effects remain typed contracts.

All 26 UART candidate C units compile Cortex-M55 `-O2 -Wall -Wextra
-Werror`; partial link with the latest available Apollo root candidate has
zero duplicate strong providers and 150 unresolved symbols. Current
`audio_uart_` named code frontier has 15 lowers: handshake send, feed byte,
timer expire, event2, ready, service prepare 0/4/5/6/7/8/9, sync reset
0/1/2. This excludes non-UART providers and product data contracts.

## TinyFrame parser and timer expiry source reduction (2026-10-11)

`module_expire.c` reduces native0x49183e. It clears the timer callback and
counter fields, decrements the last-slot count, and passes the three
stock-written callback record fields. The remaining record bytes are opaque
because the native routine does not initialize them. Bounded original-byte/C
checks pass60 cases, including12 callback cuts comparing record fields.

`module_parser.c` reduces the 756-byte native0x491be4 state machine plus its
46-byte start helper0x491bb6. It implements all parser states0-6,
saturating timer reset, header/body CRC16/ARC, oversized payload drop,
frame-complete dispatch and diagnostic branches. The CRC recurrence follows
the authenticated A001 table contract; no stock lookup table was copied.
`module_strings.c` defines11 original text literals read through the
authenticated ROM pointers0x491ee4..0x491f50. The native/C oracle passes
1040 bounded cases: 1024 parser-state/CRC comparisons and16 diagnostic
paths with flags1/2/4/7, including literal text and logger ABI arguments.
The parser's scratch R0 return is not modeled because its only selected
caller ignores it. Actual frame dispatch0x4919e8, callback effects, multi-byte
stream composition and hardware execution remain open.

All29 UART candidate C units compile Cortex-M55 with warnings as errors.
Partial link with the latest available root Apollo candidate has zero
duplicate strong providers and149 unresolved symbols. The UART named code
frontier currently includes14 entries: handshake send, parser frame done,
event2, ready, service prepare0/4/5/6/7/8/9, and sync reset0/1/2.
Product state and other Main image imports remain separate.

## TinyFrame frame dispatch (2026-10-11)

`module_dispatch.c` reduces native0x4919e8. It constructs the native
24-byte message record, searches timer, type, and global listener tables,
restores callback-owned context, handles timer reload and listener removal,
and calls the selected timer-expiry reduction. Three unhandled-message
strings are authenticated against ROM pointer entries0x491f24/28/2c and
supplied by `module_strings.c`. The original-byte/C oracle passes32 bounded
scenarios covering no listener, timer/type/global listeners at slots0/1,
and callback results0/1/2/3. Callback bodies and timer-expiry child effects
are cut at their actual entry points; this is not a whole stream or live
hardware qualification.

All30 UART candidate C units compile Cortex-M55 with warnings as errors;
partial link with the latest available root Apollo candidate has zero
duplicate strong providers and148 unresolved symbols. UART named code
frontier is13: handshake send, event2, ready, service prepare0/4/5/6/7/8/9,
and sync reset0/1/2. Product state contracts and the wider Main image still
remain open.

The legacy advertising connected code paths are now source-defined through
`appSlaveAdvMode` 0x4b2bde, `appSlaveAdvStart` 0x4b446a,
`AppDbCheckBonded` 0x47a600, stop/restart callbacks 0x4b2afe/0x4b2b90,
and leg start/type-change/next-state 0x4b2a04/0x4b2a92/0x4b2aaa.
Actual compiled-C/native scripts compare 5 mode, 4 start, 3 database,
8 callback and 7 state cases. The product non-auto bondability write and
warning dispatch were verified against native branches. The coherent Main
`peripherals-app-slave-callback-state-round` receipt passes with 2475
definitions, 807 mixed unresolved and zero duplicate strong, SHA-256
`59d0140b4d9bc65bf83620b370620c4f54198e8d8dd49f92f01f76c51ddea925`.
No direct `appSlaveAdv*` code import remains in this connected graph.
The product-added transition flag, timer, handler ID, live state and
advertising profile table still require source ownership/placement proof.

The product BLE advertising initializer `_bleAdvInit` 0x46db04 is now a
complete native-backed C body for test and normal modes, configuration
fields, four advertising data setters, random address, address type, start
and bondable flag. All four actual C/native cases pass, including the
diagnostic branches with authenticated literal contents. Its descendants
`AppAdvSetData` 0x4b2cec, `appAdvSetData` 0x4b4240,
`DmDevSetRandAddr` 0x4b304c, `DmAdvSetAddrType` 0x4b32b8 and
`HciLeSetRandAddrCmd` 0x52b4ba have actual C/native PASS8, PASS2 and
PASS2 across packet/state/lock cases. Product `appSlaveConnOpen` 0x46de78
has actual C/native PASS4 pointer and diagnostic effects.

Six slave pointer cells at native RAM 0x20074328, 0x2007432c, 0x20074330,
0x20074334, 0x2007434c and 0x20074350 now have 4-byte ARM BSS source
definitions. Selected `APP_SlaveHanderInit` writes five; the native-backed
connection-open provider writes the sixth. Absolute placement and startup
zeroing remain external image gates. Coherent Main
`peripherals-adv-pointer-cells-round/receipt.json` passes with 2488 defined,
799 mixed unresolved and zero duplicate strong, SHA-256
`97a5efeb6bce8be09fd952272f5812321fd35982730ea510846eafb34d3e86ab`.
Advertising config/name RAM and app timer/handler cells remain authentic
data obligations, with other Main interfaces and final firmware proof open.

The next Cordio advertising descendants are source-defined: `appAdvStart`
0x4b42f0 with its product OTA gate and independently evaluated capacity
queries; `DmAdvStop` 0x4b3250; `DmAdvStart` 0x4b31ea;
`DmAdvSetInterval` 0x4b3292; `DmAdvConfig` 0x4b3166; and
`appSetAdvScanData` 0x4b3514. Actual compiled-C/native bounded checks pass
3, 4, 6, 2 and 8 cases across these units. The capacity-query oracle
caught and corrected a short-circuit discrepancy. The application slave
profile pointer at native RAM 0x20074350 uses the existing
`audio_ble_slave_profile_slot` written by the selected slave initializer;
the profile table itself remains an unresolved data contract. The coherent
`peripherals-app-adv-scan-config-round` target receipt passes with 2461
defined, 809 mixed unresolved and zero duplicate strong, SHA-256
`625ea7047c9754ca5e1ba2755a03548cedfaf169905e6f61061f9f3f30c3fb30`.
Direct remaining connected code is `appSlaveAdvMode`,
`appSlaveAdvStart`, `appSetAdvScanDataFrag`, `appSlaveConnectableAdv`,
`appNumConns`, `DmAdvSetData` and their genuine descendants; RAM/profile
data and final image/runtime gates are separate.

## UART sync reset and setup (2026-10-11)

`sync_reset.c` reduces native0x584bc0/0x584c8c/0x584db6. It conditionally
creates the semaphore and mutex, binds the transport driver, configures the
two pins, buffer, mode, baud, and HAL sequence, installs the callback cell,
and restarts the receiver. ROM words0x78f108 and0x78f10c both hold pin
configuration4. The pin-function child0x480f0c is already selected as
`g2_codec_pin_function`; the source now binds directly to that provider.
`verify_audio_uart_sync_reset.py` passes13 controlled original-byte/C cases
for callback installation, restart, handle presence and bind success,
comparing return, product cells and typed child call order. Driver/HAL
operations and actual scheduler/hardware effects are child cuts, so this is
experimental source coverage. Configuration cells at0x20074610/18/1c/20,
0x20074fc9 and buffer0x20000d9c remain typed product data contracts.

`service_prepare4.c` reconstructs the 44-byte native0x471528 RPC initial
sync request. Authenticated Thumb disassembly resolves the fifth send
argument omitted by the decompiler: timeout5 is stored at SP before the
call0x465480. The full call is channel0x20, ten-byte zeroed local packet
starting `{2,0}`, transmitted length2, flags0, timeout5.
`verify_audio_uart_service_prepare4.py` passes its bounded original-byte/C
child-call comparison, including packet bytes and stack timeout. The send
child remains a true code contract.

`service_prepare5.c` reconstructs native0x47e4a6 onboarding flag RPC. The
six-byte getter0x4a7832 reads typed product RAM0x20000040; the two-byte
packet `{0x0d,flag}` is sent on channel0x10 with flags0 and timeout5.
The module, source, function and format strings are exact text reached from
authenticated ROM pointers0x47e620/24/50/54/58. The original-byte/C oracle
passes15 cases across flags0/1/255 and logger masks0/1/2/4/7, comparing
send arguments and packet plus extended/compressed diagnostic arguments.
The send child0x465480 remains open.

`service_prepare6.c` reduces native0x47d818 ring-status peer sync. It
branches on authenticated getters0x4a2fdc/0x4a2914, calls idle or active
sync0x47cf28/0x47ced6, and preserves the log-disabled/extended/compressed
paths with exact text from ROM pointers0x47d914/18/b4/b8/bc.
`verify_audio_uart_service_prepare6.py` passes20 original-byte/C comparisons
across ready, active and logger-mask states. Getter/action effects remain
typed child contracts.

`service_prepare7.c` reduces native0x4ff99a ring-battery request. It sends a
12-byte zeroed packet headed `{6,0}` on channel0x105 via child0x4651e0,
then follows the native success/failure log branches. Seven diagnostic
strings are exact text read through authenticated ROM pointers0x4ffa4c..6c.
`verify_audio_uart_service_prepare7.py` passes15 original-byte/C cases for
send results0/1/UINT32_MAX and logger masks0/1/2/4/7, comparing packet and
logger ABI. Send side effects remain a typed child contract.

`service_prepare9.c` reduces native0x501066 dashboard slave report. It
checks selected service version2, tests PB-file presence0x55876a, optionally
runs native vTaskDelay0x454b4c(100), sends a six-byte message through
0x465480 with timeout5, and emits authenticated diagnostics. The packet
normalizes existence to Boolean while the log passes the raw getter byte;
the oracle found and corrected this difference. The five static strings
match ROM pointers0x501184/88 and0x501814/18 plus0x501d0c.
`verify_audio_uart_service_prepare9.py` passes90 original-byte/C cases
across mode1/2/3, getter0/1/5, delay0/1 and log masks0/1/2/4/7.
The PB getter, delay and send implementations remain child contracts.
# UART semaphore constructor continuation (2026-10-11)

`g2/components/audio/uart_thread_source_candidate/semaphore_new.c` now
contains the complete CMSIS `osSemaphoreNew` decision tree at native
`0x44989a`: interrupt rejection, parameter and attribute validation,
static/dynamic binary and counting creation, initial binary give with
failure deletion, and initial counting value at the authenticated queue
control offset `+0x38`. All children bind selected FreeRTOS source providers.
The new file compiles for Cortex-M55 with clang `-O2 -Wall -Wextra -Werror`
and links relocatably with the previous UART candidate without duplicate
symbols. This is source/ABI reduction, not yet an original-byte execution
oracle for every creation and allocator path. The direct UART named-symbol
frontier decreases from 22 to 21; `audio_uart_ready`,
`audio_uart_process_event2`, `audio_uart_service_prepare0/8`, the two
send cores, and hardware driver children remain genuine code work. The
latest independently available whole-Main receipt is
`auxiliary-transition-audio-formatter-integrated-round` with 107 imports;
it predates this UART addition and must not be conflated with the local
frontier or firmware completeness.

The same round adds `service_prepare0.c` (`0x444720`) and `ready.c`
(`0x45e8d0`). Both compile with Cortex-M55 clang at `-O2 -Wall -Wextra
-Werror` and link with the local candidate without duplicate symbols.
Authenticated ROM templates establish `DispQueue`, static queue dimensions
`96 × 12`, `ui_task` stack size `0xc000`/priority `0x2c`, and
`sync_data_queue`, static dimensions `150 × 4`. The latter preserves master
and slave listener registration order, startup and failure diagnostics, queue
creation, poll-thread startup, and timeout timer. Product RAM buffers/control
blocks stay typed externs. Lower display initialization, TinyFrame creation,
listeners, poll/thread/timer setup, and hardware effects remain separate
source contracts. No original-byte execution claim is made for these two
larger constructors.
After these two constructors, the local UART object has 33 unresolved
`audio_uart_*` names because their genuine display/TinyFrame/listener/poll/
timer children are now exposed. Its complete undefined set has 187 distinct
names, including product data and the stale root base. Raw imports are not a
monotonic body-completion measure.

`process_event2.c` now reduces native `SyncModuleSendDataHandler` at
`0x45e664`: nonblocking queue drain, null-message diagnostics, 24-byte
TinyFrame send-frame fields, all five message-type callback pairs in the
native branch order, listener failure cleanup through the selected
mutex-owned file/TLSF heap free, multipart payload and close, and the
architectural assertion mask prefix for invalid types. Its direct CMSIS
queue-get lower `0x449b3c` is now implemented in `queue_receive.c` against
selected FreeRTOS task and ISR receive providers, including ISR yield bit.
Both new units compile and join the local Cortex-M55 relocatable candidate
without duplicate strong symbols. This is native-pseudocode/ABI source
qualification; bounded original-byte execution for the long send loop and
real scheduler/heap effects remains outstanding. The local named UART import
frontier is now 46 because ten callback bodies and multipart children are
exposed, while the `process_event2` and queue-get outer bodies are closed.

`pb_file_exists.c` additionally reduces native `0x55876a` with authenticated
ROM path `/configure/dashboard_ext.proto`, mode `rb`, and both diagnostic
branches. It closes the direct `audio_uart_pb_file_exists` import; the real
file-open body at `0x474550` is an exposed code lower and selected file-close
is reused. Cortex-M55 Werror compile and local relocatable link pass. The
local `audio_uart_*` count is 45 after this provider; the whole Main count
still requires the coordinator's fresh integrated receipt.

`alloc_retry.c` reduces native `CommonMalloc` `0x4646f0` to ten selected
mutex-owned allocator attempts with exponential CMSIS delays and exact ROM
retry diagnostics. `send_core.c` reduces both native `SendDataToPeer`
`0x4651e0` and `SendDataToPeerExt` `0x465480`: authenticated 12-byte node,
8-byte protocol header, length truncation, payload copy, 2000-tick CMSIS
queue enqueue, event bit 2, failure frees through selected file/TLSF heap,
and all diagnostic branches. The fifth extended argument is the two-byte
event type in the payload header. These two units compile with Cortex-M55
clang Werror and join the local relocatable link without duplicates. The
local `audio_uart_*` frontier decreases to 43 named imports, still exposing
the real callbacks, multipart children, HAL drivers, and product data.
No stock execution equality or live UART behavior is inferred from this
compile/link result.

`sync_hal.c` closes four native sync children: NVIC IRQ enable
`0x5849d4`, disable `0x5849f2`, priority write `0x584a10`, and UART
finalization `0x584df4`. The MMIO bases are authenticated ROM literals
`0xe000e100`, `0xe000e280`, `0xe000e400`/`0xe000ed18`; finalization uses
ROM pin functions `3` and `0xe083`. Cortex-M55 Werror compile and local
relocatable link pass without duplicates. The local named UART frontier
falls to 39; remaining sync driver bind/mode/buffer/prepare/baud are true
code, while product handles and MMIO runtime effects are unverified.

`sync_driver_basic.c` reduces native Ambiq UART state bind `0x58dae4`
and IRQ enable register update `0x58e782`, including all invalid-handle
status returns, four-instance state reset, ROM handle magic `0x1ea9e06`,
and MMIO base `0x40039000`. The state slab at RAM `0x2006a02c` remains a
typed product data contract. Cortex-M55 Werror compile and local link pass;
the named UART frontier decreases to 37. No physical UART access or full
driver coverage is claimed.

`sync_driver_prepare.c` reduces optional DMA callback preparation
`0x58ddd6` with typed DMA child `0x53006c`. The caller `sync_reset.c` now
declares the full five-word native ABI and passes zero for both optional
channels on its startup path. The active-channel DMA child remains a code
lower, without a hardware-equivalence claim. Both changed C units compile
Werror. The exact fifth-word forwarding is established below.

**Whole Main versus local UART:** the newest independently available
`radio-callback-inventory-all-six-round/receipt.json` reports Main candidate
compilation true, 192 unresolved symbols (33 named `audio_uart_*`),
`source_complete=false`, and `full_payload_linked=false`. That receipt
predates at least the latest local UART source additions. The current local
UART candidate has top-level ready/event2/prepare0/send cores reduced but
continues to expose callback, TinyFrame multipart, display setup, driver,
file-open, product-data, and other code contracts. It cannot be counted as
a whole Main image or bootable firmware.

Native Thumb instructions settle the optional DMA fifth word:
`0x58de1c` loads `[sp,#0x10]`, checks it, and forwards it in `r3` to
`0x53006c` for the TX channel. The startup call at `0x584c44..0x584c50`
stores zero to `[sp]` and clears `r1`/`r2`/`r3`, so the five-argument
`sync_reset.c` call is ABI-correct for that path. `sync_driver_mode.c`
reduces native `0x58dbb8` mode0/1/2 state save/restore, MMIO,
revision-gated register bit, and peripheral power flow. Pin-mux enable/
disable children `0x4c44bc`/`0x4c4530` remain typed code imports.
Cortex-M55 Werror compile and local link pass; physical MMIO behavior and
all backup/revision cases have not been compared against original execution.

`module_new.c` closes three TinyFrame bodies: `TF_InitStatic`
`0x491752`, `TF_Init` `0x4917d2`, and `TF_AddTypeListener` `0x491962`.
It preserves the native 0x7160-byte allocation/zeroing and two retained
words, master byte, sentinel words, 32-slot type-listener scan, high-water
mark, and exact error diagnostics from ROM. The allocator binds selected
`codec_allocate` at `0x474cd2`. Cortex-M55 Werror compile and local link
pass with no duplicate provider; local named UART imports decrease to 36.
Allocator state and complete TinyFrame runtime remain unverified.

`module_multipart.c` reduces the TinyFrame wrapper chain
`0x492200/0x49224c/0x492266/0x492278/0x492280`. Native Thumb shows the
fifth timeout halfword is forwarded through the two stack wrappers; the
0x492266 entry clears frame payload at `+8` before begin and sends inline
payload/close only if the frame has zero size or a nonnull payload. The
actual begin/payload/close engines (`0x4920aa`, `0x492114`, `0x492198`)
remain typed code children. Cortex-M55 Werror compile and local link pass,
zero duplicates. Named UART import count stays 36 as three wrappers expose
three real engines.

`module_begin_core.c` reduces TinyFrame TX claim `0x4916c8`, ID-listener
registration `0x4918c2`, the nine-byte header writer `0x491f54`, and begin
engine `0x4920aa`. It preserves the 128-slot listener records and timeout,
send-lock byte, frame ID generation, CRC16/ARC header and native error
diagnostics. The CRC recurrence shares the previously authenticated
`0xa001` polynomial/table and parser proof. Cortex-M55 Werror compile and
local link pass, no duplicates; named UART imports decrease to 35. The
remaining TinyFrame payload/close engines and physical transport flush
still require source/runtime qualification.
`verify_uart_tinyframe_header.py` now executes original `0x491f54` under
Unicorn and the compiled C begin engine with the same module/frame fields.
It passes 256/256 combinations of master role, prior frame ID, explicit/
automatic ID, payload size, and message type, comparing all nine emitted
header bytes plus updated module/frame IDs. This specifically qualifies
the header writer, not listener scheduling, payload output, or transport.

`module_payload_close.c` now reduces the payload engine `0x492114`,
byte-copy/CRC `0x492032`, footer `0x49207a`, close engine `0x492198`, and
flush wrapper `0x4d9522`. The real sync UART send at `0x541790` is an
explicit child. `verify_uart_tinyframe_payload.py` passes 84/84
original-byte/C comparisons spanning initial buffer occupancy,
zero/short/multi-buffer payloads and CRC footer on/off. It compares the
module state and captured flush bytes, with only the physical UART flush
call replaced by a capture return in both executions. Cortex-M55 Werror
compile and local link pass; named UART imports decrease to 34. This
qualifies the bounded TinyFrame buffer/CRC behavior, not device I/O.

`sync_send.c` and `sync_write.c` reduce the UART physical-send wrapper
`0x541790` and full DMA write control `0x584c98`, with local reductions of
DMA stop/start `0x584a64`/`0x584a38` and status `0x58e754`. Native Thumb
confirms the wrapper forwards only the first two caller words to the write
body. The C body preserves input/state guards, 0x400-byte TX limit,
selected mutex/semaphore operations, tick/copy, cache clean with DSB/ISB,
DMA registers, timeout and error cleanup, and bounded status polling.
TX storage at RAM `0x20379da0`, handles, and error byte remain typed
product data. Cortex-M55 Werror compile and local relocatable link pass;
named UART imports decrease to 33. Real DMA, cache, scheduler, and UART
effects have not been tested on hardware or compared under an MMIO oracle.

`sync_driver_buffer.c` reduces native Ambiq UART configuration
`0x58e09e`: handle validation, clock-mode/revision gate, pin-mux choice,
divider request, framing parity/stop fields, and UART MMIO register
sequence. It reads only authenticated offsets from the product config
pointer passed by `sync_reset.c`; actual contents at RAM `0x20000d9c`
remain a typed data contract. The divider body `0x58de38` and pin-mux
enable `0x4c44bc` remain true code children. Cortex-M55 Werror compile
and local link pass, zero duplicates. Named UART import count remains 33
because the body exposes its divider lower.

`sync_driver_divider.c` reduces native baud divider `0x58de38` for six
authenticated clock modes with ROM frequency/status words, integer and
fractional MMIO registers, and actual-rate output. It compiles and links
locally on Cortex-M55 without a new unresolved division helper; named
UART imports decrease to 32. Valid nonzero requested baud is the source
qualification domain. Native behavior for a zero divisor and all physical
clock configurations remains unverified.

A fresh local build compiles all 56 UART candidate `.c` files with Cortex-M55
clang `-O2 -Wall -Wextra -Werror`. The current root
`radio-callback-inventory-all-six-round` object already selects 39; linking
the 17 disjoint new files against that snapshot passes without duplicate
providers. That delta object has 195 distinct undefined names, 31 named
`audio_uart_*`. This count is a snapshot-dependent lower frontier, not
whole-image completion or a new six-image builder receipt.

The next UART chunk adds four source units: `task_delay.c` reconstructs
native FreeRTOS `vTaskDelay` at `0x454b4c`, using the selected suspend,
delayed-list, resume, and yield providers. It retains the authenticated
scheduler-suspended assertion and differs from the CMSIS `osDelay` IRQ
wrapper. `ring_active.c` reconstructs native owner-side predicate
`0x4a2914`; `ring_getters.c` provides its two six-byte product-state
getters at `0x466518` and `0x45a568`. `ring_sync.c` reconstructs the
8-byte status/query packets at `0x47ced6` and `0x47cf28` and calls the
already-selected request sender. Four units compile for Cortex-M55 with
`-O2 -Wall -Wextra -Werror`. Product context pointer, role byte,
status/query ROM templates, and live status word remain typed data
contracts. Native execution comparison for these units and full product
initialization remain open; this is source-defined reduction, not stock
equality or hardware qualification.

`display_setup.c` reconstructs the two native display startup outer bodies
at `0x444694` and `0x4446b4`. The second writes authenticated control
fields at offsets 0, 2, 12, and 16 before the native clock, pin, IRQ, and
start call sequence. Product board pointer and control RAM are typed data
contracts; eleven direct lower functions remain explicit code imports.
Five of its direct children are also reconstructed in the same unit:
board register write `0x44d254`, control reset `0x471cae`, enable-word OR
`0x471e92`, pin mode `0x442256`, and pin set `0x442238`. Six direct code
children remain; the IRQ-enable site `0x473934` binds the already-selected
`g2_codec_global_irq_enable` provider. The unit compiles for Cortex-M55 with
`-O2 -Wall -Wextra -Werror`. This removes two named UART code contracts
while retaining explicit remaining native children; there is no physical
display qualification.

The deeper display pass adds `display_control.c` for native channel
configuration `0x471c9a`/`0x471bca` and stop/pulse bodies `0x471dac`/
`0x471d58`. It preserves the observed register write sequence, channel
validation, 0/1/2 mode checks, IRQ save/conditional restore, and pin group
map; it binds selected `g2_gpio_critical_save`, privilege test, and
`audio_uart_pin_mux_disable` at `0x4c4530`. `display_init.c` reduces the
outer lock/display creation at `0x473928` and lock setup `0x4738a8` using
selected queue create/send providers. Both compile with Cortex-M55
`-O2 -Wall -Wextra -Werror`. MMIO base, format mask, lock cell, and
source-path data are explicit product contracts. `display_driver.c` adds
native display-driver construction `0x473782`: object allocation, pixel
format selection, 576-by-288 platform bind, failure log, draw buffer/flush
binding, surface creation, attach, mode, size, and origin in native order.
It compiles with Cortex-M55 Werror and leaves its allocators and platform
callbacks imported. Large LVGL initialization `0x473548`, LVGL logger
`0x44d25c`, and their descendants remain true code; compilation does not prove
display execution or stock behavior.

`service_prepare8.c` reconstructs native dashboard extension loader
`0x501d5c`: existence/open/seek/tell, nonempty 4096-byte maximum, read
and close, 16-byte protobuf stream setup, 188-byte decoded state, ready
flag, and all eight outcome-specific logging branches. It retains real
file and protobuf child imports. Schema, ROM path/mode and format literals,
and both product RAM buffers are typed contracts. `thread.c` now declares
the real 32-bit return ABI. Both compile with Cortex-M55 `-O2 -Wall
-Wextra -Werror`. Native parser execution and product file contents are
unverified, so this is a source-defined outer body, not a completed
dashboard service or stock-equal runtime.

`role_get.c` reconstructs native role-strap getter `0x45a578`, GPIO read
`0x480f8a`, and millisecond delay wrapper `0x4910f4`. It samples GPIO
0x9c five times with four 5-ms waits, returns 3 on read failure or
inconsistent samples, and stores role 2 for stable 1 or role 1 for stable
0. It retains the three diagnostic branches. GPIO register bases, pin
configuration, role byte, and ROM format strings are typed contracts.
Cortex-M55 Werror compilation passes; strap hardware and native execution
comparison remain unverified.

`send_timeout_end.c` reduces five native timeout callback bodies at
`0x45d710`, `0x45d9cc`, `0x45dc84`, `0x45df24`, and `0x45e5a4`, plus their
dispatch callback `0x45ade8`. It preserves callback-null, logging,
five-argument work submission with stack flag zero, status -2, and direct
callback fallback. `timeout_submit.c` reduces actual work submit
`0x491184` with its 20-byte queue item, 3000-tick mutex/queue sequence,
diagnostics, and native assertion/stop path on fatal queue failures.
`send_begin0.c` reduces native SlaveScheduleModuleDataCmd listener
`0x45daa0` with message offsets +8/+16/+20, event type 0x0b, callback
submission/fallback, and selected heap frees. All three compile with
Cortex-M55 `-O2 -Wall -Wextra -Werror`. Product queue state and ROM
diagnostic strings remain typed; there is no timer-worker runtime oracle.

The connected user-response branch now includes `send_begin_type1.c` for
native UserDataCmd listener `0x45d7e4` and `user_response.c` for allocator/
copy/enqueue `0x45a72c`, worker `0x45a6d0`, and 16-byte registered-listener
walk `0x442524`. The native ROM word at `0x45b130` was read as Thumb
address `0x45a6d1`, distinct from the end-listener dispatch at
`0x45ade9`. The scheduler item dispatch ABI was corrected to four words
with an opaque payload. Both files and the revised timeout callers
compile with Cortex-M55 Werror. Product registry data and log literals
remain typed; there is no live listener or stock runtime comparison.

`sync_timer_start.c` reduces native timeout-detection startup `0x45d34c`
and timer callback `0x45d302`: semaphore maximum 0xffff/initial 0,
periodic timer construction, 100-tick start, and callback release/event
bit 4. It preserves four diagnostic outcomes and compiles with Cortex-M55
Werror. The CMSIS timer constructor `0x4493b0` remains a genuine code
child. Product handle/event cells and ROM literals remain typed; timer
daemon execution is unverified.

`ring_mac_ready.c` reduces native `APP_MasterRingMacIsSet` at `0x4a2fdc`:
six bytes from the authenticated hand context +12, both three-byte
diagnostics, and the all-0xff absent sentinel. It compiles with
Cortex-M55 Werror. The hand-context pointer is already a typed product
contract; ROM log literals remain typed. MAC hardware state is untested.

`master_prepare.c` reduces native schedule-manager initialization
`0x45d1ec`: queue of 150 four-byte entries, 36-byte thread attribute
copy, scheduler thread creation, and queue/thread/success diagnostics.
`ready.c` now uses its 32-bit return ABI. Both compile with Cortex-M55
Werror. The scheduler thread `0x45c058` is a genuine remaining code
child; queue cell, attribute records, and log strings are typed product
contracts.

`dma_channel_create.c` reduces native six-word descriptor initializer
`0x53006c`: three zero words followed by configuration, enable, and
address. Cortex-M55 Werror compilation passes with no new imports.

`pin_mux.c` reduces native `0x4c44bc`/`0x4c4530` group dispatchers for
groups 0 through 6 and the pin<0x39 gate. It compiles with Cortex-M55
Werror and exposes 14 distinct, authenticated on/off lower functions
`0x4c3bfc`..`0x4c43ec`. Several lower groups have board pin, power,
and refcount effects, so the dispatcher is source-defined while the
connected pin-mux component remains incomplete.

`pin_mux_basic.c` reduces native bitset read/write helpers
`0x4c37a8`/`0x4c37fe` and group-0/1 on/off bodies `0x4c3bfc`,
`0x4c3c2e`, `0x4c3c60`, and `0x4c3ca2`. It preserves volatile register
updates, the group-1 capability gate, and selected IRQ/privilege behavior.
Cortex-M55 Werror compilation passes. Group-2 through group-6 control
still has distinct lower code and product state.

The same unit now covers native any-bit helper `0x4c377a` and group-3
on/off `0x4c3cd4`/`0x4c3d28`: capability check, selected pin function
0x0f active/idle configurations, bitset transition, and IRQ protection.
Group-2, -4, -5, and -6 lower bodies remain source work.

Group-4 off `0x4c4016` and its power-bit child `0x4d391e` are now in
`pin_mux_basic.c`, clearing the group bit under IRQ protection and
clearing product power bit 0 only when the group is empty. The product
power word is typed. Group-2 and groups 4-on/5/6 remain incomplete.

`send_begin4.c` reconstructs native PeerData listener `0x45d554`:
message payload/user-node validation, event byte 0x0d, diagnostics,
selected heap ownership release, and callback scheduling/fallback.
Cortex-M55 Werror compilation passes. The remaining original named
UART imports in the local component object are nine after this file;
this excludes new child code and product data contracts.

`send_begin3.c` reduces native MasterInputEventDataCmd listener
`0x45dd68`: event byte 8, packet fields +2/+4/+8, the actual input
event child `0x4445a4`, callback work submission/fallback, diagnostics,
and selected heap frees. It compiles with Cortex-M55 Werror. The input
event child remains a genuine unimplemented body.

`input_event.c` reduces that child at `0x4445a4`: ten-byte ID/two-word
record, selected mutex protection, native ring writer `0x46d8c4`,
12-byte queue notice type 7/length 10, and authentic fatal queue failure
path. Cortex-M55 Werror compilation passes. Ring write and display
failure reporting remain true lower code; product ring/queue/mutex cells
remain typed.

`input_ring_write.c` reduces native ring wrapper/core/free-space
`0x46d8c4`/`0x46d8e0`/`0x46da92`: capacity validation, one-byte gap,
truncation, wrap copy, write index, callback, and returned byte count.
Cortex-M55 Werror compilation passes. The bounded
`verify_uart_input_ring.py` executes the original bytes under Unicorn and
compares seven ring transitions with the source algorithm model: 7/7
pass. Two unsupported ARMv8-M LDA/STL instructions are interpreted as
ordinary word load/store; this comparison does not cover concurrency,
compiled-C equality, or physical hardware.

A fresh component-only sweep compiles all 81 UART candidate `.c` units
with Cortex-M55 clang `-O2 -Wall -Wextra -Werror` and links them
relocatably without duplicate globals. This object defines 153 global
symbols and has 318 distinct undefined names, including selected code
providers outside this component, newly exposed genuine children, and
typed product data. Eight original named UART imports remain:
`audio_uart_display_thread`, five ready-listener callbacks,
`audio_uart_poll_thread_start`, and `audio_uart_send_begin_type2`.
These counts are component-local and do not measure whole Main coverage.

The native shared reply listeners `0x45b588` and `0x45b6e4` now have
`listener_common.c`; the slave input listener `0x45b850` has
`listener_input.c`. Each checks the native high-byte command, emits the
native diagnostics from ROM-derived literals, builds the 24-byte TinyFrame
ACK descriptor, then dispatches the actual user response or input event.
The three new bodies compile with Cortex-M55 `-Wall -Wextra -Werror`.
A fresh relocatable link of all 83 UART candidate C units passes with no
duplicate definitions. Five original named UART imports remain:
`audio_uart_display_thread`, `audio_uart_listener_master0`,
`audio_uart_listener_slave2`, `audio_uart_poll_thread_start`, and
`audio_uart_send_begin_type2`. The real TinyFrame response lower native
`0x49225a` is now a typed code import; frame send descendants and stock
runtime comparison remain outstanding. No hardware equivalence is claimed.

`poll_thread_start.c` reduces native `init_thread_pool` `0x49137a`:
mutex creation, queue attributes, eight worker names and thread attributes,
partial-success policy, cleanup and logging. The ROM queue/thread templates
and RAM pool extents are typed extern data; worker execution, mutex delete,
and bounded formatter remain true code children. `listener_display.c`
reduces all four command branches of `SlaveDispalyCommandReplyListener`
`0x45adf4`, leaving its four display-processing children explicit.
`frame_response.c` now reduces the connected TinyFrame
`0x49225a`/`0x49223c`/`0x492200`/`0x4920aa`/`0x492114`/`0x492198`
response/setup/feed/finish path, exposing its authentic header, checksum,
output, check and reset children. These units pass the target clang Werror
compile. The response path is source-defined but not stock-oracle qualified.

`listener_master.c` reduces all native `0x45b14c` command branches,
the bytewise diagnostic loop, ACK and five genuine display/input children.
`send_begin_type2.c` reduces native `0x45e024` null-data, four display
response, missing-userdata, callback-submit/fallback, ownership-release,
and unknown-command paths. The latter shares the four display children
exposed by `listener_display.c`. Fresh component-only Cortex-M55 clang
`-O2 -Wall -Wextra -Werror` compilation passes for 88/88 C units;
relocatable link passes with 170 global definitions, 337 distinct undefined
symbols and no duplicate definitions. Only one **original named** UART
import remains, `audio_uart_display_thread` native `0x4437e0`. The 337
component undefined symbols include external selected code providers,
authentic newly exposed code descendants, and typed product RAM/ROM data;
they are not whole Main unresolved count. The display thread is a 419-line
retained decompilation with an infinite state loop, display buffer/queue,
power/brightness, audio/UI and callback transitions. It remains a full
body gap, not an aliasable one-call provider.

The TinyFrame path has since gained native `0x4916c8` claim,
`0x491722` release, `0x49172c` sequence, `0x491f54` header,
`0x492032` payload copy/CRC and `0x49207a` CRC append. The 256-entry
native CRC lookup table at ROM `0x6c0950` matches the reflected
polynomial `0xa001` algorithm for all 256 values; C computes the table
entry instead of copying a stock data blob. `verify_uart_frame_header.py`
compiles the actual C header with a host harness and compares five
controlled cases against authenticated original bytes under Unicorn:
**5/5 pass** for header bytes, descriptor ID, counter and return length.
This bounded comparison does not cover frame output transport or
concurrent TinyFrame operation.

`display_thread.c` reduces the retained native `0x4437e0` infinite
message/state loop, including start, refresh, exit, upgrade, input,
close-all, timeout, shutdown, driver-vtable, audio/brightness, and
diagnostic branches. It is a source-defined candidate with typed
product RAM cells and authentic external UI/hardware child contracts;
there is no stock runtime oracle for this full state machine yet.
`display_ring_read.c` reduces its native ring read/count path
`0x46d9ac`/`0x46d9c8`/`0x46dacc`; the bounded native-versus-source-model
`verify_uart_display_ring.py` passes **7/7** transitions. Unicorn
interprets two unsupported ARMv8-M LDA/STL instructions as ordinary
load/store, so concurrency and compiled-C equality remain unverified.
`display_registry_init.c` reduces native UI module registration
`0x4425a6`: 43 sixteen-byte ROM rows from authenticated
`0x6a44b0..0x6a4760` are capped at 128 and copied to RAM
`0x20066230`; the corresponding `user_response.c` declaration is now
a direct RAM array instead of a pointer object. `display_status.c`
reduces the status calculation/send native `0x47243a`; service and ring
children remain typed code imports. All new sources compile with
Cortex-M55 Werror.

Fresh UART component-only sweep after these additions: **92/92** C
translation units compile for Cortex-M55 with `-O2 -Wall -Wextra -Werror`;
relocatable link passes with **179** global definitions, **377** distinct
undefined names, and zero duplicate definitions. The eight original
named UART imports from the prior frontier are all defined, while newly
exposed native descendants and product layout/data contracts account
for much of the larger undefined count. The latest whole Main receipt
available at inspection (`channel-frontier-closed-all-six-round`,
2026-10-11T08:00:35Z) showed 363 unresolved names and still included
`audio_uart_display_thread`; it predates this source snapshot and must
not be used as a current whole-image frontier count.

The newer whole Main coordinator receipt
`segment-descendants-all-six-round/receipt.json`, captured
2026-10-11T08:32:08Z, reports **428** unresolved names. Parsing actual
component `extern` declarations classifies **97** as function contracts,
**328** as object/data contracts, and three unmatched names
(`am_hal_pwrctrl_periph_enable`, `am_hal_pwrctrl_periph_disable`,
`osEventFlagsSet`) as known function calls: approximately **100 code /
328 data** for that hash-bound snapshot. Within those, `audio_uart_*`
accounts for 59 code and 197 data; `g2_*` for 18 code and 128 data.
Data includes source-owned ROM strings, typed product RAM and hardware
configuration, and cannot be treated as a single missing configuration
block. The snapshot predates the newest display descendants below.

`display_timer_process.c` reduces native LVGL scheduler handler
`0x464344`: guarded reentry, timer list restart, remaining-delay scan,
utilization accounting and lock/unlock. It retains typed LVGL list,
clock, timer and logger children plus product RAM state. This target C
body has no bounded stock runtime comparison yet.

`display_timer_children.c` now reduces native LVGL list first/next
`0x482cd8`/`0x482cf0`, tick/elapsed `0x473482`/`0x4734a0`,
lock wrappers `0x49acba`/`0x49acc4`, timer remaining `0x46467c`,
and timer execution `0x464604`, including repeat count, callback,
delete/pause and scheduler restart flags. Lock core, timer deletion,
pause, LVGL logger and product LVGL state remain typed true contracts.
A fresh UART-only compilation passes **94/94** C units and relocatable
link passes with **188** defined globals, **384** distinct undefined
names and no duplicate definitions. The rising undefined count reflects
source reduction exposing real descendants, not regression in the eight
original named imports, which remain all defined.

The LVGL timer delete path now includes intrusive list removal native
`0x482c0e` plus its four link accessors, free wrapper `0x44f758`,
and the mutex-owned allocator release `0x484338`/`0x48429e`, reusing
selected FreeRTOS queue/semaphore and TLSF block/free providers. Pool
RAM `0x20000338` and static slot `0x2006f5ac` remain typed data.
`display_lvlog.c` reduces the native platform logger `0x44d25c`
and shared bounded `snprintf` wrapper `0x44b728` with the selected
`g2_log_vformat` body; arbitrary formatter grammar is still gated by
that underlying candidate. A fresh UART-only sweep compiles **95/95**
C units and relocatable-links with **195** global definitions,
**387** distinct undefined names, and zero duplicate definitions.
### LVGL recursive mutex lower closure

`display_timer_children.c` now contains native-derived bodies for mutex initialize
0x4d477a, double-checked critical-section ensure 0x4d47cc, recursive take
0x4d4666, and recursive give 0x4d4696. The two-word mutex cell remains a
typed product RAM import; creation uses the selected dynamic mutex provider,
and the take/give paths preserve the actual infinite wait, success test,
failure log, and return value. All 95 UART candidate C translation units
compile for Cortex-M55 with `-O2 -Wall -Wextra -Werror`; the local relocatable
link passes. This is source/native-static correspondence, not stock runtime or
hardware equivalence.

`display_ring_head.c` additionally reduces native list-head accessor 0x46cf56,
including its null-path extended and compressed diagnostics. The source
compiles for Cortex-M55 with warnings as errors. Its ROM log strings remain
typed imports. The larger constructor and initializer are addressed in the
subsequent font-chain section.

### LVGL font-chain constructor and initialization

Native disassembly/decompilation identifies 0x46cae0 as
`font_manager_create_chain`, 0x46d464 as `font_manager_init`, and 0x46d29a
as the font configuration loader. The legacy `audio_uart_display_ring_*`
candidate names arose from their display-thread call site; they describe
font-chain objects, not UART byte rings. Three new source units reduce these
bodies and the 0x46cfa6, 0x46d158, and 0x46d1c6 children. The constructor
retains zero/null/too-large checks, 12-byte list/node allocations, eight-item
limit, per-font creation/tracking/cleanup, linked `next` pointers, and failure
diagnostics. The initializer creates four-font background/foreground chains,
publishes both list and first-font pointers, and logs failures/success.

The authenticated `g2-2.2.6.10/ota_s200_firmware_ota.bin` SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`
maps native addresses to file offsets with base `0x437fe0`. ROM literal
pointers from the exact native pools were decoded to source-defined C strings
for the new font units, eliminating 48 literal imports. Remaining product
cells include list/head RAM `0x200746d4/dc` and `0x200746d8/e0`, four-entry
descriptor RAM `0x20002c48` and `0x20002c78`, active configuration RAM
`0x20002c00` and `0x20002c24`, byte flag RAM `0x20074fe3`, scratch RAM
`0x20324600`, and configuration records at `0x80100000`/`0x80700000`.
Those records/descriptors remain typed external data; no values were guessed.
The native font item create/release 0x4b1c9c/0x4b1ef6 remain genuine code
contracts. `display_font_flash_lock.c` reduces the configuration guard at
0x46f65e/0x46f674 and its mutex/power children 0x46f5a6/0x46f604,
0x46f52c/0x46f50c. Its authenticated literals identify the MX25U flash
driver, with device/mutex cells RAM `0x20074544/548` and sleep/mode bytes
RAM `0x20074fb9/b8`. CMSIS mutex calls bind to the selected
`audio_file_mutex_acquire/release` providers at 0x4497b6/0x44981c. The HAL
MX25U power operation 0x4c26e0 remains a genuine code contract.

The native callback pointer `0x46d239` in the first active config is a
previously unharvested 98-byte Thumb function at 0x46d238. Direct disassembly
shows a 512-entry, 40-byte-entry font glyph descriptor cache in RAM
`0x20324600`, gated by byte RAM `0x20074fe3`. `display_font_glyph_cache.c`
implements its direct, hit, and miss paths with the selected 32-byte copy
provider and a typed FreeType glyph descriptor lower 0x4b26a4. The latter's
602-byte native body reads glyph metrics and bitmap state, confirming this
callback is a glyph cache. `verify_font_glyph_cache.py` compares authenticated
original-byte execution with actual host-compiled C for cache disabled,
codepoint zero, hit, and miss; 4/4 pass including return code, output bytes,
cache entry, and glyph-lower call count. The underlying glyph descriptor
implementation remains a genuine code contract; no live rendering proof.
`display_font_glyph_descriptor.c` now reduces that 208-byte 0x4b26a4
descriptor body: codepoint nine maps to space, glyph index and optional
kerning are queried, glyph metrics/advance/bbox/bitmap mode are written to
the LVGL 32-byte descriptor, and a missing glyph returns zero. Its two native
lookup/kerning children 0x4b2774/0x4b28ee remain genuine code contracts.
`verify_font_glyph_descriptor.py` executes original bytes with controlled
children and compares four missing/normal/kerning/tab transitions against a
source-field model: 4/4 pass. The model is not compiled C, so descriptor
compiler/runtime equivalence is not established by this oracle.
`display_font_kerning.c` reduces native 0x4b28ee with its two sorted-pair
formats and class-matrix form. It performs the native byte/halfword pair
comparisons and signed kerning lookup directly, avoiding an opaque binary
search provider. `verify_font_kerning.py` executes authenticated original
bytes for six format-zero/format-one/class-matrix present and absent pairs;
6/6 match independently calculated expected values. This is native branch
qualification, not compiled-C equivalence. `display_font_glyph_index.c`
reduces the remaining 0x4b2774 cmap resolver, including direct ranges,
sparse byte maps, and both sorted 16-bit unicode list formats. The native
generic bsearch/comparator effects are written as typed C binary search.
`verify_font_glyph_index.py` runs authenticated original-byte fixtures for
all four cmap formats, present/absent entries, and out-of-range codepoints:
9/9 match the independently calculated source semantics. This is native
branch evidence; compiled-C and complete font-table equivalence remain open.

`display_font_create.c` and `display_font_delete.c` reduce native FreeType
create/delete outer bodies 0x4b1c9c (602 bytes) and 0x4b1ef6 (214 bytes).
They preserve input assertions and their actual native fatal loop, path-key
and cache lookup/create/release, descriptor allocation/layout, face size
selection, metric scaling, callback setup, and reverse cleanup. The font
chain constructor now calls these source-defined bodies. Their newly exposed
cache, allocator, face and scale helpers remain typed real code imports;
those descendants and successful creation/deletion have no bounded stock
comparison yet. The assertion loop represents observed native behavior, not
a substitute for an unimplemented success path.
`display_font_path.c` reduces native pathname retain/release 0x4b20d4
and 0x4b21a0: intrusive LVGL list search, pathname deduplication, refcount
increment/decrement, node removal, and native assertion branches. Existing
list traversal/removal and LVGL free providers are reused; node append,
pathname compare/duplicate remain genuine code children.
`display_font_callbacks.c` reduces native callback dispatcher 0x4b20aa:
common attach followed by bitmap or outline attach by descriptor mode. Its
three FreeType callback installers remain genuine children. Both files
compile for Cortex-M55; native runtime comparison for their successful paths
is pending.
`display_font_alloc.c` now reduces the LVGL nonzero/zero-size allocation
wrappers 0x44f718/0x44f730 and mutex-owned pool allocator 0x484180,
reusing selected FreeRTOS queue and TLSF allocation providers plus the
typed LVGL pool RAM. `display_font_path_children.c` reduces byte comparison
0x46cacc, duplicate 0x4547c6, and LVGL intrusive tail append 0x482bca.
`verify_font_path_compare.py` compares original bytes with actual compiled C
for seven empty/equal/prefix/different/high-byte cases: 7/7 pass. The
allocator, duplicate, and append success paths have no bounded stock runtime
comparison yet.
`display_font_size_setup.c` reduces native 0x4b202c: glyph cache
allocation, bitmap/outline draw-cache selection, descriptor cache pointers,
and native failure logs. Three deeper FreeType cache constructors remain
real code imports. `display_font_metric_scale.c` reduces native 0x5246f8
16.16 fixed-point signed multiplication. `verify_font_metric_scale.py`
executes original bytes versus actual compiled C for 136 boundary and seeded
random pairs: 136/136 pass, including sign and large-operand paths.

The fresh hash-bound Main integrated snapshot at
`primary-dispatch-crt-all-six-round/receipt.json` has 458 unresolved names.
Cross-referencing declarations in actual component C/H files classifies
103 as definite functions and 352 as definite objects/data; three unmatched
are two known Ambiq HAL functions and the former glyph-lower name in that
pre-correction snapshot. This is approximately 106 code / 352 data at the
snapshot, separate from the current UART local dependency graph.

All 112 UART candidate translation units compile for Cortex-M55 with
`-O2 -Wall -Wextra -Werror`; their local relocatable link passes with 219
global definitions and 422 component-only imports. This is a source/target
compile result and static native correspondence. There is no bounded original
execution comparison yet for allocation, FreeType, logs, or product records;
font subsystem runtime/stock equivalence and whole Main image completion
remain unproven.

`verify_font_chain_head.py` separately executes authenticated original bytes
at 0x46cf56 with log flags controlled to zero and compares them with the
actual compiled C accessor: 3/3 null, empty, and populated list cases pass.
This narrow result does not qualify the constructor, flash guard, or full
font manager.
`verify_font_chain_constructor.py` adds four original-byte versus compiled-C
constructor cuts: null descriptors, zero count, count nine, and first
allocation failure at count eight. The original allocator entry is controlled
to return null; the three invalid cases invoke it zero times and the fourth
once. All 4/4 pass. Item creation, successful list construction, diagnostics
under enabled logging, and real allocation remain outside this bounded proof.
### FreeType cache-entry and cache-acquire continuation

`display_font_cache_entry.c` now reduces native `lv_cache_entry_get_ref` (0x4d5312), `lv_cache_entry_get_data` (0x4d5396), `lv_cache_entry_inc_ref` (0x4d5278), `lv_cache_entry_acquire_data` (0x4d53c6), `lv_cache_entry_is_invalid` (0x4d536a), `lv_cache_entry_dec_ref` (0x4d52b2), and `lv_cache_entry_release_data` (0x4d5400). `display_font_cache_find.c` reduces `lv_cache_acquire` (0x4d4dca) including the authenticated null assertions, recursive mutex, virtual lookup, reference increment, and unlock. The source/function/assertion literals were read from the pinned 2.2.6.10 official image pointer table. The entire local UART candidate graph compiles 114/114 Arm M55 C units and links relocatably with zero duplicate definitions; three latter accessor bodies also compiled individually after the graph sweep. These eight bodies have static native-to-source correspondence only; no original-byte versus compiled-C runtime oracle or target execution claim is made. Cache add/remove/drop, cache constructors, face load/select, and product RAM/data remain open.

The next cache continuation adds `display_font_cache_remove.c` for native release/drop and internal drop (0x4d4e72, 0x4d5094, 0x4d511c), `display_font_cache_add.c` for acquire-or-create/add/evict (0x4d4f90, 0x4d51c0, 0x4d5172), and the cache-entry invalidation/deletion helpers (0x4d533e, 0x4d54da). This preserves native lock order, virtual cache operations, reference and invalidation conditions, create and destroy callbacks, and ROM-authenticated assertions/diagnostics. Fresh 116/116 Arm M55 units compile and relocatable link with zero duplicate definitions. This is static native/source qualification and target compilation; successful cache transitions still need original-byte versus compiled-C oracles. Cache constructors and FreeType face load/select remain definite code gaps; their product-owned RAM/data remain typed contracts.

`display_font_face_size.c` next reduces native FreeType `FT_Select_Size` (0x526ca8), `FT_Request_Size` (0x526ce4), and `FT_Set_Char_Size` (0x526d54), including size request bounds, fixed-point shift, driver callbacks, and the explicit still-unreduced lower helpers at 0x526944/0x526a9c/0x526b04. Inspection confirmed the latter two are actual metrics setters; their typed signatures now carry face/index and face/request respectively. Fresh 117/117 Arm M55 units compile and relocatable link. These are static native/source candidates: face/driver layouts and all result paths still need original-byte versus compiled-C comparison. Three cache constructors remained at this checkpoint, sharing native cache-create 0x4d4cd4 plus backend vtable/callback providers.

`display_font_cache_create.c` now reduces that common native cache-create (0x4d4cd4) and all three font cache wrappers (0x5293c0, 0x5297b8, 0x529b38). It retains the exact native block sizes 0x28/0x0c/8, init/cleanup, lazy mutex initialization, name slot, and ROM-authenticated name strings. The backend vtable and three hook tables are explicit typed data contracts for authenticated ROM locations 0x73f478, 0x78ae74, 0x78ae8c, and 0x78aeb0; their pointed-to backend functions are not yet source-reduced. Fresh 118/118 Arm M55 units compile and relocatable link with zero duplicate definitions. Constructor success and backend behavior remain unqualified by compiled-C versus original-byte execution.

The next metrics/backend pass adds `display_font_face_metrics.c` for native fixed-strike metrics (0x526a9c), scaled metrics (0x526a4e), and request metrics (0x526b04, 420 native bytes). It retains five request modes, DPI conversion, fixed-point scales, strike handling, and selected memory clearing; division/multiply-divide helpers remain explicit lower code contracts at 0x524754 and 0x524606. `display_font_lru_alloc.c` adds backend allocator 0x5c2bee and its real 0x44-byte zeroed allocation. The authenticated shared vtable at ROM0x73f478 has ten Thumb entries: 0x5c2bee, 0x5c2c54, 0x5c2e0c, 0x5c2e4c, 0x5c2f32, 0x5c2fd4, 0x5c3098, 0x5c315a, 0x5c3222, 0x5c328a. The glyph/bitmap/outline hook arrays at ROM0x78ae74/0x78ae8c/0x78aeb0 each have three callback pointers. Fresh 120/120 Arm M55 units compile and relocatable link with zero duplicate definitions. Static native/source correspondence and target compilation are shown; compiled-C versus original-byte execution and backend callback qualification remain open.

`display_font_math.c` now implements native FT_MulDiv0x524606 and FT_DivFix0x524754 using signed magnitude and wide arithmetic. `verify_font_math.py` executes authenticated original bytes against the actual compiled C on 137 fixed/seeded cases per function: 137/137 and 137/137 PASS. An initial general clamp model failed on both INT_MIN and a large signed quotient; the corrected implementation wraps 32-bit quotients and clamps only values beyond 32 bits, as observed. This is bounded arithmetic evidence only. The face metrics functions and LRU backend allocator still have static/target compile proof, not native execution comparison.

`display_font_face_size.c` also now reduces fixed-strike search 0x526944: fixed-face flag/type checks, DPI scaling, 26.6 rounding, strike dimension comparison, optional width ignore, and returned strike index. Fresh 121/121 Arm M55 units compile and relocatable link with zero duplicate definitions. The successful strike search still needs an original-byte versus compiled-C oracle because host address-width differences make the nested pointer layout unsuitable for a trivial host shared-library comparison.

Direct disassembly resolved the two shared backend vtable entries absent from Ghidra's function list: index 2 at 0x5c2e0c is the cache destroy dispatch (`vtable[7]`), and index 4 at 0x5c2f32 is insertion into the red-black tree followed by payload pointer conversion and `cache[3] += size_callback(data)`. Vtable roles across indices 0..9 are allocator, init, destroy, lookup, add, remove, remove/evict path, destroy-all, get-victim, and reserve-condition. Cache RAM layout observed in source and native: vtable+0, node size+4, max capacity+8, current size/count+12, compare callback+16, init callback+20, free callback+24, mutex+28, optional name+36, backend red-black tree+40, LRU list+52, size callback+64. The three hook tables provide compare/init/free callbacks for glyph, bitmap, and outline variants; their C bodies are not all reduced yet. This is authenticated pointer-role mapping, not data or callback source closure.

`display_font_lru_hooks.c` now reduces those native backend destroy/add entries, retaining the exact vtable dispatch, RB insertion lower import, entry offset conversion, size callback, and live-size update. `display_font_cache_entry.c` also reduces native entry-offset accessor 0x4d5452 with authenticated assertion. Fresh 122/122 Arm M55 units compile and relocatable link with zero duplicate definitions. RB insertion 0x5c2b00 and the other backend callbacks remain actual source gaps. This pass did not run compiled-C/native runtime comparison for these pointer-rich paths.

`display_font_lru_insert.c` next reduces native LRU RB/list insertion 0x5c2b00 and list-prepend allocation 0x482b12. It copies the key, allocates and links the MRU list node, records the crosslink, initializes the cache entry, and erases the RB node when list allocation fails. `display_font_cache_entry.c` adds native entry init 0x4d547e. Deeper red-black tree allocate/erase helpers at 0x5c34e4/0x5c36c8 remain typed native code imports. Fresh 123/123 Arm M55 units compile and relocatable link with zero duplicate definitions. Successful RB/list pointer effects still need actual compiled-C/native comparison.

`display_font_lru_capacity.c` reduces native get-victim0x5c3222 and reserve-condition0x5c328a: tail-to-head LRU traversal, cache-entry refcount test, size callback, capacity statuses 0/1/2, and exact ROM diagnostic. Fresh 124/124 Arm M55 units compile and relocatable link with zero duplicate definitions. These two pointer-rich callbacks have static native/source qualification only.

`display_font_lru_init.c` reduces native count-based init0x5c2c54 and count-size callback0x5c330c. It checks the real compare/free/node-size contracts, initializes the RB tree through typed lower0x5c3428, initializes the four-byte-payload LRU list, and sets the size callback to one element per node. Fresh 125/125 Arm M55 units compile and relocatable link with zero duplicate definitions. RB initialization and callback table functions remain incomplete; these C bodies have no compiled-C/native runtime comparison.

`display_font_lru_lookup.c` reduces native backend lookup0x5c2e4c and LVGL list move-before0x482d22. It checks the MRU node with the supplied compare callback, falls back to typed RB lookup0x5c3594, moves a found node to MRU, and returns the entry at the native node-size offset. Fresh 126/126 Arm M55 units compile and relocatable link with zero duplicate definitions. The RB lookup and successful pointer transitions still require source and/or compiled-C/native qualification.

`display_font_lru_remove.c` reduces native backend remove0x5c2fd4 and drop0x5c3098; `display_font_lru_clear.c` reduces drop-all0x5c315a. They retain RB/list removal, free callback, size accounting, referenced-entry diagnostics, and bulk tree/list clear through explicit deeper imports. `display_font_lru_vtable.c` now defines the ten-entry source C backend table in the exact authenticated ROM order. Its target C object contains relocations to all ten C functions, not a copied ROM pointer array. Fresh 129/129 Arm M55 units compile and relocatable link with zero duplicate definitions. The remaining local font imports are three hook tables, RB init/insert/find/remove/erase/clear, list clear, display callbacks, font flash power, and product data. This closes the shared LRU vtable code/data at source/target-compile level only; RB tree and hooks are still missing and the pointer-rich paths lack compiled-C/native execution comparison.

`display_font_cache_hooks.c` now defines all three FreeType cache hook tables in source C from the authenticated pointer order. It reduces glyph/bitmap two-word comparators at native0x52977a/0x529aee, outline one-word comparator0x529d50, native no-op glyph cleanup0x529778, bitmap cleanup0x529ae4, and outline cleanup0x529d40. The three substantial initialize callbacks and bitmap/outline cleanup children remain typed lower code imports. Fresh 130/130 Arm M55 units compile and relocatable link with zero duplicate definitions. `verify_font_cache_compare.py` executes original bytes against actual compiled C: 9/9 for each comparator, including equality, first/second field ordering, and unsigned high-bit cases. That bounded proof does not qualify hook initialization or cleanup.

`display_font_outline_init.c` reduces native outline cache initializer0x529cf8, retaining font-context lock, mode flag, outline render child0x529f8e, unlock, output slot, and success result. `display_font_hook_cleanup.c` reduces native FreeType context getter0x4b1fcc, outline-release packet0x52a264, bitmap draw-buffer destruction0x48b216, and bitmap handler release0x48b85a. The log strings and product RAM address were authenticated from the official image. Fresh 132/132 Arm M55 units compile and relocatable link with zero duplicate definitions. Outline rendering/dispatch and glyph/bitmap cache initializers remain code gaps; cleanup and init paths lack compiled-C/native runtime comparison.

The same 132-unit graph now includes source-defined outline event dispatch0x529ea2 and LVGL LRU list clear0x482da4/0x482c9a. Both preserve real callback or node-free effects and exact authenticated diagnostics; outline render0x529f8e, glyph/bitmap cache initializers, RB tree internals, and product hardware/data still remain. No stock-runtime equivalence is claimed for the event and clear paths.

`display_font_rb_core.c` reduces native red-black tree init0x5c3428, compare-directed lookup0x5c3594, and destroy0x5c3716. The tree layout is root/comparator/node-size at offsets 0/4/8; nodes have parent/left/right/color/data at 0/4/8/12/16. Destroy traverses leaves, frees data and nodes, and clears the root as the native routine does. Fresh 133/133 Arm M55 units compile and relocatable link with zero duplicate definitions. Tree insertion/rebalance and removal still require source recovery; these three bodies have not passed compiled-C/native pointer-transition comparison.

Direct Thumb disassembly of native0x5c36c8 confirmed it calls red-black remove0x5c3600, tests the returned payload pointer, and frees that payload on success. `display_font_rb_core.c` now contains this erase wrapper, and caller declarations use the verified pointer-return ABI. Fresh 133/133 Arm M55 units compile and relocatable link. The deeper remove/rotate path remains.

`display_font_rb_remove.c` now reduces native red-black removal0x5c3600 from the full Ghidra body and direct Thumb register evidence: zero/one-child transplant, two-child successor transplant, color carry, rebalance call with verified `(tree, child, parent)` registers, node free, and returned payload pointer. Fresh 134/134 Arm M55 units compile and relocatable link with zero duplicate definitions. The rebalance lower0x5c3976 and insert/allocation path remain; this complex pointer algorithm has static native/source correspondence only and needs controlled original-byte versus compiled-C tree fixtures before a runtime equivalence claim.

`display_font_rb_insert.c` next reduces native node/data allocation0x5c37a4, BST parent walk0x5c3838, and insertion0x5c34e4. It retains the duplicate lookup, root initialization, temporary key substitution for parent search, comparator branch, and explicit insert-rebalance lower0x5c38cc. Fresh 135/135 Arm M55 units compile and relocatable link with zero duplicate definitions. Insert rebalance and remove fix-up are the remaining core RB algorithms; no successful tree oracle is claimed yet.

`display_font_rb_balance.c` reduces native right/left rotations0x5c3860/0x5c3896 and insert fix-up0x5c38cc, including uncle red recolor, inner/outer rotations, and root blackening. Fresh 136/136 Arm M55 units compile and relocatable link with zero duplicate definitions. Remove fix-up0x5c3976 remains the main RB code lower. These tree pointer/color mutations require controlled native/C fixtures before any runtime qualification.

The same file now reduces native remove-color fix-up0x5c3976 using the decoded sibling red/black cases, rotations, recoloring, and final blackening. It takes `(tree, child, parent)` as verified at both call sites by direct Thumb registers. Fresh 136/136 Arm M55 units compile and relocatable link. This closes the named RB algorithm code frontier in the local graph, while actual pointer/data effects still need original-byte versus compiled-C validation. The sibling color read directly dereferences the sibling, matching the native fault behavior for a null sibling; null child links retain the native black-leaf treatment.

The reproducible `verify_font_rb_balance.py` oracle executes authenticated stock bytes and actual compiled Arm C on the same controlled 32-bit tree layouts. Five insert transitions (LL, LR, RR, RL, uncle-red recolor) and four removal transitions (left/right black sibling and left/right red sibling) match whole tree and node memory, **9/9 bounded fixtures**. The oracle compiles the C for Cortex-M4 because the installed Unicorn ARM backend rejects one M55 CSET instruction; the full source remains independently compiled for M55 with `-Werror` and relocatable-linked, 136/136. Malformed-input behavior beyond the audited null sibling dereference and broader tree histories remain unqualified.

The current 136-unit local UART/FreeType relocatable graph has 17 unique remaining font/LV names: three code callbacks (`audio_uart_font_glyph_cache_initialize`, `audio_uart_font_bitmap_cache_initialize`, `audio_uart_font_outline_render`), three exported callback tables, five flash hardware/product contracts, and six LVGL product/runtime cells. This local import count does not measure the full Main image or distinguish externally selected providers in the coordinator's unified graph.

### Next FreeType callback reduction

`display_font_glyph_initialize.c` reduces native0x5295a8: context lock, indexed glyph lookup, scalable/fixed face-size selection, authenticated load flags (0x208008/0x208000), glyph-slot metric packing, italic adjustment, missing-glyph bit, diagnostics, and unlock. `display_font_bitmap_initialize.c` reduces native0x529936: face-size selection, load/render/get glyph, bitmap mode 0x10/0x0e, stride/allocation, exact row copy, glyph release, diagnostics, and unlock. `display_font_italic_shift.c` reduces native0x4b201e fixed-point bearing adjustment. Each deeper FreeType and draw-buffer function is a typed import with its native address; the bitmap allocator's product handlers remain `audio_uart_display_lv_state+0xe8` (authenticated RAM 0x2006f630), not a fabricated table.

`display_font_outline_render.c` reduces native0x529f8e and its 0x529ee8 decomposition callbacks into C: size/load/optional embolden, native six-word callback table, outline vertex estimate and event packet, decompose, optional second stroker pass, close/release paths. `display_font_hook_cleanup.c` now returns the decoded success status from event dispatch0x529ea2, which prior callers may ignore. The deeper stroker, FreeType outline, and glyph operations remain typed code imports. The native null-context diagnostic/fault loop is retained as an actual decoded path.

Fresh **140/140** Arm M55 source files compile with `-Werror` and relocatable link with zero duplicate definitions (the full sweep must be rerun if these files change). Bounded authenticated original-byte versus compiled Cortex-M4 C oracles: `verify_font_glyph_initialize.py` **6/6** cases covering two render modes, italic adjustment, neutral mode, size/load failures; `verify_font_bitmap_initialize.py` **5/5** cases covering success row bytes and size/load/render/get failures; `verify_font_outline_render.py` **3/3** cases covering size/load failure and a no-stroke success with controlled decompose/event lowers. M4 is used only for Unicorn instruction support; the independent M55 build proves target compilation. Stroke pass, live FreeType backends, callbacks from decompose, font memory ownership, and hardware rendering are unqualified. The three former top-level callback imports are now C-defined; the current local graph exposes deeper FreeType/draw operations and product cells, so neither whole font subsystem nor Main image is complete.

The final local `nm -u` font/LV census after this chunk is **27** unique names: **13 true code lowers** (`bitmap_allocate`, `bitmap_stride`, `decompose_outline`, `done_glyph`, `embolden_outline`, `get_char_index`, `get_glyph`, `load_glyph`, `render_glyph`, `stroke_glyph`, `stroker_configure`, `stroker_create`, `stroker_destroy`); **three callback-table symbols**; **five flash product/hardware contracts**; and **six LVGL runtime/product cells**. This is an intentionally local frontier; root's integrated Main graph can resolve some names from other selected sources and has other non-font gaps.

### Deeper FreeType bodies

`display_font_freetype_glyph_leaf.c` reduces native FT_Get_Char_Index0x526f10, FT_Done_Glyph0x567f88, and `ft_mem_free`0x529256 with the genuine charmap class and allocator method pointers. `display_font_freetype_get_glyph.c` reduces FT_Get_Glyph0x567ec8, glyph-new0x567e24, and its allocator/zeroing leaf0x529148/176. Bitmap/outline glyph-class tables at ROM0x7601b0/0x7601d0 remain explicit typed data contracts. `display_font_freetype_render_glyph.c` reduces FT_Render_Glyph0x527228; `display_font_freetype_renderer.c` reduces renderer list lookup0x52705a and render dispatch0x5271c0.

`display_font_freetype_load_glyph.c` reduces the complete 702-byte native FT_Load_Glyph0x525574 control flow: flag normalization, conditional native hinter, driver method calls, outline validation/grid metrics, advance selection/scale, optional transform, and render/preset dispatch. Subordinate FreeType driver, hinter, transform, and bitmap-preset bodies remain typed code calls through their authenticated ABIs. Controlled original-byte versus actual compiled-C oracles pass `verify_font_freetype_leaf.py` **4/4** (charmap index, glyph acquisition memory effects, glyph destruction) and `verify_font_freetype_load.py` **4/4** (both cache load flags, alternate driver flag, null-face error). Hinter, transformed outlines, renderer retry, and actual class-method behavior are not qualified by those bounded fixtures.

`verify_font_freetype_renderer.py` additionally compares authenticated FT_Render_Glyph/renderer bytes with compiled C on **5/5** controlled bitmap, outline, mode-width, and arbitrary-format renderer-list cases. Its renderer method is a controlled callback; actual GPU/draw behavior remains unqualified.

Fresh local Arm M55 `-Werror` compile and relocatable link pass **145/145** source units with zero duplicate definitions. The current local font/LV `nm -u` frontier is **33 names**: **17 genuine lower code** (bitmap allocate/stride, decompose, embolden, get format, slot clear, grid metrics, outline check/transform/translate, bitmap preset, slot renderer, glyph stroke, stroker configure/create/destroy, vector transform), **two glyph-class data tables**, **three callback tables**, **five flash product/hardware contracts**, and **six LVGL runtime/product cells**. This local count excludes unrelated Main image gaps and may overlap providers selected elsewhere in the unified build.

### 2026-10-11 deeper FreeType outline and glyph classes

The Audio experimental source archive now target-compiles **152 C translation units** for Cortex-M55 with `-Wall -Wextra -Werror`, and a relocatable link succeeds with no duplicate definitions. New source files are `display_font_freetype_glyph_classes.c`, `display_font_freetype_glyph_stroke.c`, `display_font_freetype_stroker.c`, `display_font_freetype_orientation.c`, `display_font_freetype_cbox.c`, `display_font_freetype_decompose.c`, and `display_font_freetype_outline_storage.c`; the last file reduces native FT_Outline_Check, Copy, Translate, New, and Done and their allocator/free effects. Existing `display_font_freetype_get_glyph.c` exports the authentic glyph allocator/new helper, and bitmap glyph copy was corrected to return the native child status. All sources remain experimental and are selected by the Audio candidate source glob; they do not establish a firmware image.

The two glyph-class records are generated as C constants with typed function-pointer relocations. `verify_font_glyph_class_tables.py` compared all scalar slots with stock ROM 0x7601b0 and 0x7601d0 and verified all **10** method-pointer relocations (4 bitmap, 6 outline). It does not claim equal final pointer addresses because the C image layout differs from stock.

Actual compiled-C versus original-byte Unicorn checks: `verify_font_decompose.py` PASS **8/8** callback traces and returns across on/conic/cubic, malformed tags, callback errors, and shift/delta; `verify_font_outline_storage.py` PASS **7/7** check/copy/translate cases; `verify_font_outline_alloc.py` PASS **10/10** New/Done cases using controlled allocator/free callbacks, including invalid counts and flags. `verify_font_orientation.py` PASS **4/4** with the C CBox child. `verify_font_outline_render.py` PASS **4/4** for outer renderer control, including the stroke pass, while its deeper stroke children remain hooks. The allocation oracle uses a fixture-only zeroing implementation to satisfy the selected memset ABI; production uses the selected C provider. None of these fixtures validate physical hardware or arbitrary outlines.

Current local font/LV frontier after this source chunk is **30 imports**: 16 code or callback methods (`bitmap_allocate/copy/done/init/stride`, `embolden_xy`, `get_format`, `glyphslot_clear`, `grid_fit_metrics`, `outline_transform`, `preset_bitmap`, `slot_renderer`, `stroker_export/get_counts/parse_outline`, `vector_transform`), 3 callback tables, 5 flash/product contracts, and 6 LV product/runtime cells. Class tables and outline storage are now C defined. Full stroker parse/export, bitmap conversion, product cells, all-image source coverage, and target image equivalence remain open.

Follow-on: `display_font_freetype_transform.c` now reduces the native FT_MulFix 0x5246f8, FT_Vector_Transform 0x527b60, and FT_Outline_Transform 0x527ba0 with 32-bit fixed-point rounding. `verify_font_transform.py` compares actual compiled C against stock on **23 vector** and **23 outline** fixtures, including randomized signed coordinates/matrices; all pass. Current Audio candidate is **153 units**, target compile and relocatable link PASS. The local font/LV frontier is now **28 imports** (14 code/callback, 3 callback tables, 5 flash/product contracts, 6 LV cells); the preceding 30-import count was the immediately prior snapshot.

### Stroker parse/export and LVGL callback installers

The next authenticated C bodies are `display_font_freetype_stroker_parse.c` (native FT_Stroker_ParseOutline 0x569748), `display_font_freetype_stroker_export.c` (FT_Stroker_GetBorderCounts 0x5696d4, ExportBorder 0x569716, and their real border walkers 0x5686be/0x568728), `display_font_freetype_stroker_begin.c` (BeginSubPath 0x5694e0), `display_font_callback_installers.c` (three descriptor callback installers 0x529406/0x5297f8/0x529b7e), and `display_font_callback_release.c` (bitmap/outline draw-release callbacks 0x5298f8/0x529e04). The installers preserve authenticated source/function strings, magic check, log and faulting-store assertion sequence. Five other callback/geometry bodies remain typed imports. The stroke-glyph point/contour variables were renamed to reflect actual native argument order.

Actual compiled-C/original-byte checks: `verify_font_stroker_parse.py` PASS **9/9** callback traces/returns across on/conic/cubic, open, malformed, and callback-error cases with geometry children hooked; `verify_font_stroker_export.py` PASS **10/10** border count/export state cases; `verify_font_stroker_begin.py` PASS **9/9** state transitions including cap/join/open branches; `verify_font_callback_installers.py` PASS **3/3** normalized callback-pointer slot records; `verify_font_callback_release.py` PASS **4/4** cache-remove calls and node clearing. These do not execute all real stroke geometry or application rendering hardware.

Fresh Audio candidate is **158 C units**, all Cortex-M55 `-Werror` compile and relocatable link PASS. Local font/LV frontier is **29 imports**: **18 code/callback** bodies, five flash/product contracts, and six LV runtime/product cells. The code frontier includes stroker line/conic/cubic/close and glyph/bitmap/outline callback bodies; completing the entire stroke path and firmware remains open. The prior transform file now reuses the already selected `audio_uart_font_scale_metric` implementation of native FT_MulFix instead of defining a duplicate body; its 23+23 stock/C oracle still passes.

Further stroker child reduction adds `display_font_freetype_stroker_close.c` for native EndSubPath 0x5695f8 and `display_font_freetype_stroker_border_close.c` for FT_Angle_Diff 0x52910e and border Close 0x56834a. The first preserves open/closed branch order, cap/arc/reverse calls and early errors; `verify_font_stroker_close.py` compares actual C to stock over **10/10** controlled call/state/error traces. `verify_font_stroker_border_close.py` compares **36/36** signed angle cases and **8/8** border close mutations, including reversal. Fresh Audio candidate is **160 C units**, M55 `-Werror` compile and relocatable link PASS. Current local font/LV frontier is **32 imports**: **21 code/callback** providers plus the same 5 flash/product and 6 LV runtime/product cells. This increase from 29 reflects authentic newly exposed cap/arc/reverse children, not regression in already reduced providers.

### Stroker growth, reversal, cap and polar continuation

`display_font_freetype_realloc.c` reduces native FreeType array reallocate 0x52919c/0x5291e4 with allocator vtable calls, signed count validation, overflow, zero-size free, retained old pointer on realloc failure, and zeroing of newly allocated tail. `display_font_freetype_border_grow.c` reduces 0x5682de and its actual two-stage points/tags allocation/error order. `display_font_freetype_stroker_reverse.c` reduces 0x569532 with border transfer and tag reversal. `display_font_freetype_border_add.c` reduces 0x5683f2 with active-point replacement, near-duplicate suppression, growth and error. `display_font_freetype_stroker_arc.c` reduces 0x5688b8 round/butt/square cap dispatch and polar-coordinate composition; `display_font_freetype_polar.c` reduces FT_Vector_From_Polar 0x5290fa and keeps FT_Vector_Rotate 0x529006 as a genuine deeper child.

Actual compiled C versus stock with controlled authenticated allocator/geometry interfaces: `verify_font_border_grow.py` PASS **5/5** including both realloc failure positions, `verify_font_stroker_reverse.py` PASS **7/7** including grow failure, `verify_font_border_add.py` PASS **7/7** including duplicate and error, and `verify_font_stroker_arc.py` PASS **11/11** including all three cap types and error exits. The allocator oracle uses an explicitly fixture-local zeroing provider and is not hardware evidence. Full line/conic/cubic geometry, first/second/round caps, and CORDIC rotation are still source gaps.

Fresh Audio candidate: **166 C units**, Cortex-M55 `-Werror` compile and relocatable link PASS. Local font/LV imports remain **32**: 21 code/callback, 5 flash/product, 6 LV runtime/product; the newly exposed CORDIC and cap children offset resolved wrapper imports. Full stroke and image completion remain open.

### Polar math and first complete stroke geometry bodies

The native FT_Vector_Rotate orchestration and its normalize/shrink/CORDIC children are now C-defined in `display_font_freetype_rotate.c`, `display_font_freetype_rotate_scalars.c`, and `display_font_freetype_cordic.c`, including the authenticated 22-word stock angle table at ROM 0x6e35c0. Actual compiled-C versus stock checks pass rotation **6/6** controlled-child traces, normalize **65/65**, shrink **101/101**, CORDIC core **75/75**, and the connected polar math graph **55/55** signed/angle fixtures. These are arithmetic comparisons, not a complete rendered-glyph oracle.

`display_font_freetype_stroker_round_cap.c` reduces native 0x568870 and `display_font_freetype_stroker_line.c` reduces native FT_Stroker_LineTo 0x568d86. They preserve both border selections, error exits, state mutations, and typed lower calls. `verify_font_round_cap.py` passes **12/12** actual compiled-C/stock comparisons with the arc emitter controlled. `verify_font_stroker_line.py` passes **7/7** with vector and corner helpers controlled; its oracle exposed and corrected the native left-before-right border order. Actual arc emission, corner joining, conic, cubic, and both end-cap helpers remain source work.

Fresh local Audio candidate now has **171 C translation units**, all Cortex-M55 `-O2 -Wall -Wextra -Werror` compile and relocatable link PASS with zero duplicate definitions. Local font/LV `nm -u` has **34 names**: **23 code/callback** contracts, five flash/product/hardware contracts, and six LV runtime/product cells. This local graph is distinct from root's earlier all-image Main snapshot and does not establish image linking, stock equality, or hardware behavior.

The next `display_font_freetype_stroker_line_children.c` reduces native existing-corner join 0x568ce2 and first-border start 0x568d2a, preserving the two cap calls and the two border moves with their native state and error order. The selected symbol aliases predate the pinned source mapping. `verify_font_stroker_line_children.py` passes **7/7** actual compiled-C/stock fixtures with controlled cap, polar, and border-move children. The local archive now has **172 C units**, target compile and relocatable link PASS; local font/LV frontier is **33 names** (22 code/callback, five flash/product/hardware, six LV runtime/product).

`display_font_freetype_stroker_border_move.c` then reduces native 0x568636, including the existing-contour close, start index, active flag, and point append. `verify_font_stroker_border_move.py` passes **6/6** compiled-C/stock fixtures with close/add children controlled, including error return. The latest local archive has **173 C units**, target `-Werror` compile and relocatable link PASS, and **32 font/LV imports** (21 code/callback, five flash/product/hardware, six LV runtime/product).

### Native vector measurement and arc emission

`display_font_freetype_vector_measure.c` reduces FT_Atan2 0x528fbc and FT_Vector_Length 0x529086, preserving zero/axis cases, normalization, CORDIC, shrink, and signed shift rounding. `display_font_freetype_angle_core.c` reduces native CORDIC pseudo-polarize 0x528ee4 with the authenticated 22-word ROM angle table and quadrant/rounding behavior. Actual compiled-C versus stock checks: `verify_font_vector_measure.py` **18/18** controlled angle-core fixtures, `verify_font_angle_core.py` **129/129** arithmetic vectors, and `verify_font_vector_measure_integrated.py` **105/105** each for angle and length with all arithmetic children in C. The angle-core oracle caught and corrected a wrong negative-quadrant literal before admission.

`display_font_freetype_arc_emit.c` reduces native FT_StrokeBorder_Arcto 0x56851e: sweep clamp, segment iteration, tangent factor, Bezier controls, and immediate child error. `verify_font_arc_emit.py` passes **10/10** stock/compiled-C cases with controlled polar/trig/muldiv/cubic children, including positive/negative, multi-segment and first/second segment failures. The oracle caught and corrected the native polar-before-trig call order. `display_font_freetype_trig.c` reduces unit-vector0x528fde and sine/cosine wrappers0x528f9a/0x528f8c; `verify_font_trig.py` passes **68/68** each with the real C CORDIC child. `display_font_freetype_border_cubic.c` reduces native 0x5684c2, including grow, three point/tag writes and active flag; `verify_font_border_cubic.py` passes **6/6** controlled-grow cases.

Fresh Audio selected candidate has **178 C units** compiling Cortex-M55 with `-O2 -Wall -Wextra -Werror`, relocatable link PASS and zero duplicate definitions. The local font/LV frontier is **29 imports**: **18 code/callback bodies**, five flash/product contracts, six LV runtime/product cells. The largest true stroke bodies still open are first/second caps and conic/cubic geometry. These source and bounded arithmetic checks do not establish all-image equivalence or live rendering behavior.

`display_font_freetype_stroker_cap_first.c` now reduces native FT_Stroker_Inside 0x5689e6: the signed angle half-turn, authentic intersection bound 0xb38001, tangent/radius test, fallback vector, inside miter, active flag, and border append. Native tangent 0x528fa8 is source-defined by the selected unit vector and DivFix providers. `verify_font_cap_first.py` passes **8/8** compiled-C/stock controlled-child cases across both border sides, miter/fallback, zero/short lengths, and append error. Fresh local archive is **179 C units**, M55 `-Werror` compile and relocatable link PASS; font/LV frontier **28 names** (17 code/callback, five flash/product, six LV cells). The second cap, conic and cubic remain substantive native bodies.

`display_font_freetype_stroker_cap_second.c` reduces native FT_Stroker_Outside 0x568abe: round, fixed bevel, clipped miter and variable-width miter paths, with all polar/append calls and early errors. `verify_font_cap_second.py` passes **11/11** actual compiled-C/stock controlled-child cases. Its oracle caught and corrected the outer scale argument order and the perpendicular rather than half-turn offsets for the two clipped-miter points. Fresh local archive is **180 C units**, target `-Werror` compile and relocatable link PASS; font/LV frontier **27 names** (16 code/callback, five flash/product, six LV cells). The two large conic/cubic stroke bodies remain, along with unrelated bitmap/glyph callbacks and product data.

### Conic and cubic native body reduction

`display_font_freetype_curve_helpers.c` reduces native conic split0x567fce, cubic split0x5680ce, conic/cubic angle continuity0x568020/0x568176, and quadratic border append0x56847a. Its `verify_font_curve_helpers.py` compares actual compiled C with stock across **12/12** controlled-child split, near-point, angle, append, and grow-failure cases.

`display_font_freetype_stroker_conic.c` and `display_font_freetype_stroker_cubic.c` reduce native FT_Stroker_ConicTo0x568e52 and CubicTo0x569160 using the [official FreeType 2.9.1 ftstroke.c pin](https://github.com/freetype/freetype/blob/VER-2-9-1/src/base/ftstroke.c) with stock offsets/calls verified against the native disassembly. They include degenerate short-circuit, bounded recursive subdivision, first/subsequent arc joins, both borders, wide-stroke reverse sector, exact child errors, and center/angle state. `verify_font_stroker_conic.py` and `verify_font_stroker_cubic.py` pass **9/9** actual compiled-C/stock controlled-child cases each, including wide reverse-sector and first/second border failures. Their children were already source-defined independently, but these fixtures do not run the entire connected stroker graph without hooks; full arbitrary-outline equivalence remains unqualified.

Fresh Audio local source archive is **183 C units**, Cortex-M55 `-O2 -Wall -Wextra -Werror` compile and relocatable link PASS with zero duplicate definitions. Its font/LV frontier is **25 imports**: **14 remaining code/callback contracts** unrelated to the now locally source-closed principal stroker geometry, five flash/product contracts, and six LV runtime/product cells. All-image Main source coverage and hardware rendering remain open.

`verify_font_stroker_connected.py` runs the actual compiled C conic/cubic, angle, CORDIC, fixed arithmetic, vector, curve-split and border-append sources together against authenticated stock bytes. It passes **8/8** bounded ordinary/near-point and first-corner/grow-error fixtures. Only first-corner state setup and border capacity allocation are fixture hooks; the connected geometry and point/tag writes execute in C. The fixture uses the separately identified quotient-only `__aeabi_uldivmod` provider solely to supply M4 compiler arithmetic. Wide reverse-sector behavior is covered in the controlled-child conic/cubic oracles above, not this connected one. Arbitrary outline, allocator and product-font execution remain unverified.

### Bitmap lifecycle and font format follow-on

`display_font_freetype_bitmap_lifecycle.c` reduces native FT_Bitmap_Init 0x58ed20 and FT_Bitmap_Done 0x58f156, preserving null checks, the 24-byte zero operation, supplied allocator free, and buffer-pointer clear. `display_font_freetype_format.c` reduces FT_Get_Font_Format 0x524b64 using the authenticated `font-format` ROM literal at 0x78aa84 and the driver's class callback at +0x20. The bitmap-done caller declaration now uses the native `int32_t` return ABI. All three are direct native-instruction translations; actual compiled-C/stock runtime oracle remains pending.

`display_font_freetype_slot_clear.c` also reduces the native slot bitmap release0x5250a2 and FT_GlyphSlot_Clear0x5252bc, including conditional owner-bit free and the exact clear order. Fresh local Audio source archive is **186 C units**, all Cortex-M55 `-O2 -Wall -Wextra -Werror` compile and relocatable link PASS. These sources remove four of the former 14 local font code imports; ten other code/callback contracts, five flash/product contracts, and six LV runtime/product cells remain. This is a local relocatable candidate, not a completed image.

`display_font_freetype_metrics_renderer.c` reduces FT_Grid_Fit_Metrics0x5254c8 and slot renderer selection0x527096, including signed-width modulo-64 rounding and the authenticated renderer-list fallback. The local Audio archive now has **187 C units**, Cortex-M55 strict compile and relocatable link PASS. The local font/LV frontier is **19 imports**: eight code/callbacks, five font flash/product cells, and six LV runtime/product cells. These newest bodies have target compile and native static correspondence, with actual compiled-C/stock fixture comparison pending.

`display_font_bitmap_stride.c` reduces native0x48aad8/0x48aaea by dispatching the width and byte format through the callback at +0x14 of the authenticated LV RAM descriptor0x2006f610 (the existing LV state base +0xc8). Its null callback returns zero as native. Width remains full 32-bit per native ABI; the bitmap initializer declaration was corrected. Local Audio archive is **188 C units**, Cortex-M55 strict compile and relocatable link PASS; local font/LV frontier is **18 imports**: seven code/callbacks and eleven typed product/runtime cells. Actual stock/C runtime oracle for these new units is still pending.

`display_font_freetype_bitmap_copy.c` reduces native FT_Bitmap_Copy0x58ed2e using the selected FreeType memory allocator, raw realloc0x5291e4 (now exported from the existing source), and byte copy. It implements null/same-object returns, absent source buffer, same/different pitch signs, existing-buffer resizing, new allocation, and error propagation. `verify_font_bitmap_copy.py` passes **8/8 actual compiled-C/stock** comparisons for null/same, absent buffer, and existing same-size buffer with both pitch orientations. Those fixtures do not execute allocation/reallocation; their source-defined code is compiled and linked but runtime equivalence is not yet qualified. Local Audio archive is **189 C units**, Cortex-M55 strict compile and relocatable link PASS; six font code/callback contracts plus eleven data contracts remain.

`display_font_callback_bitmap_lookup.c` reduces native0x529858 FreeType bitmap glyph lookup, preserving descriptor assertion/fatal diagnostics with the authenticated ROM strings and magic0x5f5f4654, three-word cache key, cache add failure log, retained entry, and cache data+8 return. The installer callback declaration now has the native pointer return ABI. This body has static native correspondence and target compile; runtime oracle still pending. Local Audio archive is **190 C units**, strict Cortex-M55 compile and relocatable link PASS; five true font code/callback contracts and eleven typed data cells remain.

`display_font_callback_outline_lookup.c` reduces native0x529d70/0x529e52, including native descriptor magic/fatal diagnostics, caller-supplied cache owner pointer, glyph index key, cache failure log, retained entry and cache-data return. A register audit corrected both bitmap and outline callbacks to pass the descriptor in cache-add R2. `display_font_bitmap_allocate.c` reduces native LV draw buffer create0x48b010 and size helper0x48b86c, including format-specific palette bytes, device allocation callback, failure logging/free, packed header fields, and authenticated LV descriptor callback. These new bodies are target compiled and statically crosswalked; actual compiled-C/stock oracle remains pending. Fresh local Audio archive **192 C units**, strict Cortex-M55 compile and relocatable link PASS. Local font/LV frontier **14 imports**: three true code (common glyph callback, embolden XY, preset bitmap) plus eleven typed product/runtime cells.

`verify_font_bitmap_allocate.py` now executes actual compiled C against stock0x48b010 with controlled heap/device/palette callbacks. It passes **6/6** successful allocation fixtures across formats14,7,8,9,10,20, comparing callback arguments, all 28 packed header bytes, and return. Failure/fatal branches remain source-static and target-compiled, not runtime-qualified.

`display_font_freetype_preset_bitmap.c` reduces native bitmap preset0x5250de and the +21/-21 LCD adjustment0x524f36. The source preserves owned-buffer early return, origin translation, mode-specific grid rounding, 3-channel width/row transforms, pitch, and slot bitmap fields. Its caller declaration now passes a typed origin pointer. `verify_font_preset_bitmap.py` passes **36/36 actual compiled-C/stock** comparisons over six modes, three bounding boxes, and two origins with only outline-cbox child controlled. Local Audio archive is **193 C units**, Cortex-M55 strict compile and relocatable link PASS. Two local font code imports and eleven typed data cells remain.

`display_font_freetype_normlen.c` reduces FT_Vector_NormLen0x524902 from the [official FreeType 2.9.1 ftcalc.c pin](https://github.com/freetype/freetype/blob/VER-2-9-1/src/base/ftcalc.c), with explicit native 32-bit wraps. `verify_font_normlen.py` passes **129/129 actual compiled-C/stock** vectors. `display_font_freetype_embolden_xy.c` reduces FT_Outline_EmboldenXY0x527bd6 from the [official FreeType 2.9.1 ftoutln.c pin](https://github.com/freetype/freetype/blob/VER-2-9-1/src/base/ftoutln.c), using selected orientation, CBox, MulFix, MulDiv and the new NormLen. `verify_font_embolden.py` passes **12/12 connected actual compiled-C/stock** rectangle orientations/strengths. Arbitrary outline and overflow extremes are not covered by these fixtures. Only the common glyph callback remains as a local font code import, alongside eleven typed product/runtime cells.

`display_font_callback_glyph_lookup.c` reduces native common glyph callback0x529460, including all three fatal assertions, low Unicode clear, 40-byte cache key, cache lookup failure log, glyph descriptor copy, optional advance adjustment, and cache release. `verify_font_callback_glyph.py` passes **5/5 actual compiled-C/stock** controlled-cache fixtures spanning low Unicode, normal, and adjusted descriptor paths. Fresh local Audio archive **196 C units**, strict Cortex-M55 compile and relocatable link PASS; `nm -u` shows **zero local font/LV code imports**. Eleven typed font/LV data cells remain. This is connected local source-graph closure, not full Main firmware source or runtime equivalence.

**Frontier correction:** the previous `nm` count classified all eleven residual names as data. Native0x464512 `audio_uart_lv_assert_null` is a real LV timer fatal branch and native0x4c26e0 `audio_uart_font_flash_power` is a real MX25U power sequencer. `display_lv_timer_assert.c` now reduces the first with authenticated `lv_timer_pause` line204 diagnostic and native faulting store. The remaining local font/LV frontier is **one true code function** (`flash_power`) and **nine RAM data cells** (four flash state, five LV runtime). The local font geometry/callback subgraph is source-closed; flash power and RAM initialization are not.

**Flash-power source continuation:** `display_font_flash_power.c` now reduces the
full native MX25U sequencer at `0x4c26e0`, including mode 0/1/2, authentic
magic validation, peripheral and pin ordering, 25-word MSPI save, restored
registers, and the native byte-width restore of state `+0x8b8` into MSPI
`+0x2b4`. `verify_font_flash_power_guards.py` compares actual compiled C
against original bytes for six guards and one controlled restore with full
device and MSPI memory comparison: **7/7 pass**. The restore correction is
specifically bound to native `0x4c287c` LDRB, mask, and `0x4c2884` STR.

`display_font_flash_hal.c` reduces its five native code descendants:
MSPI transition `0x4c0758`, command-queue suspend `0x4bfd44`, resume
`0x4bfd62`, power prepare `0x4c235c`, and seven-group pin mux disable
`0x4c45a4`. The command-queue state and register ABI is pinned to AmbiqSuite
`release_sdk5p1p0-366b80e084` and checked against native `0x538e3c/8c`;
the register and magic literals are authenticated in the ROM pools.
`verify_font_flash_hal.py` compares actual compiled C with original bytes
for eight controlled child cases, including enabled/disabled transition,
CMDQ suspend/resume, valid/invalid power prepare, and valid/invalid pin
disable: **8/8 pass**. External pin, clock, critical section, and delay
calls are cut at their authentic interfaces in these focused cases.

The dedicated Audio UART source archive now has **199 C translation units**;
all pass Cortex-M55 `-O2 -Wall -Wextra -Werror`, and the full 199-object
relocatable link passes. The local font/LV/flash subgraph has no remaining
true code imports. Nine RAM runtime cells remain typed imports: flash
device/mutex/mode/sleep and LV heap pool/level names/lock/static slot/tick
state. Their initializer ownership and contents are not authenticated, so
they are not filled with guessed values. These target compile and bounded
oracles do not establish full Main payload linking or hardware behavior.

**Runtime-cell audit and next file facade:** The four flash cells are
device and mutex handles (`0x20074544/548`) and mutable mode/sleep bytes
(`0x20074fb8/b9`); native `0x46f54a` creates the mutex on demand, while
`0x46f50c/52c` write the sleep byte. The LV heap pool (`0x20000338`)
contains mutable mutex/pool pointers and usage counters; the timer state
(`0x2006f600`) contains a mutable tick callback and count; the lock cell
(`0x2006f718`) is initialized by native mutex-create code. The static
zero-size allocation sentinel (`0x2006f5ac`) is an address identity and
requires correct final placement. The level-name pointer table
(`0x20002bec`) is the only one of these nine likely to carry preinitialized
string pointers, but its four entries and copy owner have not been
authenticated; no table values are invented. The Boot startup copy record
for RAM `0x20000000..0x2000055a` belongs to the Boot image and is not used
to assert Main runtime initialization at `0x20000338`.

`display_file_api.c` reduces four native stdio/LittleFS facade bodies:
open `0x474550`, read `0x474634`, seek `0x474814`, tell `0x474870`.
It preserves the 96-byte handle allocation, mode letters and flags,
1000-tick mutex policy, LittleFS handle offset `+4`, return/error and
size multiplication/division behavior. Six actual compiled-C/native
guard fixtures pass in `verify_display_file_api_guards.py`: allocator
failure, read mutex failure, invalid seek origin, seek mutex failure,
null tell, and tell mutex failure. Successful LittleFS lower behavior
remains unqualified. This opens four true LittleFS operation children
at `0x4cfa94`, `0x4cfb40`, `0x4cfbb2`, `0x4cfbe8`, plus typed Main
runtime cells `0x20071ac8` context and `0x200748f4` mutex.
The dedicated Audio UART archive now has **200 C units**, all passing
M55 Werror compilation and relocatable link.

`display_file_lfs_wrappers.c` reduces the four directly exposed LittleFS
public bodies at `0x4cfa94`, `0x4cfb40`, `0x4cfbb2`, and `0x4cfbe8`.
They validate the open-list membership at filesystem `+0x28`, dispatch
the native diagnostic literals and source lines, then invoke the actual
operation cores `0x4cdcc8`, `0x4ce158`, `0x4ce3bc`, and `0x4ce45c`.
`verify_display_file_connected.py` compiles the facade, these wrappers,
and the selected membership C source together; against original bytes,
three connected successful read/seek/tell cases pass with only the
operation core and mutex calls cut. The wrapper file compiles M55 Werror;
successful open allocation and the four operation cores remain to reduce
and qualify. The wrapper source adds no product data values.

The next LittleFS pass source-reduces three of those four operation cores:
`display_file_lfs_open_core.c` maps `0x4cdcc8` to the pinned `lfs_file_opencfg`
with its authenticated 16-byte zero default config at ROM `0x78ab8c`;
`display_file_lfs_read_core.c` maps `0x4ce158` to the selected
`g2_lfs_file_flush`/`g2_lfs_file_flushedread` sources with exact read flag
assertion; `display_file_lfs_seek_core.c` maps `0x4ce3bc` including
whence adjustment, max-file bound, cache-offset fast path, and flush fallback.
The fourth, tell core `0x4ce45c`, is the authenticated file position load
from `+0x34` within `display_file_lfs_wrappers.c`. The connected actual-C/
original-byte oracle now passes **4/4** (read, seek, tell through facade and
open core with `lfs_file_opencfg` cut). Deep read/write and successful
`lfs_file_opencfg` behavior are outside this bounded fixture. Three true
LittleFS descendants remain directly exposed by these cores:
`lfs_file_opencfg` `0x4cda36`; selected flush/flushedread and
`g2_lfs_ctz_index` providers remain source-defined in the existing
LittleFS archive. The file-size core `0x4ce472` is also now reduced in
`display_file_lfs_seek_core.c` as the native max(position,size) under
writing mode, otherwise stored size. The connected oracle has expanded
to **6/6**, including seek from end and max-file bound. The dedicated
Audio UART archive is now **204 C units**, passing M55 Werror compile
and full relocatable link.

`display_file_lfs_opencfg.c` now source-reduces the full pinned LittleFS
`lfs_file_opencfg_` control flow corresponding to native `0x4cda36`:
write-mode consistency, setup, dir-find and create/truncate/exclusive
branches, 3-tag commit, user-attribute read/write checks, cache buffer
allocation/zeroing, inline-file import, and error cleanup through the
selected `g2_lfs_file_close`. Native struct offsets, tag masks, status
codes, and the 16-byte default config are explicit. The connected oracle
still passes **6/6**, now with actual C `opencfg` executing the early
force-consistency failure instead of a cut; successful metadata and cache
paths remain unqualified. This opens **nine** true direct LittleFS helper
imports (`forceconsistency`, `dir_find`, `path_islast`, `path_isdir`,
`path_namelen`, `mlist_append`, `dir_get`, `ctz_fromle32`, `malloc`).
The five selected LittleFS helpers (`cache_zero`, `ctz_index`, `dir_commit`,
`file_close`, `file_flush`/`flushedread`, `mlist_isopen`) are existing
source providers, not duplicate definitions. Dedicated Audio UART archive
now **205 C units** with M55 Werror compile and relocatable link pass.

The next LittleFS helper unit, `display_file_lfs_simple_helpers.c`, reduces
eight of the nine direct `opencfg` imports with native and pinned-source
correspondence: path name length/last/directory checks, mlist append, a
two-word little-endian ctz conversion, allocator forwarding to the selected
`codec_allocate`, force-consistency's three ordered operations, and
`lfs_dir_get` forwarding to the already selected `g2_lfs_dir_getslice` with
zero slice offset and tag-size length. The latter ABI is visible at native
`0x4cb3c8`, which passes a fifth buffer argument and takes size from native
`0x4caeb8`. The connected actual-C/native oracle passes **7/7**, including
`lfs_dir_get` with the inner `0x4cb23a` operation cut identically on both
sides. The dedicated Audio UART archive is **206 C units**, Cortex-M55
`-O2 -Wall -Wextra -Werror` compile and relocatable link PASS. The remaining
direct `opencfg` helper is `lfs_dir_find` `0x4cc04a`; the force-consistency
chain opens three genuine child bodies at `0x4cf648`, `0x4cf6e8`, and
`0x4cf7ac`. Successful metadata/cache paths remain outside the bounded
oracle and the Main image remains incomplete.

`display_file_lfs_dir_find.c` now reduces the remaining direct `opencfg`
helper, native `0x4cc04a`, using the pinned LittleFS path-resolution loop:
root pair initialization, slash and dot processing, parent-depth handling,
directory traversal, child pair lookup, and disk-name callback through the
selected block comparator and directory fetch-match provider. Actual compiled
C/native oracle **9/9** includes empty path and a one-component missing path
with identical cut at `g2_lfs_dir_fetchmatch` `0x4cb968`. Other traversal,
successful lookup, and callback comparator paths remain unqualified. Dedicated
Audio UART source archive is **207 C units**, M55 Werror compile and
relocatable link PASS. Direct `opencfg` code imports are now source-defined;
the deeper force-consistency recovery/move operations remain source work.
Its third orphan operation already binds selected `g2_lfs_fs_deorphan`
`0x4cf7ac`, avoiding a duplicate provider.

`display_file_lfs_demove.c` reduces the next consistency child, native
`0x4cf6e8`, with its move-state check, diagnostic, authenticated assertion,
directory fetch, state preparation and delete-tag commit. It binds selected
LittleFS `dir_fetch`, `fs_prepmove` and `dir_commit` providers. The connected
actual compiled-C/native oracle passes **11/11**: added no-move force chain
and active-move fetch-error paths; the latter cuts at identical native
`dir_fetch` `0x4cbedc` with error -5. Successful delete commit remains
unqualified. Audio UART archive now **208 C units**, M55 Werror compile and
relocatable link PASS. The remaining direct consistency child is superblock
recovery native `0x4cf648`.

`display_file_lfs_desuperblock.c` now reduces that remaining direct
consistency child. It implements the native bit-9 pending-superblock check,
authenticated diagnostic and root pair, selected directory fetch and commit,
six-field 24-byte superblock with native disk version `0x00020001`, native
inline-struct tag `0x20100018`, and bit-9 clear only after successful commit.
The connected actual compiled-C/native oracle passes **13/13**, adding
fetch-error and successful commit/state-clear cases with identical lower
cuts; the latter checks observable filesystem memory, while committed media
contents remain dependent on the selected commit implementation. The Audio
UART candidate archive is now **209 C units**, M55 Werror compile and
relocatable link PASS. All direct force-consistency operations are now
source-backed or bound to selected LittleFS providers. A complete Main image
still requires further application, runtime, product-data, and layout work.

The connected open oracle now executes two metadata/cache success branches:
existing regular file with truncate, and newly created empty inline file.
Both run actual compiled `opencfg`/directory path code against native with
the same selected `dir_fetchmatch`, allocator and commit cuts. The selected
`g2_lfs_cache_zero` and `g2_lfs_cache_fill` C bodies execute directly, and
native executes its original cache zero and reverse-fill sequence. The
comparison includes file and filesystem state plus the 16-byte allocated
cache. **15/15** connected fixtures pass. Physical flash I/O, successful
directory commit, and arbitrary path matching are still not covered by
these bounded cases.

The `dir_find` disk-name callback had a confirmed signed-comparison defect:
its shorter-name branch returned `-1` while native returns
`LFS_CMP_LT=1`; longer-name returns `LFS_CMP_GT=2`. Corrected the C branch
and added direct actual compiled-C/native callback cases for shorter, equal,
and longer names, cutting only the same selected `bd_cmp` operation. The
connected oracle now passes **18/18**, and the fresh **209-unit** M55 Werror
archive compile/relocatable link passes. Sources were frozen again for the
all-six snapshot after this correction.

After the fresh all-six snapshot, the wider Main unresolved frontier held
**452** symbols, mostly typed product/runtime data cells. One genuine shared
code import was `osEventFlagsSet`, original `0x4495e4`. New
`cmsis_event_flags_set.c` implements the complete CMSIS wrapper: invalid
handle/mask rejection, task-context `xEventGroupSetBits`, ISR pend with
success/error handling, current bits OR, and ICSR yield-pend write when a
higher-priority task wakes. Its children bind already selected
`audio_irq_context`, `xEventGroupSetBits`,
`xEventGroupSetBitsFromISR`, and `audio_uart_event_get_isr`. Actual compiled
C/native comparison passes **6/6** for null, invalid mask, task success,
ISR failure, ISR success without wake, and ISR success with wake; lower
FreeRTOS children are identically cut, so waiter-list and daemon scheduling
semantics retain their separate source evidence. The dedicated Audio UART
archive is **210 C units**, M55 Werror compile and relocatable link PASS.

Power's authenticated original-address map binds five public enable/disable
names plus the two Audio I2S names to the existing experimental
`g2_power_vendor_enable` `0x47f5b8` and disable `0x47f7ae` bodies. Those names
now alias the two compiled bodies; the alias changes symbol closure only.
Product descriptor/clock/configuration cells and unqualified active branches
remain explicit. The fresh aggregate Main experimental build after the first
five aliases passed with **1,397 definitions / 446 imports / zero duplicate
strong providers** at `audio-shared-event-power-stage/receipt.json`.

`imu_aid_status.c` reduces native `semantic_get_aid_enabled` `0x4a4822` to
its actual volatile byte load from product RAM `0x20074fd8`, represented by
typed `g2_imu_aid_enabled_cell` import. Actual compiled-C/native comparison
passes **5/5** for byte values 0, 1, 2, 127 and 255. The next aggregate
Main experimental build after adding the two Audio power aliases and IMU
status passes with **1,400 definitions / 444 imports / zero duplicate
strong providers** at `audio-shared-event-power-imu-stage/receipt.json`.
The IMU RAM cell is a live state input; no initializer is inferred.

Two substantial service-settings bodies are now reduced in
`display_auto_brightness.c`: `SVC_Settings_AutoBrightnessOpen` native
`0x46c01c` (186 bytes) and Close `0x46c0e8` (104 bytes). Their connected
sensor-hub children `HUB_Open` `0x4a6d58` and Close `0x4a6dca` (114 bytes
each) are reduced in `display_hub_channel.c`, including product-mode and
master-role gating, enabled-state byte, channel-4 message construction,
role denial, full authenticated diagnostic and compact-log branches. The
sender remains a genuine typed code import at native `0x4a6a1a`.
Three live product cells stay typed: auto-brightness enabled
`0x20072daa`, HUB role `0x20004526`, and existing role/mode cells.
Actual compiled C/native connected comparison passes **13/13** across
open/close mode gates, disabled, wrong role, master message, HUB left-role
denial, and extended-log branches, cutting the same HUB sender/logger lower
while checking emitted eight-byte message, log count/level/line, and return.
The dedicated Audio UART archive is **213 C units**, M55 Werror compile and
relocatable link PASS. Fresh aggregate Main experimental build at
`audio-autobrightness-hub-stage/receipt.json` passes with **1,404 definitions
/ 445 imports / zero duplicate strong providers**. The net import count
reflects two public settings bodies closed while three new typed lower/data
contracts are exposed; it is not a whole-image completion measure.

`display_hub_send.c` now reduces native `HUB_SendMessage` `0x4a6a1a` (108
bytes): null record/queue checks, selected CMSIS queue put with priority and
timeout zero, failure status and both authentic diagnostic branches. Queue
handle ownership is a typed live RAM cell `audio_hub_send_queue` at
`0x20003670`. The connected settings/HUB oracle has expanded to **15/15**:
native now executes the original sender body and compiled C executes this
new body, with the same CMSIS queue operation cut; it compares message
payload and queue-failure extended-log count/level/line. The fresh aggregate
Main candidate at `audio-hub-sender-stage/receipt.json` passes with **1,405
definitions / 445 imports / zero duplicate strong providers**. This swaps
one code import for a live queue data contract; the queue constructor and
initialization owner remain to be attributed.

The initializer audit now attributes two of those live cells to concrete
source-owned bodies. `display_hub_role_init.c` implements native
`hub_role_init` `0x4a6d28`, writing HUB role `3` for device role `1`, role
`2` for device role `2`, and otherwise leaving the prior value.
`display_auto_brightness_configure.c` implements native
`settings_configure_auto_brightness` `0x46c158`: setting the enabled byte,
conditionally opening when worn, or clearing both the enabled byte and the
profile word `0x20072dac` before closing. The connected actual C/native
oracle now passes **21/21**, including cell-state and message comparisons.
The dedicated Audio UART archive is **216 C units**, M55 Werror compile and
relocatable link PASS. HUB queue handle `0x20003670` is written by the
authenticated native `HUB_ResourceInit` `0x4a66ee`, which creates a 50-entry
8-byte queue and a timer; its full source body is the next connected gap.

`display_hub_resource_init.c` reduces native `HUB_ResourceInit` `0x4a66ee`
with its queue constructor (50 entries of eight bytes), guarded one-shot
CMSIS timer constructor, authentic timer attributes, and all four diagnostic
branches. `display_hub_timer_callback.c` reduces native `0x4a696c`: it copies
an eight-byte product message template, replaces the first halfword with
command `8`, and calls the selected HUB sender. The queue cell at
`0x20003670` and timer handle at `0x20074908` now have an authenticated
initialization owner. The timer control block at `0x20073650` (44 bytes) and
message template at ROM `0x78e47c` stay typed external data contracts; no
arbitrary product initialization is supplied. `audio_uart_timer_new`
(native `0x4493b0`) is the newly exposed genuine code contract.

`verify_hub_resource.py` executes actual compiled C and original Thumb bytes,
with identical selected queue/timer constructor and logger cuts: **5/5**
resource success/failure/existing-timer/callback cases pass. It does not
establish CMSIS internals, log string identity, or live hardware behavior.
The dedicated UART archive is **218 C units**, Cortex-M55 `-O2 -Wall -Wextra
-Werror` compile and relocatable link PASS. Aggregate Main experimental
receipt `audio-hub-resource-stage/receipt.json` passes with **1,409 defined
symbols / 449 unresolved / zero duplicate strong providers**, candidate SHA256
`5ab5f3420008f5816b95d554264ec88dfb6b42df5f15bb1e5cf1f09d2413ab63`.
The full image remains incomplete; runtime/data contracts and many source
bodies are still unresolved. Power-provider aliases remain experimental and
do not close known whole-body branch differences.

The timer/settings continuation adds three candidate translation units:
`cmsis_timer_new.c` reduces native `osTimerNew` `0x4493b0` and callback bridge
`0x449398`; `cmsis_timer_freertos.c` reduces FreeRTOS timer dynamic/static
constructors `0x47e6dc`/`0x47e712`, shared setup `0x47e75a`, and timer ID
getter `0x47eb26`; `display_settings_save_config.c` reduces native
`SVC_Settings_SaveSettingConfigToKVCheck` `0x46be7c` plus its save-event
wrapper `0x448e34`. The timer setup uses the already selected
`audio_daemon_initialize_queue` implementation of native `0x47eab8`, avoiding
a duplicate provider. Product settings comprise a CRC-covered 26-byte prefix
of a larger live object at RAM `0x20072da8`, a previous-config pointer cell
at RAM `0x20003700`, and the shared event handle `g2_audio_log_event_handle`
at RAM `0x20074570`; these remain typed runtime/data contracts. The source
only signals the event when the first 24-byte CCITT CRC changes. Its bitwise
polynomial `0x1021` agrees with the authenticated table at ROM `0x6c0b50`
on 100 randomized inputs.

`verify_timer_new.py` runs actual compiled C and original Thumb bytes through
**8/8** valid/failure/static/dynamic constructor cases, cutting the same
IRQ, heap and lower FreeRTOS constructors. `verify_timer_freertos.py` passes
**6/6** actual C/native dynamic/static/ID cases, cutting only selected heap,
queue-init and critical helpers. `verify_settings_save.py` passes **3/3**
actual C/native changed/equal/event cases, executing the original table CRC
and compiled source recurrence. These bounded results do not establish full
scheduler behavior or product RAM initialization. The dedicated UART archive
is **221 C units**, Cortex-M55 Werror compile and relocatable link PASS.
Fresh aggregate Main experimental receipt
`audio-timer-settings-deep-final/receipt.json` passes with **1,416 defined
symbols / 449 unresolved / zero duplicate strong providers**, candidate
SHA256 `82729ac043eb35ed0668f3604dd5db33095fb49e5d5457d27a50e51c5fbdb9e5`.

`display_settings_init.c` now reduces native `SVC_Settings_Init` `0x46be10`
through its 80-byte state reset, three authenticated persisted-record copies
(28, 4, and 12 bytes), ALS scale application, dump, battery callback
registration, display-level application, and peer config send.
`display_settings_battery_callback.c` reduces native callback `0x46b3e4`
through its null-data diagnostic and event 0/1 paths, writing CHG state at
live settings offsets `+0x38`/`+0x3c` before status notification.
`verify_settings_init.py` compares actual compiled C with original Thumb bytes
and passes the restored 80-byte state plus ordered lower-call captures.
`verify_settings_battery.py` passes **4/4** actual C/native branch cases.
Downstream code imports remain for dump, ALS, charging, status and peer/display
paths, while manager pointer cells at RAM `0x20003700`, `0x20003714`, and
`0x20003718` remain typed product runtime data. The dedicated UART archive is
**223 C units**, Cortex-M55 Werror compile and relocatable link PASS. Aggregate
Main experimental `audio-settings-init-battery-stage/receipt.json` passes
**1,418 definitions / 459 imports / zero duplicate strong providers**, SHA256
`243398bb086944a0f865fd449265d99e80d5cc580921e11386f3f36011a6379a`.
The increased import count exposes real children and data, not regression of
previous selected providers.

The connected settings/notification pass adds **16 native-backed C units**
from `display_settings_apply_send.c` through
`display_settings_notify_ble.c`, including the six-function ALS curve,
charger callback manager, display level tables, peer queue transport,
104-byte status construction, nanopb notification staging, unread count,
left-version throttle, and BLE notification role/OTA gates. These are full
bounded source bodies with real lower calls; product RAM, protobuf descriptors,
and BLE message queue state remain typed imports. The ALS threshold table and
display profile tables are copied from authenticated ROM extents. Focused
actual compiled-C/original-Thumb comparisons pass: settings send 6/6, ALS
11/11, charger registration 2/2, callback manager 7/7, status notify 3/3,
peer transport 5/5, full status 4/4, notify common 4/4, nanopb buffer write
5/5, unread 4/4, left version 7/7, and BLE notify 4/4. Formatter, protobuf
encode, BLE TX, and configuration ownership beyond these cuts remain open.
The dedicated UART candidate archive is **239 C units**, Cortex-M55 Werror
compile and relocatable link PASS. Fresh Main experimental aggregate
`audio-settings-notify-ble-stage/receipt.json` passes with **1,441 defined
symbols / 483 unresolved / zero duplicate strong providers**, candidate SHA256
`ed06fae372d5b01b5f30d6bea3d61d6f7f587b133a601d5a94dbd1af61d4e297`.
This is a source candidate graph, not complete image link or runtime proof.

The next BLE transport pass reduces native `Thread_MsgTxByBle` `0x47564e`
(1002 bytes) and three real guard predicates (`0x4487ac`, `0x46f258`,
`0x46f1d0`) in `display_ble_msg_tx.c` and `display_ble_role_ota.c`.
The transmit body now performs the four native framing layouts, allocation,
queue count/capacity backpressure, dispatch, thread wakeup, and failure frees.
The manager at RAM `0x20004020` is a live 16-byte struct, not a pointer cell;
an initial candidate/oracle mismatch exposed and corrected this distinction.
Actual compiled C/native comparisons pass 8/8 transmit cases (null message,
null queue, all four layouts, ESS half-full drop, queue failure) and 5/5 for
each role/OTA predicate with diagnostics disabled. Diagnostics are source-defined
from authenticated strings but not yet runtime-oracled. The UART candidate
archive is **241 C units**, Cortex-M55 Werror compile and relocatable link
PASS. Main experimental aggregate `audio-ble-tx-stage/receipt.json` passes
**1,445 definitions / 488 unresolved / zero duplicate strong providers**,
SHA256 `3c840e99bf1b3d269711267ee92c0f082cd2c1335868b35eafe382e887b59292`.
The nine newly exposed BLE/OTA queue, manager, and state imports are explicit
lower/data contracts; source completion remains false.

The next connected BLE lower pass adds `display_ble_queue_getters.c`
(CMSIS queue capacity and task/ISR count), `display_ble_connected.c`
(authenticated connection marker `0xa3`), and
`display_ble_fast_mode.c` (30,000-tick wrap-safe rejection throttle and
remove/push-delayed event). The queue wrappers reuse selected FreeRTOS count
providers; the delayed-event callback and live RAM cells remain typed source
contracts. Compiled C/native checks pass queue count/capacity 3/3 each and
fast-mode scheduling/throttle 5/5. The source archive now has **244 C units**,
Cortex-M55 Werror compile and relocatable link PASS. Fresh Main experimental
aggregate `audio-ble-lowers-stage/receipt.json` passes **1,449 definitions /
491 unresolved / zero duplicate strong providers**, SHA256
`1d51db262172d32d9f11b48de782cb4ac6df2e7e35ccd9dc48f8a5e6343f6f0f`.

`display_ble_ota_status.c` adds the two native packed OTA status getters at
`0x47d8b8/0x47d8c2`; both read the authenticated shared byte at RAM
`0x20075043`. The dedicated candidate archive has **245 C units**, Cortex-M55
Werror compile and relocatable link PASS. Main experimental aggregate
`audio-ble-ota-status-stage/receipt.json` passes **1,451 definitions /
490 unresolved / zero duplicate strong providers**, SHA256
`d1bc1eb5cf7abed0d55e1415f3e4fb4af734d78a06e89afad54108487ceb22e2`.
The larger connected event-loop push/remove/timer callbacks and their product
scheduler cells remain genuine source work; no full-firmware claim follows.

The event-loop connection now includes native immediate `fw_event_loop_push`
`0x4766ec`, delayed push/remove `0x47697e/0x476ace`, and timer callback
`0x4767a8`. The C bodies preserve the 64 callback/argument/deadline slots,
mutex sequence, tick subtraction, expiry enqueues, next timer start, and queue
error handling. Product RAM at `0x200745ec/f0/f4/f8/fc`, `0x20074600`, and
`0x2006dad4` remains typed live state, with no invented initializer values.
Actual compiled C/native bounded checks pass immediate push 4/4, delayed
push/remove 5/5, and timer callback 5/5. The candidate archive is **248 C
units**, Cortex-M55 Werror target compile and relocatable link PASS. The
terminal Main experimental aggregate `audio-event-loop-stage/receipt.json`
passes **1,455 definitions / 494 unresolved / zero duplicate strong
providers**, SHA256
`68e7e623fed2999d1d7b744c7344a549c9299203b4779bb182ead637040d31e1`.
Source complete remains false; hardware/scheduler concurrency and complete
image proof are outside these bounded tests.

Post-checkpoint BLE connection work adds native `_connectParamReq` `0x47761c`,
`_connectParamReq_impl` `0x47720c`, and `fw_event_loop_initialize/task`
`0x4764e0/0x476680`. The request path now implements peripheral/DM/terminal
gates, interval profile decisions, duplicate backoff, 12-byte WSF messages,
and delayed callback composition. The event initializer uses authenticated
ROM queue/timer/mutex/thread attribute fields, with exact RAM control and
stack contracts. Focused actual compiled-C/native comparisons pass request
6/6, implementation 8/8, and event initialization 2/2. The task's 8-byte
argument/callback queue layout is also verified through immediate-push tests.
Aggregate `audio-connect-event-loop-stage/receipt.json` passed **1,459
definitions / 513 unresolved / zero duplicate strong providers**, SHA256
`70c5f51c62ded3c23c3915096dd4fb641fb5ab1ca3073ed51497dc6ddb6ea63a`.

The next source chunk adds native DM connection pointer getter `0x46efcc`,
fast/slow interval classifiers `0x476db8/0x476fe2`, WsfMsgAlloc/Send
`0x4bf99e/0x4bf9ba`, and WsfMsgEnq/TaskMsgQueue/TaskSetReady
`0x4bf9de/0x52b97c/0x52b95e`. The slow profile `{0,0,72,84,4,600}` is
copied from authenticated ROM `0x784ea0`; WSF task queue and ready bits share
live RAM object base `0x20073230`. Actual compiled-C/native comparisons pass
fast and slow classification 7/7 each and WSF message paths 3/3. The
dedicated UART archive is **255 C units**, Cortex-M55 Werror target compile
and relocatable link PASS. Fresh Main aggregate
`audio-connect-wsf-stage/receipt.json` passes **1,467 definitions / 515
unresolved / zero duplicate strong providers**, SHA256
`ad1599bf160ba9577ffcef483405ae5cd5680b6ce9b721a6c5806cfd2d69c562`.
WSF buffer allocation, queue enqueue, critical/event lower bodies and live
Cordio task state remain explicit connected work. Full image remains incomplete.

The connected WSF pool/queue chunk reduces WsfBufAlloc `0x530446`,
WsfBufInit `0x530364`, WsfQueueEnq/Deq `0x538c24/0x538c4a`,
WsfCsEnter/Exit `0x52b8a4/0x52b8b6`, WsfSetOsSpecificEvent
`0x52b8d8`, and IPSR helper `0x442228`. Pool descriptors are 12 bytes;
caller-owned pool storage/configuration and the live list/count/used-byte
cells remain typed imports. Actual compiled-C/native comparisons pass pool
allocation 3 cases, queue enqueue 2, dequeue 3, and initializer 5,
including zero pools, multi pools, and undersized storage. The event setter
and interrupt effects have target compilation but no runtime equivalence
claim. Dedicated `audio-wsf-pool-queue-stage/receipt.json` passes Main
relocatable link with **1,475 definitions / 515 unresolved / zero duplicate
strong providers**, SHA256
`dc8d5ff711bb4c7837c43930b789dc38c41b3857c04d35cdec6dba048553b1ed`.
The increase in imports includes genuine WSF runtime state; source complete
remains false.

The next Main source pass binds the event-loop queue receive call to the
already selected complete CMSIS `osMessageQueueGet` C provider. It also
reduces five LV display field setters (`0x44fa3e/5e`, `0x44fbfc`,
`0x44fc18/2e`) and binds the object allocator to the existing exact
`0x44f718` LV malloc body. Actual compiled-C/native field comparisons pass
10 explicit/default-display cases. The LV root remains typed RAM at
`0x2006f548`; geometry invalidation `0x440656` is a genuine outstanding child.

Authentic compressed SRAM initialization (descriptor `0x75d3f4`, handler
`0x43a11e`, decoded SHA256
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`)
supplies the Cordio pool table at stock RAM `0x200003b0`: `{16,8}, {32,4},
{64,10}, {480,20}`. Startup `0x4b7f64` passes a `0x2940`-byte arena and
count four. These values are now typed C objects alongside BSS cells that
the native-equivalent initializer writes. Absolute RAM placement and the
full BLE startup call graph remain open. Dedicated
`audio-wsf-pool-data-stage/receipt.json` passes Main relocatable link with
**1,486 definitions / 506 unresolved / zero duplicate strong providers**,
SHA256 `186ac13116ba8eb854cb765790e2fc91bb68d9ed13eb494af7a2f55c585a40b1`.
Source complete remains false.

The FreeRTOS scheduler's 61-list initialization is now backed by typed C
storage for 56 ready lists and five other 20-byte lists. The existing native
`0x45568c` list initializer was changed from absolute stock addresses to
these symbols, preserving 61 calls and assignment of both delayed-list
pointer cells. Ten live scheduler counters/pointers have typed BSS ownership
at their authenticated stock RAM roles. The updated actual compiled-C/native
oracle `verify_thread_list_init.py` passes normalized call order and pointer
targets. Dedicated `audio-scheduler-ram-stage/receipt.json` passes Main
relocatable link with **1,501 definitions / 494 unresolved / zero duplicate
strong providers**, SHA256
`005826629a168017d2c3521bd9ca6e13a9e5ccc52b01de5da214a12bd31d4264`.
Final RAM placement and live scheduler execution remain unqualified.

The LV geometry continuation reduces native `lv_obj_invalidate`
`0x440656`, `lv_obj_invalidate_area` `0x4405d4`,
`lv_display_is_invalidation_enabled` `0x44fed2`, and LV object
screen/display traversal `0x44dbc4/0x44dc0a`. The invalidation path
preserves the authenticated null assertion/fault branch and translates
the 16-byte area using the parent ext draw size. Its visible-area test and
render invalidator remain genuine children. Actual compiled-C/native
comparisons pass **8 geometry**, **4 invalidate-area**, **7 active-display**,
and **4 screen/display registry** cases. The LV display registry root is
live RAM `0x2006f54c`; its screen-array traversal has controlled branch
coverage, not a complete UI runtime proof. Dedicated
`audio-lv-object-display-stage/receipt.json` passes Main relocatable link
with **1,507 definitions / 495 unresolved / zero duplicate strong
providers**, SHA256
`d4864080d8fff44d9983a7432b53d1b9140ba90dc10b5e4ab00fd684003bab9e`.
Source complete remains false; connected LV visible-area and render
descendants plus hundreds of other product/runtime contracts remain.

Cordio `WsfOsInit` `0x52b9b2` now has its full 64-byte task-state reset and
conditional event-group creation in C. Its live task-state array at stock
`0x20073230` and event-group pointer cell `0x20074ef0` have typed BSS
ownership; the allocator is the already selected `0x47ebd8` C body. Actual
compiled-C/native checks pass both existing and missing event-group states.
Dedicated `audio-wsf-os-init-stage/receipt.json` passes Main relocatable link
with **1,510 definitions / 493 unresolved / zero duplicate strong providers**,
SHA256 `cc226f38aae4e1425478b74e54274f2ef7e48f7a0a95a96ceec791782a614bc0`.
BLE startup and runtime scheduling remain outside this bounded proof.

The authenticated BLE startup `_bleExactleStackInit` `0x4b7f64` is now a
source-order C body: WSF OS/timer/pool setup using recovered pool data,
then DM, L2CAP, ATT, SMP and HCI registrations with all eight handler
callback targets taken from native relocations. Every unrecovered Cordio
child remains a typed function import. Actual compiled-C/native
`verify_ble_stack_init.py` compares **44 ordered child calls**, all eight
handler pointer arguments, the pool's four setup arguments, and the HCI
ACL length; the bounded test cuts all children identically. Dedicated
`audio-ble-stack-init-stage/receipt.json` passes Main relocatable link with
**1,511 definitions / 536 unresolved / zero duplicate strong providers**,
SHA256 `d2f7dea181ecdd5bf3d48e393217647da81d3f88c4242fa007849023799d98b8`.
The higher import count exposes genuine Cordio provider work; it does not
indicate a complete BLE stack or full firmware image.

The connected Cordio scheduler lowers `WsfOsSetNextHandler` `0x52b980`
and `WsfTimerInit`/callback `0x52a474/0x52a468` now have C bodies. The
handler registration writes exact indexed callbacks into the 64-byte WSF
task state; actual compiled-C/native comparisons pass five indices. Timer
initialization clears its two-word list, conditionally constructs the
authenticated `"WSF Timer"` 10-tick FreeRTOS timer, records task tick, and
uses the real stock `ulSetInterruptMask` (`BASEPRI=0x30`, DSB, ISB) before
the authenticated invalid-address fatal write if construction fails. Its
callback sets ready bit two.
Actual compiled-C/native checks pass existing/new timer branches and
callback arguments. Dedicated `audio-wsf-timer-handler-stage/receipt.json`
passes Main relocatable link with **1,517 definitions / 535 unresolved /
zero duplicate strong providers**, SHA256
`6b1cb37efbe8547875a648833391a7b1ad807e152a20840293f55a8bee806e91`.
Full Cordio/FreeRTOS interaction remains unqualified.

The BLE startup descendant round reduces native `DmHandlerInit` `0x4d2a46`,
`L2cSlaveHandlerInit` `0x536f6a`, `SmpHandlerInit` `0x537cb2`, and
`HciSetMaxRxAclLen` `0x52acce`. Their authenticated DM/L2CAP/SMP/HCI
state blocks now have typed BSS storage. The SMP row loop writes three
76-byte rows and retains real database/L2CAP/DM registration children with
native callback pointer targets. Actual compiled-C/native comparisons pass
eight handler/state/call cases (two handler IDs per body). Dedicated
`audio-ble-handler-stage/receipt.json` passes Main relocatable link with
**1,526 definitions / 538 unresolved / zero duplicate strong providers**,
SHA256 `bc773379ef585e69791c8cc6965af7407e8dbf55afd0ac24de464bf339528ab6`.
The import increase exposes real SMP registration and callback lower bodies;
BLE stack completeness remains false.

The next Cordio DM source pass implements native `DmAdvInit` `0x4bac2c`,
`DmPhyInit` `0x4c584a`, master/slave connection init
`0x536a98/0x536b18`, security/LESC init `0x4d250c/0x53496a`, and privacy
init `0x4d27e0`. `WsfTaskLock/Unlock` `0x52b8c8/0x52b8d0` now call the
selected critical section C providers. Shared DM control RAM `0x20000694`
is a typed **source-initialized data contract**; authenticated ROM dispatch
table addresses remain typed imports. Separate live DM state/ready cells
have BSS ownership. Actual compiled-C/native comparisons pass all seven
body-specific table writes and ordered child calls. Dedicated
`audio-ble-dm-stage/receipt.json` passes Main relocatable link with
**1,539 definitions / 545 unresolved / zero duplicate strong providers**,
SHA256 `42c64cb6ca58644a8d7e7a300021159aa5cbb267a99a2606e499e2a70a5f8b75`.
The higher import count includes authentic DM ROM table/data contracts.

The L2CAP/SMP continuation reduces native `L2cInit/Register/SlaveInit/
MasterInit` `0x530b34/5e`, `0x536e78`, `0x537200`, plus
`DmConnRegister` `0x4b6c64` and `SmpDbInit` `0x542288`. L2CAP's shared
state and SMP's 256-byte database have typed BSS ownership; the DM
connection registry extent stays an explicit RAM contract. Native callback
targets are typed function imports. Actual compiled-C/native comparisons
pass five L2CAP table transitions, four DM registration indices, and both
SMP database timer branches. The bounded tests cut the real timer-stop,
lock and HCI-registration children. Dedicated
`audio-ble-l2c-smp-stage/receipt.json` passes Main relocatable link with
**1,547 definitions / 550 unresolved / zero duplicate strong providers**,
SHA256 `e5715a06921a27f8e8f5c372d52f1593377d10b0f7bf544049eb4bcfbe55b42b`.
Full callback and timer execution remain unqualified.

The four native SMP initiator/responder state-machine initializers
`SmpiInit/SmpiScInit/SmprInit/SmprScInit` at
`0x537eec/0x537f14/0x5380dc/0x538104` now write their authenticated
legacy/secure table and callback pointers into the shared SMP state. The
secure branches call the genuine `SmpScInit` child. Actual compiled-C/native
comparisons pass all four table/call cases. Dedicated
`audio-ble-smp-sm-stage/receipt.json` passes Main relocatable link with
**1,551 definitions / 553 unresolved / zero duplicate strong providers**,
SHA256 `cee89deb2a7cde15349e4376055d0c5e7744de7921eb64edc6d3e4b38ed94aa9`.
Authenticated ROM tables and callback bodies remain separate source/data work.

The ATT startup continuation reduces native `AttHandlerInit`, `AttsInit`,
`AttsIndInit`, and `AttcInit` at `0x4b511e/0x5351dc/0x533e40/0x531b1c`.
Typed BSS ownership now covers common ATT, 3-by-3 server/indication rows,
and 3-by-3 client rows. Five ROM tables and ATT callback bodies are explicit
typed contracts. Actual compiled-C/native comparisons pass all four full
state-grid/registration cases with pointer-address normalization.
Dedicated `audio-ble-att-stage/receipt.json` passes Main relocatable link
with **1,558 definitions / 558 unresolved / zero duplicate strong
providers**, SHA256
`970caf296f1b9f9def0346bc993e61a0b52c8260fea069a424a870abbc8670ba`.
ATT request/response runtime remains outside this initialization proof.

Native BLE startup continuation now reduces `DmConnInit` (`0x4b6c28`),
`HciSetLeSupFeat` (`0x52acd6`), `SmpScInit` (`0x56cf74`), and
`WsfTimerStop` (`0x52a4d2`). Their authenticated ROM tables, live shared
DM/HCI/SMP RAM, and callback targets remain typed contracts. Actual
compiled-C/native checks pass five cases, including both HCI feature
bitset branches and the timer-stop call chain. Dedicated
`audio-ble-conn-hci-sc-stage/receipt.json` passes Main relocatable link:
**1,562 definitions / 564 unresolved / zero duplicate strong providers**,
SHA256 `e417220052ba900157c071ca17fdccea41a4b083286024abcc8d555d329de45b`.

The genuine WSF timer removal descendants `wsfTimerRemove` (`0x52a3fc`)
and `WsfQueueRemove` (`0x538cc8`) now walk/remove the queue and clear the
started byte at offset `0x0d`, with the native critical-section order.
Actual compiled-C/native head, tail, and miss cases all pass. Dedicated
`audio-wsf-timer-remove-stage/receipt.json` passes Main relocatable link:
**1,564 definitions / 563 unresolved / zero duplicate strong providers**,
SHA256 `619fbdf13c8c83675df7c5a0b5bfdc7c9ae23fbd53458d6088cb068198cfef59`.

`HciDrvHandlerInit` (`0x4b4a7c`) now writes its five native handler-row
bytes. Four actual compiled-C/native handler values pass. Dedicated
`audio-ble-hci-driver-stage/receipt.json` passes Main relocatable link:
**1,565 definitions / 564 unresolved / zero duplicate strong providers**,
SHA256 `580ee3e532a9d82b0898016ecf6130d02415146b960cfb68f106a90d51eea428`.
Its two live row/cell addresses remain typed external runtime storage.

`bleCommHandlerInit` (`0x4b7e74`) now writes its authenticated handler ID,
two table pointers, and mode, then calls the slave/profile/master and
subsystem initializers in native order. Actual compiled-C/native checks
pass three handler values, comparing state, table pointers, and four-call
sequence. Dedicated `audio-ble-comm-handler-stage/receipt.json` passes
Main relocatable link: **1,566 definitions / 573 unresolved / zero duplicate
strong providers**, SHA256
`a48c639ede10da823cbf7cb7d3dd9d742449776d50d7c30345331714d0103fd6`.
The four child bodies and live RAM storage remain separate work.

The next connected BLE chunk reduces `bleSubsystemInit` (`0x4b7478`),
the profile handler initializer (`0x535488`), and four of the subsystem's
five direct descendants (`0x503b76`, `0x534866`, `0x532e52`, `0x4b3c02`),
plus the latter's state-clear child (`0x4b32d4`). The profile initializer
has three actual compiled-C/native pointer-grid cases passing. The
`0x4b3c02` child matches the native 128-byte link-state transition and
callback slot after cutting only its genuine privacy-list child
`0x479418`. The even ROM pointer `0x5fa056` is deliberately represented
as a data-address contract; treating it as a Thumb function pointer
produced a one-bit mismatch in the first oracle run. Dedicated
`audio-ble-subsystem-children-stage/receipt.json` passes Main relocatable
link with **1,573 definitions / 587 unresolved / zero duplicate strong
providers**, SHA256
`3569d38cfa165aee76666cfec4691540ddc7b91095f6315241af8b2ee1079c9e`.
The larger `0x479418` privacy-list path, its product row data, selected
RAM cell ownership, and startup callback bodies are still genuine code/data
frontier. Whole Main source completion and final placement remain false.

The privacy-list descendant `0x479418` is now a complete source-defined
ten-row walk with two passes, 200-byte row stride, 16-byte nonzero IRK
check, row flag update, last-entry argument, and native logging branches.
Actual compiled-C/native checks pass empty, single, and two-row inputs,
plus log policies 1, 2, and 4. The checks compare row bytes, six-argument
resolving-list calls, log strings/line numbers, and the enable call.
The product row array at `0x20067a30` stays typed external live RAM:
its loader/initializer ownership is not established by this function.

`DmSecGetLocalIrk` (`0x4d2524`), `DmPrivAddDevToResList` (`0x4d282e`),
and `DmPrivSetAddrResEnable` (`0x4d28cc`) are also source-defined. The
local-IRK getter binds the already selected `DmSecInit` state cell at
`0x20074114`. Actual compiled-C/native comparisons pass both message
allocation outcomes for both 44-byte constructors and two local-IRK cell
values; the success cases compare copied address/IRKs, event bytes,
handler route, and message ordering. Dedicated
`audio-ble-privacy-state-bound-stage/receipt.json` passes Main relocatable
link with **1,577 definitions / 588 unresolved / zero duplicate strong
providers**, SHA256
`df65249f38cc21575fdc900d9768e17a42f03c96f601f61083523429bc830ec8`.
The remaining direct privacy data imports are the live DM handler state
at `0x20073b78` and the product row array. Main source and final image
are still incomplete.

The broader BLE startup pass source-reduces seven native leaves:
`0x536324/0x53648e/0x5366cc/0x5367ca/0x5367f8/0x5369ea` and
`0x4bae6c`, plus their connected HCI core/command initialization
`0x52ac02/0x530c00/0x52aec6`, the DM stack state child `0x55ba70`,
and two 0x5367e4/0x5367ea setters. Actual compiled-C/native checks pass
all seven state grids with callback pointer normalization, including the
connected HCI reset path. The direct HCI/L2CAP/DM RAM blocks and four ROM
callbacks stay typed contracts. Dedicated `audio-ble-stack-lowers-stage`
passes Main relocatable link with **1,589 definitions / 591 unresolved /
zero duplicate strong providers**, SHA256
`516bfd67e499f0291c5c89c1f1dc22bff82d08ba57fe3eebf920cf64a778eddc`.

The product privacy startup wrapper `0x47a85c` now orders cache maintenance,
NVM row load, resolving-list registration, and ten diagnostic row calls.
Its actual compiled-C/native sequence of 13 calls passes with children
cut. The connected `_CopyRecListFromNvmToRam` body `0x4795dc` now reads
ten 200-byte records from authenticated NVM base `0x7ff000` at 256-byte
stride, derives the four-bit key mask, repairs mismatches through its
real rewrite child, loads or clears live rows, and follows native logging.
Actual compiled-C/native comparisons pass empty, invalid, valid, and
two-record paths plus log policies 1, 2, and 4. A compact log format
placeholder mismatch found by the oracle was corrected. Dedicated
`audio-ble-privacy-loader-stage/receipt.json` passes Main relocatable link:
**1,591 definitions / 594 unresolved / zero duplicate strong providers**,
SHA256 `07714bc6373a8a54741723c6c0ece5d50d88e07d7b9c2ed3233298dcb463d1a9`.
The NVM record contents, cache maintenance `0x475014`, rewrite path
`0x479b74`, and diagnostic row body `0x4789b0` remain genuine contracts;
no storage contents or device behavior have been synthesized.

The architectural cache-maintenance lower `0x475014` is now real C with
its authenticated SCB CCR/CSSELR/CCSIDR/DCISW/DCCISW/DCIMVAC/DCCIMVAC
register flow and ARM DSB/ISB barriers. Actual compiled-C/native MMIO
sequences pass seven bounded cases: disabled cache, both set/way modes,
small two-by-two geometry, zero-length range, and two unaligned range
lengths. These are emulator comparisons, not hardware cache proof.
Dedicated `audio-ble-cache-stage/receipt.json` passes Main relocatable
link with **1,592 definitions / 593 unresolved / zero duplicate strong
providers**, SHA256
`119b420a267457251647e7d357f7512577e6eaedeaf471d124f32851105fa122`.
The remaining connected privacy code includes the NVM rewrite/eviction
body `0x479b74`, its flash-write child `0x4799a8`, and diagnostic row
dump `0x4789b0`; product NVM and RAM ownership still needs attribution.

The connected NVM flash pass now source-reduces `_updateOneRecordToNVM`
`0x4799a8`, its 16-byte/4-word alignment gate `0x4d0a2c`, the lower
aligned program wrapper `0x4d09d8`, `osThreadYield`/PendSV
`0x4491e4/0x4420bc`, and flash mode entry/exit `0x47f3c6/0x47f418`.
These keep the native two 128-byte half writes, IRQ save/restore, error
mapping, 10,000-cycle status polls, mode register changes, and HAL control
calls. Actual compiled-C/native comparisons pass three write result paths,
three alignment paths, two IRQ-context yield paths, three aligned program
paths, and six flash mode/MMIO paths. The aligned oracle normalizes the
PRIMASK instructions that Unicorn Thumb rejects; it compares return values
and lower-call arguments, not interrupt hardware behavior.
Dedicated `audio-ble-flash-mode-stage/receipt.json` passes Main relocatable
link with **1,598 definitions / 596 unresolved / zero duplicate strong
providers**, SHA256
`9fdbc500b725aeb2afa6019337b6b5bd1886c7338fcd99b138f7257d80e675b4`.
The genuine `0x480312` flash control and `0x541b7c` flash execution bodies,
privacy rewrite `0x479b74`, diagnostic dump `0x4789b0`, product flash-mode
cell at `0x20074f62`, and NVM contents remain unresolved. Source and target
link evidence do not establish a loadable image or live device behavior.

The flash-control callback dispatcher `0x480312` is also source-defined:
it reads the authenticated callback slot at `0x20073270+4`, returns zero
when empty, and otherwise passes truncated byte arguments plus the unchanged
third command pointer to the installed callback. Both branches match actual
compiled-C/native bounded cases. Dedicated `audio-ble-flash-control-stage`
passes Main relocatable link with **1,599 definitions / 596 unresolved /
zero duplicates**, SHA256
`03afee5d40a4429538ddd31d6eb233232bf6d99b1fff5425c7af23157ae7f839`.
The callback table and installed target are live product-owned data, not
invented initialized values; flash execution `0x541b7c` remains genuine code.

Flash execution wrapper `0x541b7c` is now source-defined as an indirect
five-argument call through the resident table at `0x75d630+4`, followed
by the native `0xc3, 0, 0` writes to `0x40014008/0x40014024/0x40014008`.
An actual compiled-C/native callback/MMIO sequence passes. Dedicated
`audio-ble-flash-execute-stage` passes Main relocatable link with **1,600
definitions / 595 unresolved / zero duplicate strong providers**, SHA256
`9796215f98fd286cd60eab8d4bf0c1b69703ed39e6e487a244095387eb233127`.
The resident callback target and its availability at runtime remain an
external ROM contract; this does not validate flash programming on hardware.

The two remaining connected privacy bodies are source-defined. Native
`_AppDbUpdateNVM` `0x479b74` updates an existing six-byte-address match,
uses an empty record, or chooses a role-aware least-recently-used victim;
it writes, invalidates cache, verifies the replacement, and follows the
native diagnostic branches. `PrintSmpDbRecord` `0x4789b0` emits the
authenticated record fields, four 16-byte key dumps, CCCD entries, and
handle entries under the original log policies. The six-byte comparison
child `0x4d294a` is also C. Actual compiled-C/native rewrite cases pass
existing, empty, invalid-unused, invalid-used, role-LRU, and no-candidate
paths with logging disabled, plus existing/empty/LRU paths under levels
2/1/4. The diagnostic call sequence passes levels 0/1/2/4 with populated
CCCD and handle entries. These are bounded cases, not exhaustive runtime
or physical NVM proof. Dedicated `audio-ble-privacy-closure-stage` passes
Main relocatable link with **1,603 definitions / 593 unresolved / zero
duplicate strong providers**, SHA256
`8a3d54b678dd99c003de3f22f26239eb19bdcca168e9849f578393f55d927e61`.
The privacy NVM bytes at `0x7ff000`, the live record rows, callback tables,
and other product-owned configuration remain external contracts.

The next connected Main BLE provider `APP_MasterHanderInit` `0x4a19f4`
is source-defined. It installs its authenticated registration/state slots,
sets ring-link state, initializes the ring handler, sends initial status
when the device role is one, and conditionally schedules the 15-second
connection attempt with the original diagnostics. Actual compiled-C/native
comparisons pass four role/ownership/MAC combinations, including callback
identity and RAM-slot offsets with lower calls cut. Dedicated
`audio-ble-master-handler-stage` passes Main relocatable link with **1,604
definitions / 602 unresolved / zero duplicates**, SHA256
`854500f67a90e92ed2d3a8c71c7eeb63fb681a8210206e852fa29eb380ea0bb8`.
The increase in unresolved imports exposes six product registration/state
cells and four genuine child bodies: ring-link setter `0x49f870`, ring
handler initializer `0x4c4810`, BLE status reply `0x47d870`, and delayed
connection callback `0x4a23ac`. This is a connected source frontier, not
completion of Main BLE.

Two direct master-handler children are source-defined: ring-profile
initializer `0x4c4810` installs handler/state and service handles
`0x10/0x12/0x13`; status reply `0x47d870` copies the authenticated
eight-byte template, writes role/MAC fields, and dispatches command
`0x103`. Actual compiled-C/native ring state/handle comparison passes
with logging disabled, and status payload comparison passes four role/MAC
inputs. Dedicated `audio-ble-master-children-stage` passes Main relocatable
link with **1,606 definitions / 603 unresolved / zero duplicates**, SHA256
`58ed944e8ee49edeb2e31c5f0ebea577d502459e371d9382f229e4c1fdaa23fe`.
New contracts include ring state RAM `0x20074074`, status template ROM
`0x78edf4`, status-send body `0x464d1c`, ring-link setter `0x49f870`, and
delayed connection body `0x4a23ac`.

Ring-link enum name `0x49f828` and transition setter `0x49f870` are now
C bodies with all seven authenticated names, stay/change logging, and
the live state byte at `0x20074f85` external. Actual compiled-C/native
comparisons pass five stay/change and log-policy cases, including an
out-of-range enum. Dedicated `audio-ble-ring-link-stage` passes Main
relocatable link with **1,608 definitions / 603 unresolved / zero
duplicates**, SHA256
`4f3d1bf95c016aa86a4050996831ceb6c3b4efd535ea31c4d4ea8ca02b86dbc5`.
The status-send body `0x464d1c` and delayed master callback `0x4a23ac`
remain genuine connected code imports.

The connected send and delayed callback bodies are now C. Native
`SendDataToBoth` `0x464d1c` allocates a 12-byte owned queue node and
payload, writes the `1/9` frame header and application/length fields,
enqueues with a 2,000-tick bound, wakes the event, and frees both
allocations on queue failure. Actual compiled-C/native comparisons pass
missing queue, first and second allocation failure, successful enqueue,
and queue failure. Native `APP_MasterSysStartTryConnectRing` `0x4a23ac`
copies the product MAC and authenticated 14-byte name seed, skips
non-owner, absent-MAC, and local-disconnect cases, and otherwise sets
target/auth state and schedules connection. Four actual compiled-C/native
branch comparisons pass. Its target setter `0x4a2068`, auth setter
`0x4a2168`, and scheduler `0x4a2618` pass seven bounded child cases;
cancel retry `0x4a17f4` and ring event forwarder `0x4a153c` pass three
state cases; event emitter `0x4ac16c` passes three product-mode/payload
cases. Dedicated `audio-ble-master-event-stage` passes Main relocatable
link with **1,616 definitions / 609 unresolved / zero duplicates**,
SHA256 `5df778da7981e4d297faae9f3bdd367885c8c25c7aa394aed63de19ba1674dc2`.
Product master state/registration/target cells and resident ROM templates
remain authentic external contracts. The newly exposed real code frontier
includes device-manager send `0x4c659a` and master connect event
`0x4a1b60`; the target build does not establish hardware operation.

### BLE device-manager and master connect event, 2026-10-11

- Added `display_ble_device_manager_send.c`: native `DEV_SendMessage` `0x4c659a`, including queue guard, CMSIS queue call, byte error counter wrap, and both diagnostic paths. `verify_ble_device_manager_send.py` compares actual ARM-compiled C with stock bytes for five null/success/error/wrap transitions (PASS).
- Added `display_ble_master_connect_event.c`: full native `APP_MasterConnectEvent` `0x4a1b60` branch graph, queue message layout, role/target checks, retry/success scheduling, and diagnostics. `verify_ble_master_connect_event.py` compares actual ARM-compiled C with stock bytes for seven state/message paths (PASS); child calls and log level are controlled cuts. The ring peer address lower is native `0x4b6eea`; its ownership remains external.
- Added `display_ble_master_connect_state_children.c`: native retry reset `0x4a2300`, failure notify clear `0x4a15c0`, and target link match `0x4a2864`. All three compile with ARM `-Werror`; their complete connected runtime behavior is not yet independently compared.
- Dedicated build `g2/build/c-firmware/20261011/audio-ble-master-connect-children-stage/receipt.json`: apollo_main relocatable link PASS, 1621 defined / 619 unresolved / zero duplicate strong symbols, SHA-256 `85e495377424a88bf544a3952a003276b8ccfd5cd265ea98d575258940f1e562`.
- Newly exposed typed contracts include product RAM `0x2000060c`, `0x20074fb2`, `0x20074f82/83/84/89`, pointer cell `0x200742fc`; genuine callback bodies `0x4bc418`, `0x4c4ee4`, `0x4a01fc`; and Cordio `DmConnRole`/`DmConnPeerAddr` source mapping. The 619 unresolved symbols mix code, product data, ROM, and hardware contracts. This stage remains an experimental source candidate; source completeness and runtime/hardware equivalence are false.

### Connected master delayed callbacks and slave advertising, 2026-10-11

- Added `display_ble_master_connect_callbacks.c`: native `_masterConnectCancel` `0x4a01fc` and `PB_TxEncodeNotifyRingConnectInfo` `0x4bc418`. The latter checks the controller/handler, allocates the 12-byte WSF message, and emits event `0xbb`; the former emits cancel event `0xb0`. `verify_ble_master_connect_callbacks.py` compares four actual ARM-compiled C/native allocation/handler/message cases (PASS). The callback return is void where native caller ignores it; no synthetic success provider was used.
- Added `display_ble_master_touch_followup.c`: native `app_ring_enable_touch` `0x4c4ee4`, ring touch message wrapper `0x472426`, and connection getter `0x46efd8`. `verify_ble_master_touch_followup.py` compares disconnected/connected paths (PASS).
- Added `display_ble_slave_advertising_restart.c`: native `APP_BleSlaveAdvStartEvent` `0x46ee70`, WSF event `0xb6`. `verify_ble_slave_advertising_restart.py` compares allocation failure and send paths (PASS).
- Final dedicated Main candidate build `g2/build/c-firmware/20261011/audio-ble-master-chain-stage/receipt.json`: relocatable link PASS, 1627 defined / 617 unresolved / zero duplicate strong symbols, SHA-256 `2d887b043d176191105ec4bbf786d66febe9d573382d46a501076673fbe56aed`. This is a qualified source candidate, not complete Main firmware.
- Remaining directly connected imports are principally product runtime cells (master state/context/target, device manager queue/error, profile controller context), Cordio `DmConnRole`/`DmConnPeerAddr`, plus the wider 617-symbol Main frontier. Native comparisons cut logging and external WSF/event children, and do not prove live radio or full image behavior.

### Cordio connection accessors and slave initialization, 2026-10-11

- Added `display_ble_dm_connection_accessors.c`: Packetcraft Cordio `DmConnRole` `0x4b73c4` and `DmConnPeerAddr` `0x4b6eea` over the native 48-byte connection record array at live RAM `0x200712a4`. Role validates IDs 1-3 and reads offset +25; peer accessor retains native unguarded pointer arithmetic. `verify_ble_dm_connection_accessors.py` compares actual ARM-compiled C/native across six role IDs and three peer addresses (PASS). The record storage is a typed external runtime contract, not synthesized initialization.
- Added `display_ble_slave_handler_init.c`: native `APP_SlaveHanderInit` `0x46ed94` with authenticated table slots, controller/mode pointers, mode byte clear, and all eight ordered downstream calls. `verify_ble_slave_handler_init.py` compares registration roles and child call order against stock bytes (PASS).
- Added `display_ble_slave_service_inits.c`: native message TX configuration `0x4780dc`, OTA handler `0x4bdd00`, EUS `0x4bdf98`, ESS `0x4be2d6`, EFS `0x4be524`, and NUS `0x4be7fa` setup. `verify_ble_slave_service_inits.py` compares four profile handler-state transitions with stock bytes (PASS). Message TX and OTA initialization compile and enter the selected graph; their wider runtime path remains unqualified.
- Added `display_ble_ancc_init.c`: native ANCC init `0x4bf742`, with exact two zero ranges, controller/mode pointer slots, and reset call; `verify_ble_ancc_init.py` PASS. Added `display_ble_slave_reset_children.c`: ANCC reset `0x4bf6c4` and OTA export reset `0x4486bc`; `verify_ble_slave_reset_children.py` compares both actual ARM C/native effects and child arguments (PASS).
- Dedicated `g2/build/c-firmware/20261011/audio-ble-cordio-slave-reset-stage/receipt.json`: Main relocatable link PASS, 1639 defined / 639 unresolved / zero duplicate strong symbols, SHA-256 `34f644bfe361f4a4386e5dbd48537875b5a9b250814c1c4893e7b296b3a0599f`. Newly exposed imports are predominantly source-owned or live product data slots for Cordio/slave/ANCC/message TX and genuine `audio_ble_ota_export_mode_set` body `0x478860`. Source completeness and hardware behavior remain unproven.

### OTA bootloader flag write, 2026-10-11

- Added `display_ble_ota_export_mode.c`: full native `OTA_FileSystemSetBootloaderFlag` `0x478860` no-change and write paths, diagnostic records, 16-byte seed copy, authenticated `0x12344321` flash command, four-word write through selected `audio_ble_nvm_write_words`, unconditional PRIMASK restore, and failure diagnostics. The mapped bootloader flag at `0x007fe000` and ROM seed at `0x784ed0` remain typed external data contracts.
- `verify_ble_ota_export_mode.py` compares actual ARM-compiled C/native no-change, successful write, and failed write lower-call arguments (PASS). Unicorn cannot execute the native `MSR PRIMASK` instruction in this harness; the comparison skips that exact architecturally decoded instruction on both sides. The C source emits `MSR PRIMASK` and target compilation passes. This proof does not establish physical flash safety or execution.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-ota-export-stage/receipt.json`: Main relocatable link PASS, 1640 defined / 640 unresolved / zero duplicate strong symbols, SHA-256 `fbcc9999c692dd6f9c2b8b78dd6c812aa22ff9a0a2c6d2322a738c84f524f5ce`. The one newly exposed import is the authenticated ROM seed data contract. Full Main source completion remains false.

### BLE advertising name and custom address, 2026-10-11

- Added `display_ble_adv_name_set.c`: native `_bleAdvNameSet` `0x46dd44`, including service-mode name selection, address copy, four ordered helper calls, diagnostic arguments, controller vendor command, and native invalid-context fault path. `verify_ble_adv_name_set.py` compares two actual ARM-compiled C/native normal paths (PASS). The invalid-context fault path has static native attribution but no execution oracle.
- Added `display_ble_adv_name_children.c`: native `dmSlaveAdvFormatData` `0x46dc74`, `dmSlaveAdvSetScanRsp` `0x46dca4`, `_blePsnIntoADV` `0x46dc14`, and `ble_Slave_handler_1` `0x46dccc`; the offset layout of the shared advertising buffer is authenticated from native literals. `verify_ble_adv_name_children.py` compares actual ARM-compiled C/native format and scan-response calls in two bounded cases (PASS). The PSN and slave handler branches compile but remain untested at runtime. The real `sprintf`-style formatter `0x4b4728` and version scanner `0x475fc0` remain genuine child contracts, not special-case substitutes.
- Added `display_ble_custom_bd_address.c`: native `HciVscSetCustom_BDAddr` `0x4b4cd2` zero/null guard and nonzero six-byte copy. `verify_ble_custom_bd_address.py` compares three actual ARM-compiled C/native cases (PASS).
- Dedicated `g2/build/c-firmware/20261011/audio-ble-adv-custom-bd-stage/receipt.json`: Main relocatable link PASS, **1646 defined / 644 unresolved / zero duplicate strong symbols**, SHA-256 `292e36af407374127b31f8081c6dba41badc6b3c921e57f3dd6e481dfe3c5be6`. Live product advertising configuration/name/address cells remain typed imports. The larger Main source/layout/runtime gates remain open; this is not a complete BLE stack or firmware image.

### IAR BLE format and version-scan wrappers, 2026-10-11

- Added `display_ble_format_scan_wrappers.c`: complete native `sprintf` shell `0x4b4728` and `sscanf` shell `0x475fc0`, with callback behavior at `0x4397c6` and `0x439bc6`, the ARM variadic register/stack cursor, null terminator, return values, and direct calls to the selected Main formatter candidate and genuine scan-engine lower `0x4d1638`. The scanner engine is **not** reduced by this shell; `audio_ble_scan_core` remains an unresolved body contract. The Main formatter engine itself still has its separately documented grammar/floating qualification limits.
- `verify_ble_format_scan_wrappers.py` compares actual ARM-compiled C/native callback invocation ABI, three variadic words, a two-character format result, and scan return over bounded cases (PASS). It cuts the 0x481836 formatter and 0x4d1638 scanner engines at their call boundary and does not claim complete formatting/scanning equivalence.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-formatter-wrappers-stage/receipt.json`: Main relocatable link PASS, **1648 defined / 643 unresolved / zero duplicate strong symbols**, SHA-256 `b0a34586ee0db96f53ebc5e448fbf7dfb04a5f0745d064e99752fb0067d17338`. Product advertising RAM is still live external state. Full firmware source/build/hardware completion remains false.

### Bounded BLE version scanner path, 2026-10-11

- Added `display_ble_scan_core_version_candidate.c`: executable source for the connected IAR scanner `0x4d1638` path with authenticated `"%d.%d.%d"` format, signed decimal fields, literal separators, callback read/unget, three destination cursors, and partial/failed return counts. It dispatches other formats, nonzero mode, or null destinations to the genuine unresolved `audio_ble_scan_core_full` contract. This is explicitly a **domain-limited candidate**, not full scanner engine recovery; integer overflow and locale-dependent behavior outside the compared domain remain unqualified.
- `verify_ble_scan_core_version.py` compares actual ARM-compiled C/native scan results and output memory on five complete, truncated, invalid, and signed fixtures (PASS). The native harness cuts only uninitialized locale character classification and selected integer conversion with the corresponding ordinary decimal semantics; it does not establish live product locale state.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-scan-version-stage/receipt.json`: Main relocatable link PASS, **1649 defined / 643 unresolved / zero duplicate strong symbols**, SHA-256 `ce13bd869dae6a309ba0e6943a9129b11d8f000baf67fc436f1af5c83f596e73`. The total unresolved count is unchanged because the prior `audio_ble_scan_core` import is replaced by `audio_ble_scan_core_full`; this is a connected path reduction, not whole scanner closure.

### BLE communication event dispatcher, 2026-10-11

- Added `display_ble_comm_handler.c`: full native `_bleCommHandler` `0x4b7d32` event classification, ordered DM dispatch, master/slave routing, blocked advertising-stop branch, three native diagnostic branches, one message-release call, and two post-dispatch forwards. Its seven authenticated source strings are C literals; handler children remain actual typed imports. During verification, an apparent duplicate message-release call in decompiled pseudocode was corrected against executed stock control flow.
- `verify_ble_comm_handler.py` compares actual ARM-compiled C/native child-call sequences for six null, DM, master, slave, block, and log-enabled fixtures (PASS). External handlers and logging are controlled cuts, so their internal behavior is outside this proof.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-comm-handler-stage/receipt.json`: Main relocatable link PASS, **1650 defined / 652 unresolved / zero duplicate strong symbols**, SHA-256 `2aad97a548455a7197f0862597be99087489da36f75cc55bc5af03a709dc40da`. The nine additional unresolved symbols are newly exposed real dispatch/forward/release bodies. Whole BLE stack and firmware source completion remain false.

### BLE profile forward chains and entry wrappers, 2026-10-11

- Added `display_ble_comm_forwards.c`: native `0x46ef74` seven-profile forwarding chain with nonnull advertisement preprocess, and `0x4a19c0` master chain with nonnull preprocess. `verify_ble_comm_forwards.py` compares actual ARM-compiled C/native child order and passthrough return for null and nonnull messages on both chains (PASS). The ten actual profile/preprocess children remain typed code contracts.
- Added `display_ble_profile_message_wrappers.c`: native 14-byte OTA/EUS/ESS/EFS/NUS entry bodies `0x4bdd70`, `0x4bdfe6`, `0x4be2e8`, `0x4be572`, `0x4be848`, each conditionally forwarding a nonnull message to its genuine profile body. `verify_ble_profile_message_wrappers.py` compares actual ARM-compiled C/native child calls and argument for all five null and nonnull cases (PASS). Native wrappers return the caller's preserved `r7` value, which is outside the standard C return ABI; selected callers ignore that value, so the C interfaces are void and full arbitrary-caller ABI equivalence is not claimed.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-profile-message-stage/receipt.json`: Main relocatable link PASS, **1657 defined / 660 unresolved / zero duplicate strong symbols**, SHA-256 `6be9396a371ce60078333d4e28ed0e5997824593a6b20030e7fa20641a575694`. Profile body and preprocess children, product runtime data, full scanner grammar, complete source layout, and hardware operation remain open.

### BLE profile event bodies, 2026-10-11

- Added `display_ble_profile_message_bodies.c`: full native OTA `0x4bdc0c`, EUS `0x4bded6`, ESS `0x4be24e`, EFS `0x4be420`, and NUS `0x4be76c` message-body branch graphs. They update the existing typed four-byte product state cells, handle connection role and service enable, call their genuine update children, and forward authenticated write event codes and attribute handles. OTA additionally handles reset, disconnect and delayed connection callback. The callback literal at `0x4bde24` resolves to the genuine function `0x4bdb38`, not a product data cell.
- `verify_ble_profile_message_bodies.py` compares actual ARM-compiled C/native state bytes and meaningful child-call arguments for 32 service enable, update, disconnect, ignored, write and OTA special cases (PASS). Child internals and live BLE state initialization remain outside the cut oracle.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-profile-bodies-stage/receipt.json`: Main relocatable link PASS, **1662 defined / 665 unresolved / zero duplicate strong symbols**, SHA-256 `717367f801b9228b09d55e27cce76a2833a0d1e472caaf38233eb0c3590d003e`. The five net new imports are lower profile update/write/event bodies; all product RAM remains typed external runtime state. Whole image completion is false.

### BLE profile CCC update children, 2026-10-11

- Added `display_ble_profile_ccc_updates.c`: native OTA `0x4bdb90`, EUS `0x4bde4c`, ESS `0x4be228`, EFS `0x4be3a4`, and NUS `0x4be6f0` CCC state callbacks. Each checks its authenticated profile index, records the connection and enabled flag only for CCC value 1, and clears them otherwise. OTA/EUS/EFS/NUS native diagnostic strings and log call gates are source literals; ESS has no log calls. The message-body callers now pass their actual message pointer to these callbacks, correcting a source call ABI error exposed by inspection.
- `verify_ble_profile_ccc_updates.py` compares actual ARM-compiled C/native state bytes and diagnostic-call gates on 25 matching, mismatched, enabled, disabled and logging fixtures (PASS). The prior connected `verify_ble_profile_message_bodies.py` was strengthened to check callback `r0` and still passes all 32 cases. Log argument contents beyond gate/order and live product state initialization are not established by these cuts.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-profile-ccc-stage/receipt.json`: Main relocatable link PASS, **1667 defined / 660 unresolved / zero duplicate strong symbols**, SHA-256 `503562a2d503bb65f516ef4927273679e157d08ecb91d624ef095e52635cc91f`. Product state cells, five profile write/event lower bodies, and wider Main scanner/application source remain open.

### OTA and ATT profile event children, 2026-10-11

- Added `display_ble_profile_event_children.c`: native OTA connection route `0x4bb04a` with `(3, connection, 0x13)` child call; Cordio ATT profile write wrapper `0x533ed8` with authenticated seven-argument layout and `0x1b` opcode; and device-control reset `0x4d3534` writing authenticated MMIO `0x40000008 <- 0xd4` or `0x40000004 <- 0x1b` followed by the native halt loop, with other selector values returning 6. This is decoded hardware behavior, not a fabricated trap stub.
- `verify_ble_profile_event_children.py` compares actual ARM-compiled C/native route arguments, ATT write arguments and three reset-selector outcomes (PASS). The reset oracle observes MMIO writes and bounded loop entry; it does not authorize or demonstrate physical reset behavior.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-profile-event-children-stage/receipt.json`: Main relocatable link PASS, **1670 defined / 659 unresolved / zero duplicate strong symbols**, SHA-256 `4a0f1d06b539562070c8737be7a5567b07bdb62ec06252ec3cff408ef6b9d9d3`. The Cordio ATT write and OTA routing lower bodies remain genuine imports alongside product runtime state and full scanner grammar.

### OTA delayed reset callback, 2026-10-11

- Added `display_ble_ota_delayed_callback.c`: native callback at `0x4bdb38` addressed by the authenticated `0x4bde24` ROM literal, with both diagnostic gates, 12-byte WSF allocation, event `0xa0`, current connection and handler from the external four-byte OTA state, and conditional send. `verify_ble_ota_delayed_callback.py` compares actual ARM-compiled C/native allocation failure, successful send and two enabled log paths, including message bytes and destination handler (PASS).
- Dedicated `g2/build/c-firmware/20261011/audio-ble-ota-delayed-stage/receipt.json`: Main relocatable link PASS, **1671 defined / 658 unresolved / zero duplicate strong symbols**, SHA-256 `5f483bfc242d25121a424beba38533ce692fe09042bfa1e97b2b171626a3a9bc`. OTA callback path still depends on product runtime state, WSF children and the wider incomplete Main image.

### Cordio OTA route message, 2026-10-11

- Added `display_ble_ota_route_message.c`: native `0x4b6c82` 36-byte WSF allocation, authenticated message bytes `(connection, 0x19, subtype, subtype, channel)` and send to the handler at offset 12 of live product struct `0x20073b78`. `verify_ble_ota_route_message.py` compares actual ARM-compiled C/native allocation failure and success, handler value and first six message bytes (PASS). The oracle exposed and corrected an initial mistaken pointer-cell interpretation of `0x20073b78`; native reads the struct directly.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-ota-route-stage/receipt.json`: Main relocatable link PASS, **1672 defined / 658 unresolved / zero duplicate strong symbols**, SHA-256 `8435e304c2453b7215c2298b945789f92872f62cb13d7386154528c1ecce27d2`. The newly exposed product struct replaces the genuine code import in the count; its initializer/runtime ownership remains unresolved. Whole Main remains incomplete.

### Cordio ATT write scheduler, 2026-10-11

- Added `display_ble_att_write_request.c`: full native `0x533c6c` lock/lookup/unlock sequence; registration maximum and busy-bit test; connection validation; `0x71`/`0x77` error responses; 12-byte WSF message and optional payload allocation; ATT header/opcode/attribute layout; copy, send and ownership-aware failure free. The wrapper at `0x533ed8` now calls this C body. Existing selected WSF lock, allocation, send, memcpy and buffer-free providers are reused. Registration lookup, connection validation, error send and live ATT runtime struct at `0x200610ac` remain true imports.
- `verify_ble_att_write_request.py` compares actual ARM-compiled C/native calls, return values and generated message/buffer bytes for eight missing registration, zero maximum, busy, invalid connection, short maximum, message allocation failure, buffer allocation failure and successful queue cases (PASS). The compared connected wrapper uses the no-ownership mode; owned-input and deeper registration/connection internals remain unqualified.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-att-write-stage/receipt.json`: Main relocatable link PASS, **1673 defined / 661 unresolved / zero duplicate strong symbols**, SHA-256 `761d12407e3d83b38173e4ca19ef65404aa1bf2b55b21932e1f3f88b13e598a1`. Three net newly exposed imports are genuine registration/connection/error code and product runtime data, so whole-image source completion is still false.

### Cordio ATT error callback, 2026-10-11

- Added `display_ble_att_error.c`: native `0x533934` error wrapper and `0x4b5074` runtime callback packet. It checks the live callback slot at ATT struct `0x200610ac+0x58`, then emits the native 16-byte packet with connection, event `0x12`, reason, zero field, attribute and extra field. Native leaves packet bytes 4..7 and 13 as stack scratch, so those bytes are not initialized or claimed equal in C.
- `verify_ble_att_error.py` compares actual ARM-compiled C/native no-callback and callback paths, checking all eleven defined packet bytes (PASS). It does not assert equality for the five native uninitialized bytes or external callback behavior.
- Dedicated `g2/build/c-firmware/20261011/audio-ble-att-error-stage/receipt.json`: Main relocatable link PASS, **1675 defined / 660 unresolved / zero duplicate strong symbols**, SHA-256 `2a40acb36288483f4834780fd2d9bca6b1e61a6a62e3f756ba23de159dce04ae`. ATT registration/connection handlers and runtime struct still remain, as do full scanner grammar and whole-image placement.
### ATT registration and connection record paths (2026-10-11)

`display_ble_att_registration_valid.c` reduces native 0x4b6ec6 and the valid-connection record arithmetic of 0x534f14. `display_ble_att_connection_valid.c` reduces the nonzero-connection branch of 0x52c928. Authenticated RAM bases are 0x200712a4, 0x2006e5f0, and 0x20073e04. These are live data contracts, not fabricated initializers. The native zero/invalid registration assertion trees remain explicit `audio_ble_att_registration_invalid` and `audio_ble_att_zero_connection_assert` code contracts; neither parent body is fully complete.

`verify_ble_att_records.py` passes 22 actual ARM compiled-C/native cases covering record-active values, three registration-record offsets, and connection state/attribute combinations. The dedicated target receipt `g2/build/c-firmware/20261011/audio-ble-att-records-stage/receipt.json` passes relocatable link with 1678 defined, 663 unresolved, zero duplicate strong symbols, SHA256 `a16650c823376e02d1942c059bc031b4d7e344bd33b3eb30d8e93df5ae5fbbf4`. Whole Main source, product RAM initialization, full scanner grammar, placement, and hardware behavior remain open.
### ATT transport callbacks (2026-10-11)

`display_ble_att_callbacks.c` implements complete native Cordio ATT L2C data callback 0x4b4de0, L2C control callback 0x4b4e08, and DM connection callback 0x4b4e50 with the authenticated runtime table at 0x200610ac. It preserves callback order, connection record mutation, and WSF buffer release. `verify_ble_att_callbacks.py` passes six actual ARM compiled-C/native bounded cases (both data routes, control enable/disable, DM open/close); this does not exercise all callback implementations or hardware state.

The selected aggregate `g2/build/c-firmware/20261011/audio-ble-att-callbacks-bound-stage/receipt.json` passes relocatable link: 1681 defined, 661 unresolved, zero duplicate strong symbols, SHA256 `24911a7838f03387f9bb5274c10cc096e564db5f8ddb35de5dd03fed5c6ca30e`. The remaining direct ATT code child is `audio_ble_att_ccb_by_conn_id`; product callback tables and live runtime data remain explicit external contracts.
### ATT CCB lookup (2026-10-11)

`display_ble_att_ccb_valid.c` implements native 0x4b4eee for nonzero connection IDs against live ATT runtime 0x200610ac, with 0x14-byte records. The zero-ID diagnostic assertion tree remains `audio_ble_att_ccb_zero_assert`, a genuine unimplemented code contract. `verify_ble_att_ccb_valid.py` passes four actual ARM compiled-C/native offsets. Selected aggregate `g2/build/c-firmware/20261011/audio-ble-att-ccb-stage/receipt.json`: link PASS, 1682 defined, 661 unresolved, zero duplicates, SHA256 `ff3ddd3eec127549fa7c9ec12ab01b19ea2b7e52142006e1bffc0c2df8bf461d`. Full ATT invalid/zero assertion trees and product live RAM ownership remain open.
### ATT failure trees and WSF diagnostics (2026-10-11)

`display_ble_att_assert_paths.c` now supplies the invalid/zero branches of native ATT lookup 0x4b4eee, 0x534f14, and 0x52c928. The source reproduces authenticated Cordio diagnostic literals, four short-circuit policy checks, selected extended logger calls, and trace choice; its policy byte remains a live product cell at 0x2007502f. `verify_ble_att_assert_paths.py` passes eight actual ARM compiled-C/native terminal-effect cases (four errors, policy 0/1), including corrected complete message strings. This cut compares trace/log selection and return, not arbitrary formatter bytes or live UART effects.

`display_ble_wsf_trace.c` implements native 0x52a63c through selected formatter/print providers, newline, and assert threshold. `verify_ble_wsf_trace.py` passes normal and overflow print cases. `display_ble_wsf_assert.c` implements native 0x569a44 logging/compressed logging and nonreturning reset/idle behavior; its optional callback pointer is a typed live cell at 0x2007456c. `verify_ble_wsf_assert.py` passes five nonnull-file log flag cases plus null-file callback and reset call cuts. Physical reset behavior has not been run against hardware.

The selected aggregate `g2/build/c-firmware/20261011/audio-ble-att-failure-full-stage/receipt.json` passes relocatable link with 1687 defined, 660 unresolved, zero duplicate strong symbols, SHA256 `a82f24bb33af93de0f47f7ceca4677bbc66b0e1b09c8c4960a1f0babcece1909`. The ATT code tree covered in this chunk has no remaining artificial failure-path declaration; product ATT tables/runtime, WSF callback/policy cells, full scanner grammar, and the wider Main image remain explicit open contracts.
### OTA cancel and status sync (2026-10-11)

`display_ble_ota_cancel_sync.c` reduces complete native OTA cancel 0x448784 and connected RPC status sync 0x444e90. Cancel zeroes the 0x60-byte live export state at 0x20072730, restores authenticated 0x2034bc10 at offset 0x34, then calls status sync. Sync reproduces extended/compact log selection, two separate reads of live status 0x20075024, the eight-byte authenticated packet template, and selected status send 0x464d1c when live gate 0x20074ff3 permits it. Product RAM cells remain external, with no fabricated initial values.

`verify_ble_ota_cancel_sync.py` passes six actual ARM compiled-C/native cases: enabled/disabled sync, three status values, cancel memory and packet side effects, and log/compact paths. The dedicated selected link `g2/build/c-firmware/20261011/audio-ble-ota-cancel-sync-stage/receipt.json` passes with 1689 defined, 661 unresolved, zero duplicate strong symbols, SHA256 `4bb604d649a78137a11f135ad072fcd5c8741c3e27fc1ceb483becf2632225cc`. Full scan grammar remains unreduced; whole Main still has substantial code/data/runtime contracts.
### Cordio advertising and ATT CSF registration (2026-10-11)

`display_ble_dm_adv_lower.c` completes native `dmAdvInit` 0x4b30e4 and `dmAdvCbInit` 0x4b3098. It applies two sets of interval, type, enabled, and handler state writes using live control block 0x20073394 and selected live handler state 0x20073b78. `verify_ble_dm_adv_lower.py` passes six actual ARM compiled-C/native cases, including both individual callback rows and whole initialization.

`display_ble_atts_csf_register.c` completes native `AttsCsfRegister` 0x52d4e0 by installing the callback at live table 0x20073e04+8; `verify_ble_atts_csf_register.py` passes null and nonnull callback pointer cases. `display_ble_atts_csf_callback.c` completes native callback 0x53482c, row lookup 0x4bb07c, and one-byte copy 0x47b418 against live row table 0x200717b0; `verify_ble_atts_csf_callback.py` passes five null/success/child cases. `display_ble_att_empty_handler.c` is the authenticated native `attEmptyHandler` 0x4b4ee6; both original and compiled object are a single `bx lr` instruction, so its empty effect is source-backed.

The final selected link `g2/build/c-firmware/20261011/audio-ble-dm-adv-atts-full-stage/receipt.json` passes with 1696 defined, 659 unresolved, zero duplicate strong symbols, SHA256 `e72097e7eb94099f24bf47ca2810963978e8439f7ad11c48b223d70ca1587bb1`. Remaining local ATT cells include live row data and table declarations; no product initializer or hardware effect is inferred. Full Main and scanner grammar remain incomplete.
### HCI core dispatcher and timeout path (2026-10-11)

`display_ble_hci_core_handler.c` implements native HCI callback registration 0x5367f0, callback wrapper 0x536814, full `HciCoreHandler` 0x530cb2, and WSF dequeue/free wrappers 0x4bf9ec/0x4bf9b0. It uses the selected WSF queue and buffer providers and typed live HCI state 0x20073870. `verify_ble_hci_core_handler.py` passes ten actual ARM compiled-C/native dispatcher cases at the genuine event, reset, ACL, timeout, message dequeue/free and function-pointer callback cuts. `verify_ble_hci_helpers.py` passes callback registration, message handler-byte extraction, free-hidden-header mapping and wrapper argument truncation/forwarding.

`display_ble_hci_timeout_reset.c` implements native `hciCmdTimeout` 0x52aee6 and connected `DmDevReset` 0x4b3026. The latter clears live DM state 0x20073b78+0x10, allocates a four-byte WSF message, sets event 0x38 and sends it to the selected handler. `verify_ble_hci_timeout_reset.py` passes four actual ARM compiled-C/native allocation, state and radio-call-order cases. Radio boot 0x4b48a6 and shutdown 0x4b49ce remain genuine lower code imports; event processing, ACL reassembly, and reset sequence are likewise still full native bodies to reduce.

The selected link `g2/build/c-firmware/20261011/audio-ble-hci-timeout-stage/receipt.json` passes with 1703 defined, 662 unresolved, zero duplicate strong symbols, SHA256 `3d8e538e6f0560b0e2c7c31c1878b6f13175936590b34babd34d4ae527c83916`. This is a source graph expansion, not whole-image closure; live HCI state, radio timing, and physical BLE behavior remain unqualified.

Read-only cross-component audit: the Touch report's current selected reset attribution is 534/964 bytes, with 426-byte LP history allocation extent and an unowned four-byte value at 0x20000828 still gated by generated configuration or symbol-size evidence. Its 54 selected C units compile, but this data ownership does not prove linker placement or hardware operation. The CASE older archive receipt has three direct command/formatter imports; experimental public entry and command routing candidates already exist, and current startup sources contain the nine transport descendants named in an older report. Check the current CASE selected graph before assigning those historic names anew.

### HCI radio shutdown and connected children (2026-10-11)

- Added `display_ble_hci_radio_shutdown.c` for complete native 0x4b49ce: WSF timer stop, pin and radio shutdown calls, two live flag clears, and context reset. `verify_ble_hci_radio_shutdown.py` compared actual ARM compiled C against stock across three flag cases, PASS 3. The timer, flags, and context pointer are live product RAM contracts.
- Added `display_ble_hci_radio_children.c` for native 0x52dd6a/0x52dd7c/0x52df12/0x52eece. The pin write uses the selected GPIO HAL, pin function the selected source provider; the mode word remains typed live product data. `verify_ble_hci_radio_children.py` compared compiled C and native: context reset PASS 5, pin disable PASS 2 including a child-mutated pin result. Switch and pins are statically crosswalked but their child MMIO effects are not yet runtime compared.
- Dedicated `audio-ble-hci-radio-disable-stage/receipt.json`: Main candidate compilation and relocatable link PASS, 1708 definitions, 671 unresolved, zero duplicate strong definitions, candidate SHA-256 `bfac41a7ac82f576866ae617a427ea7c7d14bf780c9e00e41359dd36e4617564`. Full image source, placement, product initialization, and hardware runtime remain open.
- Direct newly exposed code contracts include `audio_ble_hci_radio_pin_mask_4810b0`, `audio_ble_hci_radio_mask_4c2e30`, stack stop 0x55c430, option 0x55c7e8, and reset 0x55c286. Larger HCI event 0x56b390, reset sequence 0x569b56, ACL 0x52a962, and boot 0x4b48a6 remain unreduced. The 671 unresolved symbols include product RAM and other whole Main contracts, so their count is not an omitted-body count.

### HCI ACL reassembly (2026-10-11)

- Added `display_ble_hci_acl_reassemble.c` for native hciCoreAclReassembly 0x52a962, including start/continuation fragments, allocation, packet copy, length/remaining updates, complete-packet ownership transfer, and invalid-fragment frees. Added `display_ble_hci_acl_children.c` for hciCoreConnByHandle 0x52a704 (three live rows at 0x20071478, 0x1c stride) and WsfMsgDataAlloc 0x4bf990 using selected WsfMsgAlloc.
- `verify_ble_hci_acl.py` executes actual ARM compiled C and native stock in seven bounded cases: unknown handle, complete start, zero-length, other packet kind, partial allocation/copy, continuation completion, and short continuation free. PASS 7, comparing return pointer, free/alloc calls, controller record bytes, and allocation content. Other malformed/overflow combinations and hardware behavior remain outside this oracle.
- Dedicated `audio-ble-hci-acl-children-stage/receipt.json`: Main candidate compile/link PASS, 1711 definitions, 671 unresolved, zero duplicate strong definitions, SHA-256 `8d60863911f53bda0dc05018e7c124d07feb2bcd7d1bea3873a952cfb698ea42`. Whole-image source/equality remains false; controller state is live product RAM.

### HCI reset opcode sequence (2026-10-11)

- Added `display_ble_hci_reset_sequence.c` for native hciCoreResetSequence 0x569b56. It implements the complete retained command-complete opcode switch, state copies, typed live HCI controller/stack cells, vendor command progression, random retry and callback, and optional controller callback. Native R3 is an architectural input on the final 0x2018 callback path; a source-defined naked branch preserves it from the one-argument caller to the four-register C body.
- `verify_ble_hci_reset_sequence.py` compared actual ARM compiled C with native stock for seven controlled cases: non-reset event, NVDS command, supported buffer record, random retry, final random callback, 0x2024 null option callback, and 0x2024 callback. PASS 7, comparing return register, selected child/callback calls, live state fields and random count. Remaining opcodes are statically crosswalked from the retained full decompilation but lack direct runtime fixtures. Caller R3 provenance after the event processor has no higher-level C meaning beyond the preserved register contract.
- Dedicated `audio-ble-hci-reset-sequence-qualified-stage/receipt.json`: Main candidate compile/link PASS, 1713 definitions, 690 unresolved, zero duplicate strong definitions, SHA-256 `ef1df15735a4f8d5a7d6e437289d2ee721400decbd78e9bb55446a04bce72efc`. The higher import count exposes real HCI command providers and product RAM/ROM; it is not evidence of source completion.

### HCI radio boot (2026-10-11)

- Added `display_ble_hci_radio_boot.c` for native HciDrvRadioBoot 0x4b48a6, including acquire/detect/log/delay, conditional revision recovery, scheduler setup, optional identifier loading, radio register and mux startup. Every board configuration pointer, live state cell and ROM log string has an explicit typed external owner rather than a fabricated value. Corrected the shutdown parent’s live active/pending cells to 32-bit writes after checking native STR instructions; the updated four-byte shutdown oracle PASS 3.
- `verify_ble_hci_radio_boot.py` compared actual ARM compiled C with native stock across five connected cases: ordinary boot, detector retry, matching revision, recovery, and identifier copy. PASS 5 comparing return, child call order, retry and command/active/pending cells, and identifier bytes. Hardware children are cut at their actual native addresses, so this verifies boot composition rather than the radio hardware itself.
- Dedicated `audio-ble-hci-radio-boot-stage/receipt.json`: Main candidate compile/link PASS, 1714 definitions, 717 unresolved, zero duplicate strong definitions, SHA-256 `d8c8ce1149697c50d61580f74822ec9e39455ee2df85b9976f3914fd83cf91bf`. Direct radio child functions remain genuine code contracts; live hardware/product data is unresolved.

### HCI event processor (2026-10-11)

- Added `display_ble_hci_event_process.c` for the retained full native hciEvtProcessMsg 0x56b390 opcode/subevent tree: 16-bit event counters, HCI command events, LE reports, connection/CIS lifecycle, table-driven allocation/decode/callback/free, and vendor diagnostic branches. The event size and decoder tables remain typed ROM data contracts at 0x6e3720 and 0x6c910c. A source-defined naked branch preserves native R2/R3 call residue for the body’s 64-bit return. Diagnostic logging message/file pointers remain typed ROM contracts.
- `verify_ble_hci_event_process.py` executes actual ARM C and stock native in nine bounded cases: unknown event, command complete/status, completed packets, idle, LE connection, disconnection, vendor trace, and enabled vendor log. PASS 9 comparing return registers (relocation-normalized vendor pointer), child call order, 16-bit counters, and event buffer header. The native disassembly exposed 16-bit counter writes; the source and oracle were corrected before the final target build. Remaining HCI subevent decoders, source-owned ROM table data, callback behavior, and all hardware effects are not covered by this oracle.
- Dedicated `audio-ble-hci-event-qualified-stage/receipt.json`: Main candidate compile/link PASS, 1716 definitions, 746 unresolved, zero duplicate strong definitions, SHA-256 `0ad06cd758bee70fb9f16702344b167be611b37f0d4d8040f341e0a53f4af25f`. The HCI parent event/reset/ACL/boot/shutdown bodies are now source-defined; their children and product data keep the overall component and image incomplete.

### HCI event command children (2026-10-11)

- Added `display_ble_hci_event_command_children.c` for native hciEvtProcessCmdStatus 0x56b150 and hciCoreNumCmplPkts 0x530c08. The credit path uses selected hciCoreConnByHandle, 0x1c-byte live records, 8-bit wraparound subtraction, threshold callback and hciCoreTxReady. `verify_ble_hci_event_command_children.py` actual ARM C/native PASS 5 across status success/failure and credit notification/non-notification/unknown-handle cases.
- Added `display_ble_hci_cmd_complete.c` for native hciEvtProcessCmdCmpl 0x56b182, including its complete retained opcode-to-event mapping, special random callback selection, vendor OGF fallback, allocator/decoder/callback/free sequence and command-receive completion. The source-defined naked entry preserves native R3 residue used by the native return. `verify_ble_hci_cmd_complete.py` actual ARM C/native PASS 4 for unknown, mapped, random and vendor opcodes, comparing allocation size, callback route, event header, free and receive-complete count. Remaining opcodes are statically crosswalked; ROM size/decoder table data remains an explicit contract.
- Dedicated `audio-ble-hci-cmd-complete-stage/receipt.json`: Main target candidate compile/link PASS, 1720 definitions, 746 unresolved, zero duplicate strong definitions, SHA-256 `05fe7210f7155fb4f83b746e8def625082eceaa655da1d20e566daea6525f073`. The HCI graph remains incomplete through genuine decoder/radio children, product data tables and image placement/runtime gates.

### HCI connection and command lower children (2026-10-11)

- Added `display_ble_hci_conn_lifecycle.c` for native hciCoreConnAlloc/Free 0x52a67c/0x52a6b0 and open/close wrappers 0x52a758/0x52a762. The three 0x1c-byte live records retain sentinel 0xffff, queue/fragment release, credit return and callback order. `verify_ble_hci_conn_lifecycle.py` actual ARM C/native PASS 7: allocate, full table, free with/without attached messages, absent handle, open and close.
- Added `display_ble_hci_cmd_lower.c` for native hciEvtCmdStatusFailure 0x56b100 and hciCmdRecvCmpl 0x52aef8. It composes selected WSF buffer/timer sources with the genuine HCI send child, preserving a special 0x2026/0x12 failure event and timer/state/send sequence. `verify_ble_hci_cmd_lower.py` actual ARM C/native PASS 5 across nonmatch, allocation failure/success and command completion.
- Dedicated `audio-ble-hci-child-lifecycle-stage/receipt.json`: Main target candidate compile/link PASS, 1726 definitions, 743 unresolved, zero duplicate strong definitions, SHA-256 `7ba8c130db10021e42d7b7f3ef935b92d681cab5bbf52a885497049a89b966be`. Remaining HCI genuine code includes hciCoreTxReady/hciCmdSend, LE report decoders and radio HAL children; ROM tables and product runtime cells remain unresolved.

### HCI command queue send (2026-10-11)

- Added `display_ble_hci_cmd_send.c` for native hciCmdSend 0x52ae5e and WsfMsgPeek 0x4bfa00. It composes selected WSF enqueue/dequeue/free with timer start and transport command send contracts, preserves queue/message ownership and the saved R2 scratch byte overwritten by WsfMsgPeek. `verify_ble_hci_cmd_send.py` actual ARM C/native PASS 5: not ready, empty queue, transport failure, successful dequeue/free, and enqueue. The first oracle exposed the saved R2 low-byte effect, which was corrected before the final target build.
- Dedicated `audio-ble-hci-cmd-send-stage/receipt.json`: Main candidate compile/link PASS, 1729 definitions, 744 unresolved, zero duplicate strong definitions, SHA-256 `3d1056523bf00a33cb1569e6ed8fdb6e9c5f4093719fd9f18316beca51235dc6`. Native transport send, timer start and remaining radio/LE children are still genuine code contracts.

### HCI command transport children (2026-10-11)

- Added `display_ble_hci_cmd_transport.c` for native WsfTimerStartSec 0x52a4b8 and hciTrSendCmd 0x530166. It retains 32-bit wrapping seconds-to-ticks conversion, the command packet length at byte 2 plus three header bytes, and exact hciDrvWrite return-length comparison. `verify_ble_hci_cmd_transport.py` actual ARM C/native PASS 6, including timer multiplication wrap and complete versus short writes.
- Dedicated `audio-ble-hci-cmd-transport-stage/receipt.json`: Main candidate compile/link PASS, 1731 definitions, 744 unresolved, zero duplicate strong definitions, SHA-256 `a0813ab5bc460dd27c4a7f37263cec9e97c4e9cfe61e48d648fae98355e0ef2a`. The timer insert and radio driver write implementations remain genuine direct children, together with remaining event decoder and product data contracts.

### HCI timer insertion and driver write (2026-10-11)

- Added `display_ble_wsf_timer_insert.c` for native wsfTimerInsert 0x52a424, WsfQueueInsert 0x538c8c, and WsfQueuePush 0x538c6e. It composes selected task lock/timer remove/queue enqueue and retains sorted insertion with equal ticks placed after prior equal nodes. `verify_ble_wsf_timer_insert.py` actual ARM C/native PASS 5 for empty/front/middle/tail/equal sorted queues; active-timer removal is present but not bounded in this oracle.
- Added `display_ble_hci_driver_write.c` for native hciDrvWrite 0x4b4a02, including full-ring and oversize authenticated error paths, framed packet length/type/payload into the live ring, ring commit and WSF event. `verify_ble_hci_driver_write.py` actual ARM C/native PASS 5 for zero, short, maximum accepted 0x102, oversize 0x103, and full queue. It compares framed bytes, return, and genuine child call order. The test initially hit an instruction-count bound at 0x102; increasing the emulator bound resolved it without a source change.
- Dedicated `audio-ble-hci-timer-driver-stage/receipt.json`: Main target candidate compile/link PASS, 1735 definitions, 745 unresolved, zero duplicate strong definitions, SHA-256 `c37020de75828b5b69734e55c359c894da17f83ac577a5de97a2bbb34286e954`. Direct ring commit, WSF event, error handler and TxReady/ACL descendants remain, as do product RAM/ROM and whole-image gates.

### HCI ACL TxReady and fragment transport (2026-10-11)

- Added `display_ble_hci_tx_ready.c` for complete native hciCoreTxReady 0x52a79e. It saturates controller credits, drains continuation fragments, peeks/dequeues ACL queue messages, handles absent connection ownership, and starts/completes sends. The ARM entry preserves native R2 scratch. `verify_ble_hci_tx_ready.py` compares actual compiled C against stock for five controlled credit/queue cases, PASS 5.
- Added `display_ble_hci_acl_fragments.c` for native hciCoreTxAclStart/Continue/Complete 0x52a850/0x52a8b0/0x52a936. It retains 0x1c-byte live connection record fields, packet length/header rewrite, segmented pointer/remaining updates, failure rollback and exact WSF free effects. `verify_ble_hci_acl_fragments.py` compares actual compiled C and stock across eight start/continue/complete cases, PASS 8. Other malformed packet and allocation states remain outside the bounded oracle.
- Added `display_ble_hci_acl_transport.c` for native hciCoreNextConnFragment 0x52a72e, hciCoreSendAclData 0x52a76c, hciTrSendAclData 0x53013c and HciGetBufSize 0x530d34. Native literal slots 0x52ae14 and 0x530d68 both resolve to live state 0x20071478. `verify_ble_hci_acl_transport.py` executes actual C and stock through the transport with the same driver cut, PASS 7 including send success/failure and third-record selection.
- Dedicated `audio-ble-hci-acl-transport-stage/receipt.json`: Main candidate compile/relocatable link PASS, 1744 defined, 744 unresolved, zero duplicate strong providers, SHA-256 `f0a7cd0dffe958b98360ab3158c60deb8607c8dcb28481c094945e6c8beaf39b`. Remaining direct HCI code includes ring commit, WSF event, radio HAL, LE decoders and error handler; unresolved product RAM, ROM tables, build placement and hardware runtime keep Main incomplete. The candidate fragment source has actual ARM/native bounded proof; broader HCI traffic and live-radio operation remain unverified.

### HCI LE reports and driver children (2026-10-11)

- Added `display_ble_hci_le_reports.c` for full retained native LE advertising, direct advertising, extended advertising and periodic advertising report decoders 0x56a398/0x56ab50/0x56a430/0x56a5be. It preserves allocation sizes, report iteration, 0x1f/0xe5/0xf7 length gates, event field layout, live callback at 0x20073878, and free timing. `verify_ble_hci_le_reports.py` executes actual ARM C and stock through the same allocator/callback cuts, PASS 4 for one valid report of each kind, comparing all delivered event bytes and calls. Multi-report and malformed/oversize cases remain outside this bounded oracle. Connection and connectionless IQ decoders remain genuine native code.
- Added `display_ble_hci_driver_children.c` for native ring commit 0x530084, WsfSetEvent 0x52b91e, error_check 0x4b47ae, and the architectural IRQ save/restore behavior. The ring retains element-size multiplication, capacity test, optional copy, unsigned modulo and count increment; WSF event writes the handler event bit and scheduler ready bit; error_check invokes the configured callback after storing the code. Error value/callback and WSF task state are typed live RAM contracts. `verify_ble_hci_driver_children.py` executes actual ARM C and native stock with equivalent critical-section cuts, PASS 6 for ring empty/data/full, WSF event, and zero/nonzero errors. The emulator cannot execute this target's PRIMASK instructions directly; their decoded MRS/CPSID/MSR behavior is represented by authenticated C inline assembly and cut only in that bounded effect oracle.
- Dedicated `audio-ble-hci-le-driver-qualified-stage/receipt.json`: Main target candidate compile/relocatable link PASS, 1758 defined, 737 unresolved, zero duplicate strong definitions, SHA-256 `df85d8e1f3bad67c1daaf5e704dfcb583ec0bb082f9c65aeba7edf216930b9ba`. The `audio_ble_hci_`/`audio_ble_wsf_` namespace has 76 unresolved entries: these include genuine IQ/radio/command code, live product RAM, and ROM tables/strings; 737 is whole Main graph imports, not a code body count. Full Main source, placement, data ownership and hardware runtime remain incomplete.

### HCI CIS live handle table (2026-10-11)

- Added `display_ble_hci_cis.c` for native CIS allocate/free/lookup 0x52ad9c/0x52adc2/0x52adec and open/close wrappers 0x52ae24/0x52ae2e. Authenticated ROM slot 0x52ae20 points to six 16-bit live handles at 0x200714cc, within the already declared HCI controller state. Unused entries are 0xffff; wrappers preserve native R7 return behavior. `verify_ble_hci_cis.py` actual ARM C/native PASS 7 for first/free/full/lookup/open/close effects.
- Dedicated `audio-ble-hci-cis-stage/receipt.json`: Main compile/relocatable link PASS, 1763 defined, 734 unresolved, zero duplicate strong definitions, SHA-256 `a7c06a4d3143df00dc8627e2196d98b321106b0314cfe6cb4636358d976a5e26`. The live handle initializer and event/radio ROM data remain source/layout contracts, and full Main remains incomplete.

### HCI radio detect/revision/enable children (2026-10-11)

- Added `display_ble_hci_radio_simple.c` for complete native revision getter 0x52dee6, detector 0x52deee and enable 0x52dd58. Authenticated ROM slots 0x52ea24/0x52eaec point at live 0x20074224/0x20074228; detector compares against native constant 0x0301ff04 after its log. Enable passes an initialized 0x75 stack word to the genuine pin-mask child and returns the possibly modified word, as the native POP-to-R0 does. `verify_ble_hci_radio_simple.py` actual ARM C/native PASS 4 including a child mutation of that stack word.
- Dedicated `audio-ble-hci-radio-simple-stage/receipt.json`: Main compile/relocatable link PASS, 1766 defined, 734 unresolved, zero duplicate strong definitions, SHA-256 `754030a8b11331ff4f9f8a9779a16b9fdaba9531d4f78ccc83d809653b7ba3a2`. New detected word, revision word and ROM log string remain typed source/data ownership contracts; full Main incomplete.

### HCI radio scheduler and IRQ setup (2026-10-11)

- Added `display_ble_hci_radio_scheduler.c` for native ring scheduler initialization 0x53006c, conditional radio preparation 0x52f38c, NVIC priority setup 0x4b4786 and NVIC interrupt enable 0x4b4768. Authenticated literal slots point at architectural NVIC priority 0xe000e400, system handler priority 0xe000ed18, and interrupt set-enable 0xe000e100. Radio preparation retains the native R7 return and invokes its genuine mode and prepare children. `verify_ble_hci_radio_scheduler.py` actual ARM C/native PASS 7 covering ring fields, both preparation branches, positive/negative IRQ priority and interrupt-enable paths. The initial negative IRQ fixture omitted ABI sign extension; corrected fixture passes against both implementations.
- Dedicated `audio-ble-hci-radio-scheduler-stage/receipt.json`: Main compile/relocatable link PASS, 1771 defined, 732 unresolved, zero duplicate strong definitions, SHA-256 `15e5bf54caf638101c47c6621f69253828b6c984bdd3a679b07edb08c9777f90`. Two new radio mode/prepare child code contracts remain; full Main source and live hardware validation remain incomplete.

### HCI radio mode selector and watchdog wrapper (2026-10-11)

- Added `display_ble_hci_radio_mode.c` for native mode-state selector 0x50938e and watchdog-kick wrapper 0x5118e0. The three ROM literal pointers authenticate live adjacent mode cells at 0x20074368..6a; mode 1 selects +1, mode 2 selects +2, all other byte values select the base. The wrapper retains its genuine 0x5118e8 watchdog child and native R7 return. `verify_ble_hci_radio_mode.py` actual ARM C/native PASS 6 across selector values 0,1,2,3,256 and wrapper call.
- Dedicated `audio-ble-hci-radio-mode-stage/receipt.json`: Main compile/relocatable link PASS, 1773 defined, 732 unresolved, zero duplicate strong definitions, SHA-256 `2fa56e1ef3ae651fbadcdd3e93ce34571401083fc50ce52dfa49bbf7b24a5fee`. The watchdog child and live mode cells remain genuine contracts. Whole Main source and runtime remain incomplete.

### HCI radio GPIO interrupt mask body (2026-10-11)

- Added `display_ble_hci_radio_pin_mask.c` for complete native 0x4810b0: null/opcode/pin validation; single-pin set/clear with bank 0/1/2 and the native bank-3 edge case; seven-word mask set/clear; architectural critical save/restore. ROM literal pointers 0x481768..9c authenticate seven registers per bank at 0x40010530..590 and 0x400105a0..600, spaced 0x10 bytes. An initial contiguous-register interpretation failed the actual-native oracle and was corrected to the authenticated 0x10-byte stride. `verify_ble_hci_radio_pin_mask.py` actual ARM C/native PASS 9, comparing return and full MMIO region for all four operations and errors. PRIMASK instructions are cut in Unicorn as in the prior ring oracle; source inline assembly is decoded from native.
- Dedicated `audio-ble-hci-radio-pin-mask-stage/receipt.json`: Main compile/relocatable link PASS, 1774 defined, 731 unresolved, zero duplicate strong definitions, SHA-256 `ca147cb39c89be002bd8536bdf169b8880c47f43c57ff8e8b5d0f56eec3e93bb`. Radio acquire/watchdog and IQ decoder diagnostics remain genuine code; live product RAM and ROM data remain separate contracts. Full image remains incomplete.

### HCI radio resource acquisition parent (2026-10-11)

- Added `display_ble_hci_radio_acquire.c` for complete retained 0x52dd94 resource acquisition: busy/kind/config guards, power/platform preparation, 20-byte configuration copy with two caller words, four vendor stack stages, live 0x20073dc4 resource row initialization, output pointer ownership, context check/recover, revision logging and dispatch setup. Authenticated literal slots point to live resource row 0x20073dc4, product configuration 0x200001b4 and revision word 0x20074224; no values were invented. `verify_ble_hci_radio_acquire.py` compares actual compiled ARM C with stock across ten guarded/failure/success paths, PASS 10, including exact child order, configuration bytes, live row, output pointers and revision. Child hardware effects are cut at their authentic entry points; this is connected composition proof, not vendor stack or radio operation proof.
- Dedicated `audio-ble-hci-radio-acquire-stage/receipt.json`: Main compile/relocatable link PASS, 1775 defined, 746 unresolved, zero duplicate strong definitions, SHA-256 `ba801e6ded39ebb89eada5a83f233a6b643dccee8cc2ced34265e4b2bc7a5499`. The import increase exposes fifteen genuine vendor stack/context/log/data contracts instead of claiming them complete. Full image remains incomplete.

### HCI radio platform/context/dispatch children (2026-10-11)

- Added `display_ble_hci_radio_context.c` for native platform pin setup 0x52dc40, context initialization 0x52e0a2 and dispatcher flag write 0x52edd8. Platform pin words 0x183/0x93 are authenticated source ROM data at 0x78ee40/44; the third pin word is live RAM 0x200001b0. It reuses selected native GPIO pin-function/write providers. Context initialization checks active/pending bytes, invokes stack stop/options in order, clears pending and returns native status; dispatcher flag is live 0x20074f51. `verify_ble_hci_radio_context.py` actual ARM C/native PASS 5, including all nine pin/GPIO call arguments and both context branches. The wrapper preserves native incoming R3 return on platform setup.
- Dedicated `audio-ble-hci-radio-context-stage/receipt.json`: Main compile/relocatable link PASS, 1779 defined, 745 unresolved, zero duplicate strong definitions, SHA-256 `ffde102c4b213ed625dbb6e57e953e148fa319b9b35bdc9404bb6f36446b6d99`. Live pin/dispatch cells and vendor stack stop/options remain genuine imports; full image incomplete.

### Vendor stack open/stop descendants (2026-10-11)

- Added `display_ble_hci_vendor_stack_open_stop.c` for complete native vendor stack row open 0x55c2bc and stop 0x55c430. ROM slot 0x55cc18 authenticates eight 0x8a8-byte live rows at 0x2003b558, while 0x55c548 authenticates 0x40050000 MMIO. Open checks index/output/allocated bit, writes authenticated 0x00123456 low identifier plus state bits and returns the row. Stop checks the native 25-bit row signature, active/pending fields, clears MMIO bits 0 and 4, calls the genuine stop HAL child and clears active state. `verify_ble_hci_vendor_stack_open_stop.py` actual ARM C/native PASS 9 over guards and state/MMIO transitions; the HAL child effect remains cut.
- Dedicated `audio-ble-vendor-stack-open-stop-stage/receipt.json`: Main compile/relocatable link PASS, 1781 defined, 745 unresolved, zero duplicate strong definitions, SHA-256 `631190959ca3a17c316c7a70c68bf3ec95ade9147db8952533155780df91d8d1`. Live vendor rows, stack stop HAL, option/config/start and other vendor graph bodies remain, so image source is incomplete.

### Vendor stack option transfer (2026-10-11)

- Added `display_ble_hci_vendor_stack_option.c` for complete retained native 0x55c7e8 row/MMIO option transfer. It validates the row signature and mode, stores or loads thirteen authenticated row-to-register fields, preserves bit-zero handling at 0x228, active-state wait, saved high return, IRQ off/on and completion status. The 0x55d248 ROM slot authenticates 0x40050000 vendor MMIO. `verify_ble_hci_vendor_stack_option.py` compares actual compiled ARM C with native stock over eleven guarded/store/load cases, PASS 11, including before-store, active wait/high return and after-load callbacks. The lower IRQ/wait callbacks are cut at native entries; their separate effects remain source contracts.
- Dedicated `audio-ble-vendor-stack-option-stage/receipt.json`: Main compile/relocatable link PASS, 1783 defined, 751 unresolved, zero duplicate strong definitions, SHA-256 `67365767ad2393696aa4bdc7eba11ee881008dacd7fa8efb7b83a01d9cdb27c2`. The higher import count exposes genuine lower IRQ/wait callbacks and live vendor rows, not source completion.

### Vendor stack configuration (2026-10-11)

- Added `display_ble_hci_vendor_stack_config.c` for complete retained native 0x55ca94 configuration: row signature/index/active validation, mode 0 divider path and bit/rate limits, three accepted mode 1 frequencies, authenticated MMIO values at 0x40050000, row timing/count/width calculations and trailing state reset. All constants were read from stock ROM slots 0x55d24c..274; the complex divider 0x55bf64 remains a genuine imported C body. `verify_ble_hci_vendor_stack_config.py` actual compiled ARM C/native PASS 12 across null/invalid/active guards, mode 0 limits/acceptance and all three mode 1 frequencies. It compares entire 0x8a8-byte row and 0x300-byte MMIO window with the same divider cut.
- Dedicated `audio-ble-vendor-stack-config-stage/receipt.json`: Main compile/relocatable link PASS, 1784 defined, 751 unresolved, zero duplicate strong definitions, SHA-256 `e770d4767e212ba9be99d82789774752b11dd106e13e1943d36626d0f2390eaa`. Vendor start/divider/IRQ children and live rows remain; full Main incomplete.

### Vendor stack start (2026-10-11)

- Added `display_ble_hci_vendor_stack_start.c` for complete retained native 0x55c32e: row signature/active guards, hardware start guard, optional DMA state reset and preparation, authenticated 0x800040 control write, completion wait, active-flag set on success, MMIO clear on wait failure, and native high-register return. `verify_ble_hci_vendor_stack_start.py` actual ARM C/native PASS 8 across null/invalid/active, guard failure, with/without DMA, DMA failure, wait failure/success. It compares the full 0x8a8-byte row and 0x300-byte MMIO window with authentic guard/DMA/wait child cuts.
- Dedicated `audio-ble-vendor-stack-start-stage/receipt.json`: Main compile/relocatable link PASS, 1786 defined, 752 unresolved, zero duplicate strong definitions, SHA-256 `3bea4420be887a7e768aa38af7335172393565c72ba73cf7d55207f2b5654396`. Newly exposed vendor guard/DMA/wait children, live row/config and product data remain. Full image remains incomplete.

### Vendor stack start guard and DMA preparation (2026-10-11)

- Added `display_ble_hci_vendor_stack_start_children.c` for native start guard 0x55bd2e and DMA preparation 0x55c0dc. The guard uses authenticated 0x40050000 + index*0x1000 + 0x11c MMIO, compares the low state bits and writes 1 or 0x10. DMA preparation clears row offsets 0x828/0x20/0x85c, constructs the exact four-word parameter block including preserved R3 high word, calls genuine queue child 0x538d58, and sets row+0x20 to 0x100 on zero result. `verify_ble_hci_vendor_stack_start_children.py` actual ARM C/native PASS 5 for guard paths and DMA success/failure, comparing child parameters, entire row and MMIO.
- Dedicated `audio-ble-vendor-stack-start-children-stage/receipt.json`: Main compile/relocatable link PASS, 1788 defined, 751 unresolved, zero duplicate strong definitions, SHA-256 `635041ff996910d2641974a5185b8093e0c5b77af151a2dab76d1aabc2dd1ac2`. The queue child is a genuine remaining code contract; live product rows and radio hardware runtime remain unresolved.

### DMA queue channel setup (2026-10-11)

- Added `display_ble_hci_dma_queue.c` for complete native 0x538d58: channel/parameter/out validation, 0x2c-byte live channel row allocation with busy bit, source/limit/length fields, authenticated identifier 0x00cdcdcd, descriptor pointer, and five register effects. ROM slots 0x539244/248 authenticate twelve rows at 0x2006ef28 and 0x28-byte descriptor entries at 0x6c0f40; descriptors remain typed source-owned ROM data contracts, not copied opaque payloads. `verify_ble_hci_dma_queue.py` actual ARM C/native PASS 7 for invalid channel/parameters/busy and successful setup, comparing entire row and MMIO window. Its test fixture loads authenticated descriptor bytes solely for comparison; the production C references an external typed descriptor table.
- Dedicated `audio-ble-dma-queue-stage/receipt.json`: Main compile/relocatable link PASS, 1789 defined, 752 unresolved, zero duplicate strong definitions, SHA-256 `b179ad3220a90956e3d80d9f021f8856ce9e8029de1e67c73b6369e29e3eab62`. Live channel rows and ROM descriptor ownership/placement remain source-data gates; full Main remains incomplete.

### Vendor clock divider arithmetic (2026-10-11)

- Added `display_ble_hci_vendor_divider.c` for complete native 0x55bf64 and its arithmetic children 0x55bf1c/0x55bf50. It preserves integer ceiling, CLZ/shift behavior, encoded fractional/odd divider fields, nearest-frequency calculation and special power-of-two fallback. Authenticated ROM clock constants 0x05b8d800 and 0x0003d090 are source-defined values. `verify_ble_hci_vendor_divider.py` executes actual ARM C and unmodified native children for 28 frequency/mode pairs, PASS 28 comparing both return registers. These fixtures include zero, low rates, the 250/500 kHz fallback and 48/96 MHz limits; they do not prove every possible 32-bit frequency or hardware clock quality.
- Dedicated `audio-ble-vendor-divider-stage/receipt.json`: Main compile/relocatable link PASS, 1793 defined, 751 unresolved, zero duplicate strong definitions, SHA-256 `0739862bb77a50d57a2eddf71723964bac53175eab61682be5cae3d77a9c5069`. Source remains candidate, with live vendor data, radio and IQ graph and whole-image placement/runtime gates open.

### Vendor option linked-node callbacks (2026-10-11)

- Added `display_ble_hci_vendor_option_children.c` for native 0x55c13a/0x55c168. Before-store forms the self-linked node through the authenticated 0x40050000 + channel*0x1000 + 0x22c MMIO pointer only when row+0x24 is zero, then calls the genuine DMA release child with row+0x828; after-load calls the DMA resume child with the same field. `verify_ble_hci_vendor_option_children.py` actual ARM C/native PASS 3 for linked-node, skip and resume effects.
- Dedicated `audio-ble-vendor-option-children-stage/receipt.json`: Main compile/relocatable link PASS, 1795 defined, 751 unresolved, zero duplicate strong definitions, SHA-256 `2085775a04b1954fb7032be7bf383af66d7df4f2f211f79bbd23d602e144e749`. DMA release/resume remain authentic code contracts; full Main and radio runtime incomplete.

### DMA release/resume (2026-10-11)

- Added `display_ble_hci_dma_release_resume.c` for native 0x538e3c/0x538e8c. It validates the authenticated 0x01cdcdcd channel signature, follows the typed descriptor control pointer, sets/clears MMIO enable bit and active row flag, and executes DMB SY when the native 0x20080000 address threshold is met. `verify_ble_hci_dma_release_resume.py` actual ARM C/native PASS 8 for null/bad/inactive/active and barrier-threshold paths, comparing entire row and control register; the barrier instruction executes in both emulated implementations.
- Dedicated `audio-ble-dma-release-resume-stage/receipt.json`: Main compile/relocatable link PASS, 1797 defined, 749 unresolved, zero duplicate strong definitions, SHA-256 `d83c1959d452074a762e5e315bd197995789d8b0757540f7d113d90cf8d73578`. Product descriptor table/rows and whole-image/runtime gates remain.

### Radio reset/pin routing and vendor stop (2026-10-11)

- Added `display_ble_hci_radio_reset_mask.c` for complete native vendor reset 0x55c286 and radio pin routing 0x4c2e30. The ROM pin function selector 3 is authenticated at 0x78ee48. `verify_ble_hci_radio_reset_mask.py` compares actual compiled ARM C and stock across 23 guards/routes, PASS 23. Corrected an earlier exact symbol reference for stack option 0x55c7e8. Dedicated `audio-ble-hci-radio-reset-mask-stage/receipt.json`: compile/relocatable link PASS, 1800 defined, 746 unresolved, zero duplicates, SHA-256 `17fdc3162cc427d3a8d907c1efed495b5d05e324198c620a5743e6b60f30d91c`.
- Corrected the vendor stop 0x55c430 lower call ABI to pass its row in R0; the focused actual ARM C/native oracle now compares that register and PASS 9. Added `display_ble_hci_vendor_stop_hal.c` for native 0x55c11a, DMA close 0x53909a and DMA count refresh 0x538d18. The stop/close oracle compares six actual C/native guarded, busy and success transitions with the refresh child cut, PASS 6; the refresh body is target compiled but has no standalone native runtime qualification yet. Dedicated `audio-ble-vendor-stop-hal-stage/receipt.json`: Main compile/relocatable link PASS, 1803 defined, 745 unresolved, zero duplicates, SHA-256 `d0652b45511afc4345dd1579de6756d7075f25650976a9cd4a0c2e16c8fb45a8`.
- The focused HCI/radio/vendor namespace remains 80 direct imports (70 HCI, 4 radio, 6 vendor). They include live product RAM, ROM tables/strings and at least 30 distinct genuine code contracts, including larger event/IQ decoders, resource validation and radio context recovery. The whole Main candidate has 745 unresolved symbols across all namespaces. This import count is a link frontier, not a body completeness count: source placement, data initialization, runtime and full native equivalence remain open.

### Radio revision command transfer (2026-10-11)

- Added `display_ble_hci_radio_read_revision.c` for native revision wrapper 0x52eeea and full command packet/response body 0x52ea28. The ROM word at 0x52f298 authenticates command 0x00402000. The C builds the nine-byte request, initializes native-sized packet/response buffers, calls the genuine exchange child, copies the low-byte-count response or logs its status and returns 15. `verify_ble_hci_radio_read_revision.py` executes actual ARM C and native stock for five null/exchange/success/status paths, PASS 5, comparing request bytes, exchange length, output copy and logger argument. It cuts the genuine exchange and logger child effects; product error string at stock 0x75d590 remains typed ROM data.
- Dedicated `audio-ble-radio-read-revision-stage/receipt.json`: Main compile/relocatable link PASS, 1805 defined, 747 unresolved, zero duplicate strong definitions, SHA-256 `90e413bb8ce0f866c41263ad7fda268abc95744d50c481b9b71b3b76720f5f8c`. The two new genuine contracts are exchange 0x52e612 and the authenticated error string. Full command transport, product data and Main image remain incomplete.

### Radio request exchange (2026-10-11)

- Corrected the revision command's fifth stack argument: native 0x52ea9c stores the received-count pointer at SP before calling 0x52e612. Added `display_ble_hci_radio_exchange.c` for complete native 0x52e612: three null guards, begin child, authenticated 0x40010410 bit-21 poll with 5,000,000 limit, delay, receive retry until command bytes match and native two-register return. `verify_ble_hci_radio_exchange.py` compares actual ARM C/native over seven cases (nulls, begin failure, first match, retry, receive failure), PASS 7, including both R0/R1. The 5,000,000 iteration timeout is statically reconstructed and not emulated as a complete timeout fixture. Begin/receive children are genuine pending code, as is hardware state.
- Dedicated `audio-ble-radio-exchange-stage/receipt.json`: Main compile/relocatable link PASS, 1806 defined, 748 unresolved, zero duplicate strong definitions, SHA-256 `5d62ae90ceed49a336c8f33b8551244f3365ddba85541f3573732c00f8a8e706`. The two newly exposed child imports keep source completion false.
- Subsequent native register audit found that exchange forwards its original R2 request length into begin 0x52e0d2. The C call is corrected and the focused seven-case oracle now records and matches R2=9. Fresh `audio-ble-radio-exchange-abi-stage/receipt.json` PASS, 1806/748/zero duplicates, same linked output SHA-256 `5d62ae90ceed49a336c8f33b8551244f3365ddba85541f3573732c00f8a8e706`; the earlier build happened to preserve R2 in generated code but the source ABI is now explicit.

### Radio exchange send child (2026-10-11)

- Added `display_ble_hci_radio_exchange_begin.c` for full native 0x52e0d2 send path: selection, 0x104-byte bound, transmit-space chunking, serial fallback, native 0x30-byte vendor descriptor, error logs, release and context reset. ROM slots 0x52ed30/0x52ede0 authenticate log strings at 0x71b740/0x730e54; these remain typed ROM data imports. `verify_ble_hci_radio_exchange_begin.py` actual ARM C/native PASS 7 over select error, oversize, zero-length, no space, two-byte serial, vendor success and vendor error, comparing child order, descriptor count/type/payload and log arguments. Vendor, serial and context child internals remain separate code contracts.
- Dedicated `audio-ble-radio-exchange-begin-draft/receipt.json`: Main compile/relocatable link PASS, 1807 defined, 755 unresolved, zero duplicate strong definitions, SHA-256 `e9b14ade8776a58049c50f66ece1d6557c4b525c35022d4e80b5f10b637c353f`. The higher import count exposes genuine transmit and vendor children, not an image-completion regression.

### Radio exchange receive child (2026-10-11)

- Added `display_ble_hci_radio_exchange_receive.c` for native 0x52e1ea: product busy and hardware-ready guards, context selection, vendor header retry and bulk read, serial fallback, bounds/error logs, GPIO pacing, received-count update and context reset. ROM slots authenticate busy cell 0x20074f4f, MMIO 0x40010410 and four log strings 0x768ae4/0x6f7d84/0x71b778/0x71b7b0. These remain real data contracts. `verify_ble_hci_radio_exchange_receive.py` actual ARM C/native PASS 6 over busy/not-ready/select error, serial invalid/success and vendor success. It compares call order, GPIO, read count and output bytes. Vendor retry/error and multi-chunk paths remain unqualified; native vendor child must initialize the two-byte header before a successful read.
- Dedicated `audio-ble-radio-exchange-receive-draft/receipt.json`: Main compile/relocatable link PASS, 1808 defined, 761 unresolved, zero duplicate strong definitions, SHA-256 `5e081ef8e41274cb8c58523ded0393d13ae51edcd030fd4aceaad48156922072`. The +6 import growth exposes actual vendor/serial and product ROM/RAM children. Whole firmware source, placement and hardware remain incomplete.

### Radio serial and context-select children (2026-10-11)

- Added `display_ble_hci_radio_serial_children.c` for complete native 0x52e072/0x52e058/0x52dd1c/0x52dc98/0x52dcde: context select and stack option/start, transfer release timing and busy-cell reset, live serial-mode read and byte transmit/receive through authenticated 0x40010440/0x4001045c/0x40010408 MMIO. Product mode cell 0x20074f53 remains a typed runtime import. `verify_ble_hci_radio_serial_children.py` compares actual ARM C/native over ten cases, PASS 10, including exact GPIO/MMIO write sequence for two transmitted bytes and received bits, stack calls and release effects.
- Dedicated `audio-ble-radio-serial-children-stage/receipt.json`: Main compile/relocatable link PASS, 1813 defined, 757 unresolved, zero duplicate strong definitions, SHA-256 `c7a5eabec6f819ebf3544d3f5caafae1d0262753770b27feff91b720c0b054de`. The next directly connected code frontiers are tx-space 0x52df50 and vendor stack send/receive 0x55cf40/0x55cc1c; product mode/busy cells are live data contracts.

### Radio transmit-space query (2026-10-11)

- Added `display_ble_hci_radio_tx_space.c` for native 0x52df50: live busy-cell set, GPIO low, 12,000 polls of authenticated 0x40010410 with 100-tick delays, ten vendor/serial retries of command 0x42 and returned free space, vendor error log and native result. The 0x52ec80 ROM slot authenticates log string 0x6ff930, kept typed. `verify_ble_hci_radio_tx_space.py` compares actual ARM C/native PASS 5 over vendor immediate/retry/error and serial immediate/retry, including GPIO order, command byte, result and busy cell. Full 12,000-poll timeout is statically reconstructed but not executed in this bounded harness.
- Dedicated `audio-ble-radio-tx-space-stage/receipt.json`: Main compile/relocatable link PASS, 1814 defined, 757 unresolved, zero duplicate strong definitions, SHA-256 `9b76e9b0d4320e86d7a65fee2969e1e7770cb5feabb5d184788796f4a83365e3`. Vendor stack send/receive and associated data remain significant connected code frontier.

### Vendor transfer guard and encoder (2026-10-11)

- Added `display_ble_hci_vendor_transfer_children.c` for complete native descriptor guard 0x55c1e0 and control-word encoder 0x55bce8. ROM slots 0x55cc10/0x55c514 authenticate masks 0x00e0e0e0/0x000fff00; the 64-bit allowed-address mask is reconstructed from 32-bit halves to avoid an unselected runtime helper. `verify_ble_hci_vendor_transfer_children.py` actual ARM C/native PASS 34: ten guard cases (size, address, pointer/type, mode, strict flags) and 24 control encodings. No product configuration values are fabricated.
- Dedicated `audio-ble-vendor-transfer-children-stage/receipt.json`: Main compile/relocatable link PASS, 1816 defined, 757 unresolved, zero duplicate strong definitions, SHA-256 `8482ff3f70f9c388661268f4d1b9e6795a9ff87abe928aa70d497d20c55893c3`. Larger stack send/receive 0x55cf40/0x55cc1c remain genuine connected bodies; whole Main and six-image hardware/runtime source closure remain open.

### Vendor FIFO send (2026-10-11)

- Added `display_ble_hci_vendor_send.c` for full native 0x55cf40: row/descriptor/transfer guard, live vendor MMIO setup, control encoding, FIFO polling and word/partial-byte transfers, final wait, recovery and register restoration. ROM slots 0x55d248/278/27c authenticate 0x40050000, signature 0x01123456 and 500,000 poll limit. `verify_ble_hci_vendor_send.py` actual ARM C/native PASS 13 over six guards, zero/word/partial transfers, three wait failures and finish recovery. It compares entire MMIO window, output input bytes and child call order. Long asynchronous polling and hardware timing remain unverified; wait/finish/recovery lower effects are genuine imports.
- Dedicated `audio-ble-vendor-send-draft/receipt.json`: Main compile/relocatable link PASS, 1817 defined, 759 unresolved, zero duplicate strong definitions, SHA-256 `7492e8be906c43e042ff6115121bab8e2bf630e853475e9ffe5161d6fac0889b`. Vendor FIFO receive 0x55cc1c remains another substantial native body.

### Vendor FIFO receive (2026-10-11)

- Added `display_ble_hci_vendor_receive.c` for full native 0x55cc1c: row/descriptor/type guard, native zero-length type rewrite, MMIO setup and control encoding, type 1 read FIFO, type 0 write FIFO, partial-byte handling, wait/recovery and register restoration. `verify_ble_hci_vendor_receive.py` actual ARM C/native PASS 14 over guards, zero/word/partial read, type 0 write, three wait failures and finish recovery. It compares entire MMIO window, output bytes and child order. Long asynchronous waits and hardware state remain runtime gates.
- Dedicated `audio-ble-vendor-receive-draft/receipt.json`: Main compile/relocatable link PASS, 1818 defined, 758 unresolved, zero duplicate strong definitions, SHA-256 `4360b5cd0fddd820b641cfd6c0638f808ef79dba471eb598aead3e7267726ec4`. Current HCI/radio/vendor namespace has 92 direct imports (72/11/9), including source data and newly exposed genuine lower functions. Whole Main remains incomplete with 758 unresolved direct imports; this is a link frontier, not a count of missing whole bodies.

### Vendor wait and completion result (2026-10-11)

- Added `display_ble_hci_vendor_wait_finish.c` for native masked polling 0x480826 and vendor completion classification 0x55bd70. The completion branch tests authentic bit 9 (`LSLS #22`), not bit 15 suggested by one decompiler rendering; stock disassembly and actual execution resolved it. ROM constants 0x55c548/54c/550 authenticate MMIO 0x40050000 and 0x08000001/2 errors. `verify_ble_hci_vendor_wait_finish.py` actual ARM C/native PASS 10 over equal/unequal/timeout/yield and all completion statuses including extra status. Yield remains a genuine hardware/time lower.
- Dedicated `audio-ble-vendor-wait-finish-stage/receipt.json`: Main compile/relocatable link PASS, 1820 defined, 756 unresolved, zero duplicate strong definitions, SHA-256 `db5ffa82edbb13a2bd24226cfe4599126b88e05a65530971a5f0d994b6d17fcb`. Vendor recover 0x55bdac and yield 0x4807a0 remain code contracts.

### Vendor recovery (2026-10-11)

- Added `display_ble_hci_vendor_recover.c` for complete native MMIO recovery 0x55bdac: save/disable control, bit-11 flush/read-drain, bit-0x210 reset sequence with authenticated 0xdeadbeef fill word, interval delay, and final interrupt clear/control restore. `verify_ble_hci_vendor_recover.py` actual ARM C/native PASS 6 over plain, empty/one-word flush, receive drain and reset/both branches, comparing the entire 0x290-byte MMIO window and delay argument. Unbounded hardware spin waits remain a runtime condition, and the yield child is still a genuine timing contract.
- Dedicated `audio-ble-vendor-recover-stage/receipt.json`: Main compile/relocatable link PASS, 1821 defined, 755 unresolved, zero duplicate strong definitions, SHA-256 `96e271d43be9327b841397463774545c1e3895f979ad45ad462930ae6f2cf047`. Main still lacks live data initialization, placement and hardware validation.

### Vendor VFP delay (2026-10-11)

- Added `display_ble_hci_vendor_yield.c` for native 0x4807a0: exact VFP unsigned-to-float and fixed-point conversion, live 0x40021000 clock-mode branch, 250.0f/96.0f scaling, overhead subtraction and a typed resident-ROM cycle-delay call at address 0x40. ROM slots 0x4807f0/f4/f8 authenticate float constants and clock cell. `verify_ble_hci_vendor_yield.py` actual ARM C/native PASS 16 over both mode branches and duration 0 through 0xffffffff, comparing call presence and exact cycle count. The resident ROM routine is an explicit external contract and has no C source in the retained image.
- Dedicated `audio-ble-vendor-yield-draft/receipt.json`: Main compile/relocatable link PASS, 1822 defined, 755 unresolved, zero duplicate strong definitions, SHA-256 `6040bc757c2a96655a8c9722fdd2feda96cbcbe39f266e07ebd0b49d98f539f9`. ROM symbol replaces the yielded code import; firmware remains incomplete.

### Vendor IRQ bank routing (2026-10-11)

- Added `display_ble_hci_vendor_irq_dispatch.c` for complete native seven-bank disable 0x4c44bc and enable 0x4c4530 routing with IRQ bound 0x39 and low-byte arguments. `verify_ble_hci_vendor_irq_dispatch.py` actual ARM C/native PASS 20 over all fourteen bank routes and three invalid guards per direction, comparing exact lower selection, argument and low return. Native R7 high-return is unobserved by selected callers and not asserted as an equivalent output. Fourteen bank-specific lower bodies remain genuine contracts, some already source-defined elsewhere.
- Dedicated `audio-ble-vendor-irq-dispatch-stage/receipt.json`: Main compile/relocatable link PASS, 1824 defined, 767 unresolved, zero duplicate strong definitions, SHA-256 `19c48edf8ade6aeca1480571ac190c35ee635221f54cb3c0bcfaec114ccc84fd`. Import growth exposes bank-specific native code. Full HCI context/decoder graph and product data remain open.

### Radio context handshake (2026-10-11)

- Added `display_ble_hci_radio_context_check.c` for native 0x52e4b4: reset/GPIO sequence, two 30,000-tick bit-21 status phases, response read, authenticated 0x0101ff04 compare, product diagnostic word and three real log branches. ROM 0x52f090 authenticates expected word; 0x52eba4 authenticates MMIO 0x40010410. `verify_ble_hci_radio_context_check.py` actual ARM C/native PASS 4 over null, successful match, mismatch diagnostic and receive error. It compares setup/GPIO/reset/delay/read/log order and live diagnostic word. Long timeouts are statically reconstructed, not exercised across all 30,000 iterations; product log strings and reset/setup lower effects remain distinct contracts.
- Dedicated `audio-ble-radio-context-check-stage/receipt.json`: Main compile/relocatable link PASS, 1825 defined, 771 unresolved, zero duplicate strong definitions, SHA-256 `14b3506412a93f66422ef9e62b6cb0c98d4c618dec8d900b4b863bcc0f291678`. The higher direct import count exposes real product log/runtime and reset/setup lower bodies. Whole Main source/placement/runtime remains incomplete.

### Radio context pin and reset children (2026-10-11)

- Added `display_ble_hci_radio_context_children.c` for native setup 0x52e49a and reset delay 0x4910f4. ROM 0x52e6a8 points to 0x78ee44 = base pin config 0x93; enabled config is 0x2093. Reset forwards millisecond input multiplied by 1000, preserving 32-bit wrap, into the selected vendor VFP delay. `verify_ble_hci_radio_context_children.py` actual ARM C/native PASS 6 over enabled/disabled/low-byte argument and zero/unit/overflow delay, comparing exact lower arguments. Native R7 return is unobserved by selected callers.
- Dedicated `audio-ble-radio-context-children-stage/receipt.json`: Main compile/relocatable link PASS, 1827 defined, 769 unresolved, zero duplicate strong definitions, SHA-256 `b3ad3095d1669c8b17e26efa3a2abee6aa182b9f347d9e609c377cd97bc84f8e`. HCI context graph retains larger recover/configure and product data contracts.

### Radio context recovery (2026-10-11)

- Added `display_ble_hci_radio_context_recover.c` for native 0x52f0f8: optional current-mode read/compare, stop/set/special/commit/check sequence, exact request bit packing, ten diagnostic branches and native two-register result with the response word in R1. Ten ROM pointer slots 0x52f2b8..dc authenticate the product strings, kept typed external data. `verify_ble_hci_radio_context_recover.py` actual ARM C/native PASS 9 over read failure/match, stop/set/special/commit/check failure, success and skip-read; it compares R0/R1, child/log order and committed two-word payload. The six command children are genuine remaining code bodies.
- Dedicated `audio-ble-radio-context-recover-draft/receipt.json`: Main compile/relocatable link PASS, 1828 defined, 783 unresolved, zero duplicate strong definitions, SHA-256 `89760623817b137417ce95fb850b398b72f85823766622f1e188030cd58c29ef`. Newly exposed imports are real command children and product strings, not full context completion. Whole Main remains source incomplete.
### HCI radio recovery command wrappers (2026-10-11)

`display_ble_hci_radio_recover_commands.c` now defines the four original native command bodies at 0x52f094, 0x52ef74, 0x52efba, and 0x52efec. The first two command templates were corrected to their actual address ownership after an ARM C/native fixture exposed their initial reversal. `verify_ble_hci_radio_recover_commands.py` passes eight actual ARM C/native comparisons covering each wrapper with exchange success and failure: exact transmitted request bytes, CRC call arguments, copied response bytes, and return status. The first 24 commit request bytes are protocol fields and computed CRC, not an opaque executable or data blob. The deeper exchange and CRC algorithms have their own separate candidate proof scopes.

Dedicated experimental Apollo Main build `g2/build/c-firmware/20261011/audio-ble-radio-recover-commands/receipt.json` passes compilation and relocatable linking with 1,832 defined symbols, 779 unresolved symbols, zero duplicate strong providers, SHA-256 `d6992ef5f02acb40f9196399897ebb4725ef97c59fff51818df2570647297d9b`. Source completeness remains false: radio stop 0x52e8be and other HCI descendants, product RAM and log data, resident services, final placement, and hardware runtime validation remain open.
### HCI radio configuration stop and pin pulse (2026-10-11)

`display_ble_hci_radio_recover_stop.c` defines the original 0x52e8be configuration-mode polling loop, including status bit 21, receive retry and reset, four-byte response comparison, and original unbounded wait. `display_ble_hci_radio_recover_pulse.c` defines its reset and pin-pulse children 0x52e8a4/0x52e854 with the ROM-authenticated pin configuration 0x183 and the original `(duration*1000)/33` pulse count. The selected 0x4751c8 comparison body is `g2_lfs_memcmp`; three log literals remain typed source-data imports. Controlled actual ARM C/native comparisons pass four stop traces (success, receive failure and retry, response mismatch, delayed ready) and four reset/pulse call sequences (0, 1, 2 duration). Calls to receive, compare, delay, GPIO, and log were cut at their true ABI; these fixtures do not prove peripheral timing or live hardware behavior.

Dedicated experimental Apollo Main build `g2/build/c-firmware/20261011/audio-ble-radio-recover-stop-pulse/receipt.json` passes compilation and relocatable linking with 1,835 defined symbols, 781 unresolved symbols, zero duplicate strong providers, SHA-256 `c59ef4b1cbcc1b3a40e01dc070321e316a399ecd16b55eb543d8c79c68bda690`. Source completeness remains false; the three new log data contracts explain the net import increase despite three genuine code bodies being reduced.
### Fresh Touch and CASE selected graph audit (2026-10-11)

Read-only source and fresh experimental target builds were used to reassess the two other Cortex-M components. Touch receipt `g2/build/c-firmware/20261011/peripherals-touch-audit/receipt.json` passes candidate compilation/link with 228 defined, nine typed unresolved generated CapSense pointees, zero duplicate strong providers, SHA-256 `911b8972e640996960fe723a560d06e142912297ea5068aa7014082751f372c0`. This experimental top-level context selection differs from the earlier 229/0 selected graph. The unresolved names are `touch_generated_{active_scan_sns,base_frame_context,common_config,internal_context,lp_history,lp_sensor_frame_context,pin_config,sensor_frame_context,widget_config}`. The pinned v6 LP source establishes 16-bit history elements and a 212-word nominal window but does not establish the 426-byte linker extent from `0x2000065e` to `0x20000808`; the scalar `0x20000828` still has no attributed field or consumer. No generated `cycfg_capsense` declaration or symbol-size map was found in the current component/analysis source search. Thus reset ownership remains 534/964 attributed bytes and 430 unowned (426+4) in the prior hash-bound reset audit; the fresh target graph does not resolve those two data extents.

CASE receipt `g2/build/c-firmware/20261011/peripherals-case-audit/receipt.json` passes candidate compilation/link with 70 defined, three unresolved (`case_binary_command`, `case_legacy_command`, `case_vformat`), zero duplicate strong, SHA-256 `8355fc1647031b0812be4047033708df55261726cff3f574852792eaa3a80248`. Existing experimental `full_command_candidate.c` and `vformat_candidate.c` are real, partially compared C candidates, but the selected frame dispatcher accepts arbitrary command payload opcodes. The command audit identifies ten legacy switch targets and 14 visible binary command values; the 180 formatter oracle cases do not establish its full domain. Promoting these candidates as complete providers would erase genuine branch and lower-effect obligations. The actionable CASE source frontier is the high-opcode legacy family (`b0`, `d0..d4`, `dd`, `df`, `ee`, `ff`), its nonreturning reset/standby and lower effects, remaining binary command families, and full formatter callback/grammar edge cases. This audit made no CASE or Touch source edit; it found no newly authenticated generated initializer or full-body alias that could be safely admitted during this round.
### CASE ship-mode branch and standby descendants (2026-10-11)

The experimental CASE legacy command candidate now includes the full native `0xee` branch from stock 0x08000928: USB-present return/logging, USB-absent two guarded PMIC reads, watchdog disable, power-stop request, wake-pin setup, product register write, and standby entry. `known_dispatch.c` routes `0xee` to this body; `0xff` remains the one unsupported legacy opcode in that bounded dispatcher. `verify_case_ee_full.py` passes eight actual Cortex-M0 native/C whole-branch comparisons over USB/log state and child return variants, including exact lower-call sequence, log text, MMIO register write and return register. Lower calls are cut at authenticated entry ABIs, so this is not a physical standby claim.

`shipmode_mmio_children.c` defines native 0x08005094, 0x080050a8 and 0x080050c4 with exact GPIO/SCB MMIO updates and architectural `WFI`; `verify_case_ee_mmio.py` passes 24 actual Cortex-M0 native/C cases with varied mode and register seeds. `shipmode_power_stop.c` defines native 0x08002c30's three-attempt PMIC set/read loop; `verify_case_ee_power.py` passes 12 direct native/C cases covering both modes and success after 1/2/3 attempts or exhausted retry. Its guarded children already exist in the experimental source archive; physical PMIC effects remain lower validation gates.

`build_full_experiment.py` builds all selected and experimental CASE source into a deterministic relocatable object with zero undefined symbols: `g2/build/c-firmware/20261011/peripherals-case-ee-closed/case-combined.o`, SHA-256 `6769f2e13a53adae56a19165624061ada260b3f395b67645e13b94fddaa76051` (receipt alongside). The selected CASE firmware archive remains 70 providers/three imports because the full command and formatter candidates are not admitted as complete native providers. The remaining bounded direct command gate is `0xff` plus binary full-domain and formatter qualifications; reset/standby hardware, source layout and final image equality remain open.

The already sourced `0xff` reset entry and 0x0800502c AIRCR/idle child have a retained 36-case original/source reset-loop comparison. `known_dispatch.c` now routes `0xff` as well, giving all 256 opcode values an experimental branch under the allocated valid-buffer contract. The new combined source build remains deterministic with zero undefined symbols: `g2/build/c-firmware/20261011/peripherals-case-all-opcode-dispatch/case-combined.o`, SHA-256 `8d862af1d6b254df3c89f3a8ec884c8de7e5c9778a697cc16886e6056ce29f81`. The 36-case reset receipt is a prior hash-bound binary; this edit only changed routing and comments around that source body. No full 256-opcode connected stock/source oracle or production image equivalence is implied. The full binary command and formatter domains, nonreturn physical reset/standby, product linker layout and hardware effects remain open.

A fresh linked Cortex-M0 legacy source ELF was subsequently built by `build_case_legacy256.py` from the current 21 C translation units with explicit authenticated lower-call addresses. `verify_case_legacy256.py` compares the full stock public entry to the linked dispatcher for **2,560 cases**: all 256 opcode bytes, logical lengths 0/1/2/4/8, and both log-state values. It records branch result, handled flag, non-stack writes, selected RAM state, ordered lower calls, and used logger text/arguments. The test now includes `0xee` and `0xff` with child effects cut at original ABIs; all comparisons pass. The receipt is `linked256-comparison.json`. This establishes connected bounded behavior for allocated 32-byte command buffers under controlled lowers. It does not establish physically short buffers (notably `0xdd`'s byte-1 access), live PMIC/reset/standby effects, arbitrary logger callbacks or final image placement. The selected CASE archive still has three unresolved public/formatter symbols pending full binary and formatter qualification.

`verify_case_vformat_extended.py` freshly compiles the experimental formatter and compares actual Cortex-M0 native/C callback output and return across **1,140 cases**, including 116 retained native caller-format strings, 28 source literal formats, 512 deterministic random grammar cases, length modifiers, `%n` variants, and 77 unknown/floating-conversion forms. It exposed a real `%#o` precision discrepancy: stock does not add a separate alternate-form zero when precision already supplies one. `vformat_candidate.c` now follows that rule; the complete enlarged fixture passes. The combined CASE source experiment remains deterministic and links with zero undefined symbols at `g2/build/c-firmware/20261011/peripherals-case-formatter-extended/case-combined.o`, SHA-256 `fa08122f420636e26f1e0428385577a7920e95a3a1fe99b66abc5521014e418f`. This still does not prove all malformed strings, overflow, callback failure, or every native caller format; selected `case_vformat` remains an unresolved contract.

The current selected-plus-experimental CASE object was linked as a Cortex-M0 test ELF, `case-binary-whole.elf`, with `case_binary_command_candidate` as the entry. This avoids relying on the older isolated binary dispatcher ELF. `verify_case_binary_whole_no_lower.py` passes **5,370** actual stock/whole-candidate cases whose paths return without a lower call, spanning non-destination-2 opcode routing, destination-2 fallback and guarded specials. `verify_case_binary_whole_local_four.py` passes **480** controlled lower cases for `0x50`, `0x5c`, `0x5d`, `0x68`; send and ack stop at true entry, while GPIO control is cut with matched return. `verify_case_binary_whole_handoff.py` passes **48** whole-entry cases for destination-2 `0x06` and `0x41`, matching ack opcode, one-byte handoff (`0xee` or `0xff`), logical length one, and return at the legacy lower cut. These are connected whole-candidate tests on allocated 256-byte buffers. They do not cover the remaining special families through all lower effects, nor physical transport/flash/sensor timing; selected CASE public binary provider remains unresolved.

Two further native/whole-candidate special branches now pass on the same current ELF: `verify_case_binary_whole_14.py` compares **216** `0x14` cases through sourced reader wrappers to controlled sensor transaction/delay and send; `verify_case_binary_whole_3f.py` compares **192** `0x3f` cases through the sourced enable/program path to controlled bus/logger/ack, including retry and logging mutation. The connected whole-candidate total is 6,306 compared cases across distinct fixtures (5,370+480+48+216+192); these sets are bounded and their count is not a percentage of the accepted input domain. Remaining distinct special families include `0x3d`, `0x3e`, `0x51`, `0x56`, `0x5e`, `0x5f` and full effects of `0x06`/`0x41`; stock lower behavior and product configuration remain separate.

All six previously distinct CASE binary special families now have connected whole-candidate comparisons on that same current ELF: `0x3d` **192**, `0x3e` **288**, `0x51` **45**, `0x56` **216**, `0x5e` **120**, and `0x5f` **45** cases. The fixtures compare full entry routing and bounded source state to authenticated stock while cutting real native lower ABIs (dispatch/control/logger/ack/send/flash apply/exit) where physical effects or lower ownership are independent. `verify_case_binary_whole_legacy_effects.py` adds **24** connected `0x06`/`0x41` cases through the full sourced EE/FF legacy branch, matching logs, lower sequence, product MMIO write and return under controlled standby/reset/PMIC children. The bounded whole-binary fixture count is now 7,236 (prior 6,306 plus 906 plus 24), with overlapping behavioral domains possible; it is not complete accepted-input coverage. Directly connected flash success data, sensor and transport physical behavior, malformed/short buffers, and final placement remain open.

`verify_case_flash_apply_whole.py` next compares the actual compiled CASE `case_binary_5e_apply` body to stock 0x0800373c for **288** combinations of mode, logging flag, flash-read retry outcome, first/second program outcome, and three 16-byte input patterns. It passes with equal ordered mode/init/read/wait/program/finalize/log calls, exact four register arguments for each flash program block, return value and all 16 configuration bytes. The receipt is `case-flash-apply-whole-comparison.json`, keyed to the linked Cortex-M0 `case-binary-whole.elf` and source/stock hashes. This qualifies the previously untested erase-success and both program-success/failure paths of the source body under controlled real lower ABIs. Physical flash persistence, asynchronous wait and the command-to-apply connected success path remain open.

The formatter's 1,140-case direct native/C oracle was rerun with callback return values selected among zero, `0xffffffff` and positive by format length; all cases still pass, including emitted output and formatter return. This tests attempted-emission counting for these callback outcomes, while arbitrary callback side effects/faults, malformed input pointers and overflow limits remain unqualified. Current CASE selected source still has exactly three unresolved public symbols (`case_binary_command`, `case_legacy_command`, `case_vformat`); the experimental all-source archive links with zero undefined. Beyond those three admission gates, physical flash/sensor/transport effects, product layout and hardware proof are separate finite requirements.

An exhaustive single-byte formatter conversion suffix sweep (all 254 non-`%` values from 1 to 255) extends the direct compiled-C/native oracle to **1,394 passing cases** with the same three callback-return categories. `build_case_public_candidate.py` selects the actual three public provider objects and their archive dependencies into a deterministic relocatable CASE source candidate at `g2/build/c-firmware/20261011/peripherals-case-public-source/case-public-source.o`: **260 defined, zero undefined, zero duplicate strong**, SHA-256 `883e819380450e71f5c788a4765bd57607e0dfb1938d68d7f8be573f8b11aeaa`. The receipt records both input archive hashes and bounded evidence. This is a source provider selection for review, not canonical image admission; the pre-existing selected archive remains unchanged at 70/3. Native proof gaps are narrowed to malformed pointer/allocation and unbounded formatter width/precision/callback behavior. Runtime hardware effects and final placement are separate image requirements.

After public-source review, the canonical CASE source candidate builder now includes the native-backed command/formatter graph as explicit source members. A fresh deterministic Cortex-M0 build selects **153 translation units, 262 defined symbols, zero unresolved imports and zero duplicate strong providers**. Its archive SHA-256 is `e5476d3821872dbc21c9a8624dd2dfc0df673be2adaa0164ac3c2c7abd77dce3`, and the relocatable source object SHA-256 is `5f8fa00b476175d24250eac379857576154c18490d449b39b88f0ed81fc10fde`; the authoritative receipt is `g2/analysis/case-source-candidate-round2-20261010/receipt.json`. The older 70/3 baseline statements above are historical. The builder records `source_complete: false` because malformed pointer/allocation and unbounded formatter edge behavior lack full stock equivalence evidence, and final linker placement plus physical effects remain unvalidated. `build_full_experiment.py` now detects this selected public graph and avoids compiling it twice.

Main/Audio resumed with full native group-2 IRQ enable lower 0x4c3e9a in `display_ble_hci_vendor_irq_bank2_enable.c`: bit-presence early return, critical pin clear, group-any check, command 4 with one-byte payload, live power flag and pointer clear, and PRIMASK restore. The two product RAM cells remain typed external ownership contracts. Cortex-M4 target compile passes; `verify_ble_vendor_irq_bank2_enable.py` passes **32** actual stock/C cases over bit presence, remaining-group state, high pin truncation and live RAM seeds, comparing child order/args, RAM bytes and return. This closes one genuine bank lower, while the other bank routes and group-2 command itself remain separately sourced/imported.

The group's command child is authenticated stock 0x4809c4, already source-owned as selected `audio_oscillator_control` with a retained 600-plus-case direct native comparison. The group-2 IRQ C body now calls that exact selected provider for action 4. Its own 32-case native/C comparison still passes. This removes the provisional `audio_uart_mux_group2_command` import; only the two typed live RAM cells remain newly exposed by this lower.

Native ROM literals at 0x4c4680/84 authenticate the exact live addresses 0x20074f56/0x20074260, and existing selected crystal request/ownership source already accesses them directly. The new IRQ C body now uses those same typed address contracts instead of exporting new data symbols; no initializer value is fabricated. A fresh selected+experimental Main build at `g2/build/c-firmware/20261011/peripherals-group2-final/receipt.json` passes with **1,836 defined, 780 unresolved, zero duplicate strong**, relocatable SHA-256 `69d6f7bee996978c4a86b919ed512f0f914e69cbf43132fe9266215f20842d51`; `source_complete` remains false. The prior 782-import snapshot included provisional data symbol names and is superseded for this source state.

The remaining seven-bank IRQ/mux lower names were mapped against exact native entry addresses and already selected source bodies: bank 2 request is selected `audio_xtal_request` (0x4c3d9e, retained direct 404-case crystal corpus); bank 4 is `audio_hfrc_request` (0x4c3f2a); bank 5 is `audio_hfrc2_request/release` (0x4c4086/0x4c420c); bank 6 is `audio_syspll_request/release` (0x4c427e/0x4c43ec), with retained 816-case HFRC/HFRC2/SYSPLL corpus. Exact-address wrappers in `display_ble_hci_vendor_irq_existing_banks.c` reuse those complete bodies and the previously selected bank0/1/3/off4 bodies; they do not substitute for any missing native implementation. The new bank2 release body supplies 0x4c3e9a. A fresh target Main build at `g2/build/c-firmware/20261011/peripherals-irq-banks-complete/receipt.json` passes **1,856 defined, 760 unresolved, zero duplicate strong**, SHA-256 `9d2c34957edd304ffc6a17eea28565ed79cdfba9d4e049b7efc8b6f1b625cd90`. All fourteen direct bank dispatch imports and five parallel mux names are now source-bound. The remaining 760 imports include five mux product RAM/capability cells and two distinct vendor power IRQ names (`0x47f5b8/0x47f7ae`) whose existing power source is explicitly experimental with stock branch limitations; link closure alone would not qualify them. No source-owned initializer for the live mux RAM cells was authenticated in this round.

Native power enable/disable pseudocode at 0x47f5b8/0x47f7ae exposed two further real differences from the generic vendor projection. Stock ignores the GPU SPOT callback result in both directions, including a failure value; `power_vendor_candidate/power.c` now does so. Stock debug disable performs two separate control-register writes after clearing DEMCR; the source now preserves their order rather than combining masks. `verify_power_gpu_spot_continue.py` executes actual stock and Cortex-M4 C for **12** bounded cases: enable GPU mode 0/3 with callback return 0/1/7 through IRQ save, disable callback return 0/1/7 through clock release-all, and three seeded debug-register patterns through Tempco postpone with exact MMIO write sequence. All pass. This is not yet full 314/350-byte power admission: the product descriptor/config object and active non-GPU branches lack complete native/C comparison, and hardware waits remain unverified.

Five mux data contracts were traced to actual Main ROM slots. `pin_mux_attributed_data.c` now defines the three authenticated pointer constants: bitset 0x4c43dc→0x20073324, capabilities 0x4c43e8→0x200001cc, and group-4 power word 0x4d3a08→0x40004044. The group-3 active/idle ROM pointers 0x4c4678/7c target immutable image words 0x78ee34/38, both value `3`; those two source constants are selected. This supplies no initial contents for live RAM and leaves exact final linker placement explicit. A fresh Main target candidate at `g2/build/c-firmware/20261011/peripherals-power-mux-data-round/receipt.json` passes **1,861 definitions, 755 unresolved, zero duplicate strong**, relocatable SHA-256 `79744c360985067922acd90a0103abc4947391c8c9408c3bb90984668a9f6d6a`. The five-import reduction is sourced data, not additional code-body closure; source completeness remains false.

The native power descriptor function 0x47ef18 reads an authenticated 34-row semantic table from ROM 0x6becb0 (literal 0x47f944). `power_descriptor_native.c` expresses its masks and register groups as C formulas, including the five distinct shared status groups and the second peripheral register bank, without copying a stock data blob. `verify_power_descriptor_native.py` executes original ARM and compiled Cortex-M4 C for **78** selector/null combinations (all 34 valid rows and five invalid selectors, with null/non-null output) and compares status plus all four semantic fields; PASS. The vendor enable/disable C also now applies native low-byte truncation at entry. The root experimental manifest does not auto-select this new directory member; a manual Cortex-M55 softfp target compile and relocatable link with the current Main candidate succeeds at **1,862 defined, 754 unresolved, zero duplicate strong**, reducing one genuine code import. Coordinator manifest inclusion is pending. The broader vendor power body still lacks complete product config and full native/C branch qualification.

The power product's immutable selectors, masks, wait budgets, MMIO addresses and five shared-domain masks are now expressed by `power_product_native.c`, attributed to the retained 0x47f5b8/0x47f7ae/0x47f6f2 native branches and ROM literal targets. GPU current/previous mode uses authenticated adjacent live byte cells at 0x20074f60/61, not source-initialized values. The native source address map identifies 0x480826 as selected `audio_wait5`, 0x4807fc as selected `audio_wait4`, and 0x4807a0 as selected `audio_delay_us`; vendor C now calls these exact providers. This corrected a real disable error: stock 0x47f86a passes wait polarity zero to detect status clearing; the previous C had polarity one. `verify_power_crypto_gate_connected.py` passes **12** stock/C precheck cases through the actual descriptor and product C, and `verify_power_enable_connected.py` passes **56** stock/C pre-critical paths across device/audio/GPU groups with callback outcomes. The GPU/debug oracle remains PASS **12** after the timing binding correction. These bound the connected branches only; full wait/IRQ restoration and every disable path remain open. The product object still awaits root manifest selection, after which a coherent Main target receipt is needed.

The product object was selected and a fresh Main candidate at `g2/build/c-firmware/20261011/peripherals-power-product-round/receipt.json` passes target compilation and relocatable link: **1,863 definitions, 749 unresolved, zero duplicate strong**, candidate SHA-256 `44e1d260948286453421a513c8a38f970a145e08467c8b85cdea83994f2c0eb0`. This is a candidate source graph, not final image placement or live power proof.

Native 0x48032c and 0x480342 are exact live platform callback dispatches through slots 3 and 4 at RAM 0x20073270. `power_callbacks_native.c` implements both complete short bodies and leaves slot initialization as a separate runtime contract. `verify_power_callbacks_native.py` passes **16** stock/C null and non-null callback cases, including return propagation; Cortex-M55 softfp `-Werror` target compilation passes. Vendor power now calls already selected exact-address C bodies for SPOT callback dispatch 0x480312 and pin-mux enable/disable/all 0x4c44bc/0x4c4530/0x4c45a4, instead of new unresolved aliases. The previous crypto/GPU/enable comparisons still pass after these source bindings, and `verify_power_disable_precritical.py` passes **56** direct native/C selector and GPU-mode cases through the critical-save cut. The callback source awaits root experimental manifest addition. GPU transition 0x47f11c and postcritical IRQ/wait effects remain active source/behavior gaps.

The callback source was selected and a coherent Main target build at `g2/build/c-firmware/20261011/peripherals-power-callback-round/receipt.json` passes **1,865 definitions, 743 unresolved, zero duplicate strong**, SHA-256 `69b33d559013aeab9f5b5061759739601a363c986f8b69de1452e3db29608f9d`.

Native GPU transition 0x47f11c is now `power_gpu_transition_native.c`: mode guard, GPU-rate register guard, descriptor-backed power-off guard, identical-mode previous-state update, PRIMASK save/restore, platform callback slot 9, 0x40021090/0x4002108c MMIO changes, delay 1/6 and two live mode byte updates. Native/C execution exposed and corrected the polarity of its power-status guard: stock allows mode changes when GPU power status is clear. `verify_power_gpu_transition_guards.py` passes **80** direct stock/C combinations; `verify_power_gpu_transition_effects.py` passes **18** successful transitions, including null and failure-return callbacks, ordered writes and return values. Cortex-M55 softfp `-Werror` compile passes. After manifest selection, fresh Main `g2/build/c-firmware/20261011/peripherals-power-transition-round/receipt.json` passes **1,866 definitions, 742 unresolved, zero duplicate strong**, SHA-256 `539dcd004eef46293de9f141fe018f70c92f55f5d3ed2f768a31c4f6146afa9c`. No `g2_power_*` import remains, but this is only closure of the selected power source graph. `verify_power_enable_wait_entry.py` compares native/C first wait5 call arguments and enable-register state across **16** connected paths; `verify_power_disable_wait_entry.py` covers **14** first-wait/peer-domain paths with clear polarity, callback and register effects. Both pass. Later wait results, scheduler callbacks, physical IRQ privilege and hardware transitions are not established by these bounded oracles, and Main still has 742 unresolved imports.

The next Main radio firmware reconfiguration parent 0x4b480a is reduced in `display_ble_hci_radio_reconfigure.c`: configure/tune, two attempts, success commit/check and failed dispatch. Its two exact source-owned log strings are authenticated at stock 0x777984/0x7602d0; configuration is read from live RAM 0x20074970/96c/968/954. Direct stock/C child-call and return oracle `verify_radio_reconfigure_native.py` passes **9** retry and RAM-seed cases. Short source-owned configuration setters 0x52e5ce/0x52e5f2 write their authenticated live destination cells; `verify_radio_reconfigure_cells.py` passes **24** direct stock/C cases over null/non-null and byte truncation. The connected update attempt 0x52edf0 is now `display_ble_hci_radio_update_attempt.c`; it retains alternate image size, recover/current/erase/write/check error tree, exact source-owned stock diagnostic strings, live prepare flag and successful pin configuration. `verify_radio_update_attempt_native.py` passes **7** stock/C branch traces. The settled Main target receipt at `g2/build/c-firmware/20261011/peripherals-radio-update-attempt-round/receipt.json` passes **1,872 definitions, 749 unresolved, zero duplicates**, SHA-256 `52aad931e411fc8154bd847f4e82b7a83b9dee19c23dd9e31474173f99c57e2d`; the count rose from 742 because the genuine connected parent exposed its deeper code children. The pump preparation child 0x52ed34 now has a complete C read/modify/write/error tree in `display_ble_hci_radio_update_prepare.c`, with exact 0xF0040C/0xF0041C register commands and 0xF0B02 value. `verify_radio_update_prepare_native.py` passes **5** actual stock/C outcomes including four failure exits. A new coherent target receipt including this last child is pending.

Further radio update descendants are source-reduced with direct stock/C effect comparisons: `display_ble_hci_radio_write_command.c` implements native 0x52eaf8 vendor packet/response handling, **15** cases over lengths 0/1/4/8/248 and transport/controller failures; `display_ble_hci_radio_update_erase.c` implements 0x52e9b4 NVM erase, **3** packet/log/status cases; `display_ble_hci_radio_image_rows.c` implements 0x52e788 live row selection, **9** mode/data cases; `display_ble_hci_radio_update_write.c` implements 0x52ebca row iteration with the native 248-byte chunk boundary, destination/data increments and progress calls, **20** cases; `display_ble_hci_radio_update_crc.c` implements current-image 0x52e7c0 and post-write check 0x52ec84 with distinct error/mismatch semantics, **8** cases. The CRC local helper 0x4d34f8 is expressed as a reflected polynomial 0xEDB88320 C loop rather than the authenticated stock table blob at 0x699fa8; `verify_radio_crc_local_native.py` passes **28** cases including seed continuations. The remote CRC helper 0x52e6ac is a full 12-byte HCI request/response decode; `verify_radio_crc_remote_native.py` passes **9** packet/status/output cases. The percentage helper 0x52eba8 passes **8** direct native/C arithmetic/log ABI cases, and alternate serial pin setup 0x52dd24 passes **5** exact native/C calls using authenticated immutable 0x183/0x93 pin settings. A fresh coherent Main build including all these files is running. Live image-row pointers and image payload provenance remain explicit data ownership gates; child effects are cut at their authenticated ABI in these bounded comparisons.

The successful reconfiguration tail is now source-backed: `display_ble_hci_radio_commit.c` implements native 0x52eefa INFO-page read/erase/248-byte rewrite with first-word replacement; `verify_radio_commit_native.py` passes **4** stock/C success and per-stage failure effects. `display_ble_hci_radio_erase_info.c` implements its native 0x52e948 six-byte command and status decode; `verify_radio_erase_info_native.py` passes **3** stock/C packet cases. `display_ble_hci_radio_reset.c` implements native 0x44ab24 architectural DSB/AIRCR reset and 0x44b0ae wrapper; `verify_radio_system_reset_native.py` passes **6** stock/C AIRCR read/write cases up to the reset boundary, with no fabricated success return. The complete connected source graph still depends on physical reset, NVM persistence, authentic live image rows/payload and general HCI/logging runtime. The shared variadic logger import `audio_ble_hci_boot_log_4733ee` was mapped to the already selected exact 0x4733ee source body `g2_log_transport_queue_failure` via a same-translation-unit alias in `transport_failure.c`; its unbounded formatter child remains an explicit source/equality gate. Fresh target integration including the alias is running.

That final selected Main integration at `g2/build/c-firmware/20261011/peripherals-radio-logger-bound-round/receipt.json` passes **1,888 definitions, 740 unresolved, zero duplicate strong**, candidate SHA-256 `2697a20e0807bef91e3aba03e6b0ca2ece2a88ed61eed8ccea437f881d1e8bec`. None of the directly connected `audio_ble_radio_update_*`, CRC, commit, erase-info, ready, alt-mode, or shared 0x4733ee logger names remains unresolved. This is a source provider graph result only. The 740 Main imports include other private HCI/application code, authentic live RAM cells, ROM data and runtime/toolchain contracts, and the unbounded formatter path remains incomplete.

The EM9305 firmware-file path now has complete C source for native file-mode/size helpers 0x52f3a0/0x52f3f8, header validation 0x52fcfc, staged-image finalization 0x52fc04 and one-time recovery gate 0x52fb58. Their direct compiled-C/native bounded checks pass **18, 6, 4 and 6** cases respectively; they preserve the runtime `firmware/ble_em9305.bin` file and its live handle, allocation and image cells. Three downstream parse bodies are also source-owned: 0x52f86a copies the 16-byte header, 0x52f87c decodes at most four 12-byte records to the live 16-byte descriptor array, and 0x52f99e maps recognized device addresses to live image pointers/data rows. The two record parsers pass **6 and 8** original/C bounded effects with logging disabled. A direct oracle caught and corrected an eager logging-only pointer dereference in 0x52f99e. Extended/compressed log branches of those parsers and malformed file input remain outside these comparisons. Fresh Main target receipt `g2/build/c-firmware/20261011/peripherals-radio-records-corrected-round/receipt.json` passes **1,896 defined, 739 unresolved, zero duplicate strong**, SHA-256 `4b5604a3452dc1df1ebcf2a0a508b4939e64b1a196c73229ac3aabffbff73d9e`; the connected image loader 0x52f442 remains an import. No firmware file payload, placement, physical NVM persistence or live radio behavior is established by this build.

The connected loader 0x52f442 is now source-reduced in `display_ble_hci_radio_image_load.c`: open/size/rounded heap allocation/read/close, header and record dispatch, live image pointer cells, and all failure cleanups with authenticated source strings. `verify_radio_image_load_native.py` compares **8** actual stock/C branch and RAM-effect cases from open failure through successful parse, with lower file/heap/parser effects cut at their ABI and log flags zero. A fresh selected Main target receipt `g2/build/c-firmware/20261011/peripherals-radio-loader-round/receipt.json` passes **1,897 defined, 738 unresolved, zero duplicate strong**, SHA-256 `fd5b358427242770f3271f11d39d4b8fe09f7fa6898d35ed2e3de87927d48984`; the direct `audio_ble_radio_image_load_52f442` import closes. Runtime file bytes, malformed-size behavior, nonzero diagnostic flags, actual file/heap allocator behavior, radio/NVM persistence and final placement remain separate evidence gates. This is a connected source chunk, not full Main source completion.

The next Main HCI driver graph is source-reduced in `display_ble_hci_driver_handler.c`, `display_ble_hci_driver_handler_children.c`, and `display_ble_hci_serial_rx_incoming.c`. Native HciDrvHandler 0x4b4ab2 now preserves event-2 start, receive continuation, radio receive/error/restart, queue transmit, retry and timeout branches. Native 0x52b620 buffer-size command, 0x52a4c4 millisecond timer start, 0x4b4d18 queue reset, 0x5300e2 ring consume, 0x491102 delay wrapper, 0x52ae38 command allocation and 0x530186 HCI serial receive FSM are also C bodies. The last parses event and ACL headers into native live cells, calls selected WSF allocators, and dispatches complete packets through 0x530c88; the max ACL getter 0x530d4c is source-owned. Actual compiled-C/native bounded oracles pass **6** handler branches, **7** serial packet/partial-header cases, and **5** ring-consume state/output cases. These cut lower radio/WSF effects at authentic ABI and do not establish live controller behavior or full malformed-input coverage. The fresh Main target receipt `g2/build/c-firmware/20261011/peripherals-hci-handler-settled-round/receipt.json` passes **1,906 definitions, 736 unresolved, zero duplicate strong**, SHA-256 `d9a19388774bd48dc2ed2d4bea35feb24ae69c532ca3c09676566a3fa18e4b7d`. The distinct `HciLeReadBufSizeCmd` remains unresolved; it is not the newly implemented classic `HciReadBufSizeCmd` 0x52b620.

Read-only Touch/CASE reassessment found no newly attributable generated layout owner: Touch's locked reset still has 426 history-window bytes from `0x2000065e` to the next known descriptor at `0x20000808` plus the separate four-byte `0x20000828` scalar without declared object/initializer ownership. The 426-byte interval is an upper window, not a proven allocation size. No generated `cycfg_capsense` declaration or product symbol-size map appears in the current source corpus. CASE's selected Cortex-M0 source graph has zero imports, but its current receipt explicitly retains malformed pointer/allocation, unbounded formatter, product linker layout and physical-effect gates; nearby `.ld` files are test fixtures and do not establish a product linker script. Both remain incomplete components.

The HCI reset sequence's direct Cordio command frontier is now C source in `display_ble_hci_init_commands.c`: six empty opcodes, three 8-byte event masks, LE default data length, vendor power level (signed range check), vendor NVDS parameter seed and the common vendor packet sender. `verify_hci_init_commands_native.py` compares **26** stock/C allocation success/failure and packet effects, including 0xFFF2's six native-written live bytes at `0x20074150`. A fresh selected Main target receipt `g2/build/c-firmware/20261011/peripherals-hci-init-commands-round/receipt.json` passes **1,919 definitions, 724 unresolved, zero duplicate strong**, SHA-256 `84c1968b8b62b0ecbe92770b737cc1b9ee0a37df597258402da8d5ae5fc57963`. No `Hci*` command import remains in this snapshot. The reset handler's other live tables/ROM masks and hardware command transport remain separate source/runtime contracts; neither BLE controller execution nor full Main source coverage follows from this link.

The same command source now includes LE resolving-list-size and max-data-length commands 0x52b7dc/0x52b24c plus native reset feature gates 0x569b04/0x569b2a. The gates read the authenticated state byte at `0x20071500` and capability byte at `0x20000028`, testing bits 6 and 5, then update live size byte `0x20071509` or send the correct fallback command. The expanded actual stock/C packet/branch oracle passes **40** cases, including crossed capability bits. Fresh Main target receipt `g2/build/c-firmware/20261011/peripherals-hci-init-branches-round/receipt.json` passes **1,923 definitions, 722 unresolved, zero duplicate strong**, SHA-256 `518fa992dc4ce3b11834b81f29a75903597e71b1d2fd86df1dd223fcaa84bdb6`. Main remains a candidate source graph with extensive live data, ROM tables, other application code and image-placement requirements.

Three additional genuine ATT/DM dispatch bodies are now source-owned. `display_ble_att_handler.c` reconstructs native AttHandler 0x4b5146, including five event ranges and the live high-event direct callback, and `verify_ble_att_handler_native.py` passes **14** compiled-C/native callback/argument cases. `display_ble_dm_hci_callback.c` reconstructs dmHciEvtCback 0x4d299c and DmHandler 0x4d2a5c, preserving the live `0x20073b78` enable gate, class indexing and callback slots; `verify_ble_dm_hci_callback_native.py` passes **24** stock/C cases. The first DM handler's immutable event-class table at original ROM `0x6e006c` remains a typed source-data import `audio_ble_dm_hci_event_class_map_6e006c`; the bounded oracle linked its C reference to the original table for comparison and did not copy it into candidate source. The authenticated 0x5c-byte table is adjacent to other ROM data, so arbitrary event codes beyond its expected domain still need source/layout qualification. Fresh selected Main target receipt `g2/build/c-firmware/20261011/peripherals-att-dm-dispatch-settled-round/receipt.json` passes **1,926 definitions, 720 unresolved, zero duplicate strong**, SHA-256 `ce00df6a787b87a994f1c9a2cab7aadd63218f5dd1fa52c828871d5777d115af`. This link closure does not own live ATT/DM class vtables or controller execution.

Native `_bleSlaveProcMsg` 0x46e098 is now an experimental complete event-switch C candidate in `display_ble_slave_proc_msg.c`. It preserves the 0x05/09/0a/0d/0e, 15/16, 21/22, 27/28, 37, 47/48, ad, b5/b6/b7/b8, ba/bb branches; source log strings and flag reads; connection open/disconnect cleanup; retry timers; advertising restart; security; TPL timeout and notifications. Five small genuine descendants are in `display_ble_slave_proc_children.c`: 0x4b46a8, 0x4bac4e, 0x47a676, 0x47aec0 and 0x47aec8. The C target syntax passes ARM Cortex-M55 freestanding `-Werror`. Fresh coherent selected Main candidate at `g2/build/c-firmware/20261011/peripherals-slave-proc-complete-round/receipt.json` passes target compilation and relocatable link with **1,932 definitions, 745 unresolved, zero duplicate strong**, SHA-256 `9b94658571022c48d5992aac1c70420485449b8fe0e9a16dfce6030687bc486a`. This is source/compile evidence, not a stock runtime comparison. Child callback functions 0x46f098/0x46f350/0x46effc, BLE advertisement/security operations, and product RAM 0x20074f8b/c/d remain genuine typed contracts; unresolved imports grew because the full parent exposed them. Connected stock/C effects oracle is still needed, especially role-1 disconnect, logging-enabled paths, and live address table ownership. The other native `bleProcMsg` 0x4b75ce is a separate 293-line parent and remains unimplemented.

The three native delayed callbacks 0x46f098/0x46f350/0x46effc are now full C in `display_ble_slave_proc_callbacks.c`. The actual compiled-C/native effects comparison `verify_ble_slave_callbacks_native.py` passes **8** cases: security argument, trusted-state write, allocation failure and success, encoded 10-byte message prefix, and send handler. This comparison has logging disabled and does not qualify log-enabled varargs return registers. `_bleCommProcMsg`/`bleProcMsg` 0x4b75ce is now `display_ble_comm_proc_msg.c`, covering native event 0x12/15/20/27/28/2a/2b/2c/2d/2e/34/35/3c/46/79/a5/a6/bc and default; it exposes genuine pairing, timer, hash, notification and radio children. `verify_ble_comm_proc_minimal_native.py` passes **18** actual compiled-C/native event cases over event 0x00/12/15/20/2d/79 and three connection IDs. This is a bounded qualifier only; pairing, encryption, error logs and product-state transitions still need connected effect qualification. Two connected children, native 0x4bb07c pair-record lookup and 0x4b82e8 RPC security-state send, are in `display_ble_comm_proc_children.c`. The latter's compiled-C/native eight-byte payload, command, role-query order and state argument pass **9** cases in `verify_ble_comm_security_native.py`; it references the authenticated immutable template at 0x78c9ac via the typed ROM table beginning 0x78c9a4. Fresh Main candidate `g2/build/c-firmware/20261011/peripherals-slave-comm-children-round/receipt.json` passes target compilation and relocatable link with **1,938 definitions, 771 unresolved, zero duplicate strong**, SHA-256 `cc13c3fb52c7be9284b1e2719a74dde2cd649861aa6544a133afbe90a495aa99`. The source graph and source-equivalence flag remain incomplete; no hardware behavior, image placement or final product RAM ownership is inferred.

The connected bounded oracle scope was expanded without altering candidate source: `_bleSlaveProcMsg` now passes **114** compiled-C/native role/event/log flag cases across 19 event classes, two roles and flags 0/1/2, including role-1 open schedules, disconnect cleanup, MTU, live state and compact/extended diagnostics; `bleProcMsg` passes **144** cases across 16 event classes, three connection IDs and flags 0/1/2, including pair-fail/encryption and their logs under controlled child effects. These are effect comparisons with selected child calls intercepted; successful nested pairing, advertising stack and hardware paths remain outside the bounded scope. `display_ble_app_ui_action.c` now reconstructs the full native Packetcraft AppUiAction 0x4bd054 event/log switch and live callback invocation through RAM 0x20073f60. `verify_ble_app_ui_action_native.py` passes **99** actual compiled-C/native cases: every event 0..31 and 255 under logging flags 0/1/2, comparing compact text, extended line/text, and callback arguments. The RAM callback cell initializer/placement is still a product contract. Fresh Main target `g2/build/c-firmware/20261011/peripherals-ble-ui-round/receipt.json` passes **1,939 definitions, 771 unresolved, zero duplicate strong**, SHA-256 `558df923a73f66789be64523abf6334d4740d374368556118f8a478c396be63f`. No final-image or live-controller claim follows from this receipt.

Native Cordio pairing-failure descendants now have source-defined C candidates. `display_ble_pair_failure.c` reconstructs AppDbHandlePairingFailure 0x47c568 and preserves its null, invalid and status-specific record branches. `display_ble_pair_failure_children.c` reconstructs AppDbShowNvmStatus 0x47c2bc over mapped MRAM 0x7ff000 and AppDbClearRecordByConnId 0x47c8cc; `display_ble_pair_storage_refresh.c` reconstructs AppDbReloadResolvingList 0x47b4d4, including resolver clear and selected AppLoadResList. Actual compiled Cortex-M4 C/native bounded effect checks pass 45 parent, 21 children and 3 refresh cases across log policies and record states. The coherent target Main candidate at `g2/build/c-firmware/20261011/peripherals-pair-failure-round/receipt.json` passes 1,959 definitions, 768 unresolved imports, zero duplicate strong, SHA-256 `afe2f37f0f5d1c297a343ad61f5af8b5b704d51052666d85fe530d350377ed4b`. These counts reflect newly exposed genuine descendants, not a regression in source attribution; physical MRAM contents and BLE controller effects remain external.

The next connected source member `display_ble_pair_remove.c` expresses AppDbClearRecordByMacAddr 0x47b59c plus lookup 0x47ad74 and record clear 0x47a47c. The lookup uses the existing typed 10 by 200-byte live RAM rows and counter, selected address comparison, actual host address type and native timestamp update. The parent preserves null/no-match/match diagnostics, rewrite/validation and resolving-list removal. `verify_ble_pair_remove_native.py` passes 13 bounded actual compiled-C/native cases, including return and call order, ten-row search and timestamp/row effects. The deeper rewrite/validation/resolving-list hardware/storage paths are separate existing candidate or external contracts. Full BLE application/component and full Main image source equivalence remain false.

Fresh target Main candidate `g2/build/c-firmware/20261011/peripherals-pair-remove-round/receipt.json` passes with 1,962 definitions, 769 unresolved imports and zero duplicate strong, SHA-256 `74952bf2a9c1e0e5f40e64d75faf25185c8818fae958568ac74d18dcd0f070bf`. The new unresolved genuine descendants include `DmHostAddrType` (native 0x4d2aa8, reads a live role byte at a product pointer) and `DmPrivRemDevFromResList` (native 0x4d2880, allocates and sends a WSF message). The source code count rises by three while the import count rises by one because whole native parent functions expose their real children; neither metric is a full-source completion flag.

The two direct leaves exposed by the removal source are now source-defined in `display_ble_dm_privacy_remove.c`. `DmHostAddrType` 0x4d2aa8 reads the existing live DM state byte at product address 0x20073b8e and maps types 2→0 and 3→1 only when that byte is set. `DmPrivRemDevFromResList` 0x4d2880 allocates a 12-byte WSF message, writes the native 16-bit handle/event/type fields and six address bytes, then sends to the live DM handler ID at 0x20073b84; allocation failure preserves the native no-send path. `verify_ble_dm_privacy_remove_native.py` passes 14 bounded actual compiled-C/native cases. Message allocation/send themselves are separate selected/runtime contracts; live DM state initialization is not source-owned by these two bodies.

Fresh Main target candidate `g2/build/c-firmware/20261011/peripherals-pair-dm-remove-round/receipt.json` passes with 1,964 definitions, 769 unresolved imports, zero duplicate strong, SHA-256 `816c9dad736c087b8ca8fce68c8d238fb41ead547990f8ef9bbaa789c84ef99d`. The two DM names are now definitions; the complete source bodies expose genuine `WsfMsgAlloc` and `WsfMsgSend` imports, so unresolved count remains 769. Both WSF operations are actual native code contracts requiring separate implementation/selection, not no-op stand-ins. The candidate source link and bounded emulation are not full product source equivalence, final image layout or live BLE execution.

The new WSF message imports are now source-defined, with further real descendants exposed. `display_ble_wsf_message.c` implements native WsfMsgAlloc 0x4bf99e (8-byte pool header offset) and WsfMsgSend 0x4bf9ba (queue lookup, enqueue, readiness). `display_ble_wsf_queue_ready.c` implements WsfTaskMsgQueue 0x52b97c, WsfMsgEnq 0x4bf9de and WsfTaskSetReady 0x52b95e. The queue address is the authenticated `0x20073230+0x34` field of typed live WSF state; readiness bit is at `+0x3c`. Bounded original/compiled-C checks pass 12 message wrapper cases and 9 queue/enqueue/ready cases, including allocation failure, 16-bit size wrap, payload preheader write, critical-section order and signal. WsfBufAlloc, WsfQueueEnq, WsfCsEnter/Exit and WsfSetOsSpecificEvent remain real deeper source imports, as does live WSF task RAM initialization. No allocator or OS-event no-op was introduced.

Fresh target Main candidate `g2/build/c-firmware/20261011/peripherals-pair-wsf-round/receipt.json` passes with 1,969 definitions, 773 unresolved imports and zero duplicate strong, SHA-256 `da6e78df1b39b837b6deeae6898066403d9c3af7fb5af3fc529cd1c55b7b3817`. The five WSF public message/queue functions now define source bodies; their real next-level pool, queue, critical section and OS signal children plus live WSF state are unresolved. The increased import count is connected native frontier exposure, not evidence of a completed WSF subsystem.

`display_ble_wsf_queue_critical.c` now reconstructs WsfQueueEnq 0x538c24 and the native nested critical-section primitives WsfCsEnter/Exit 0x52b8a4/b6. Original Thumb instructions at 0x52b8ac/0x52b8c4 are `cpsid i`/`cpsie i`; C uses those exact architectural operations only on depth zero transition, with a typed live depth byte at 0x20075045. The queue links its new node at tail or initializes head/tail under that critical section. `verify_ble_wsf_queue_critical_native.py` passes 12 actual compiled-C/native cases across first/nonempty queue and depth 0/1/2, comparing queue/node memory and PRIMASK. WSF pool and OS event signaling remain outside this source chunk.

Fresh Main target candidate `g2/build/c-firmware/20261011/peripherals-pair-wsf-queue-round/receipt.json` passes with 1,972 definitions, 771 unresolved imports, zero duplicate strong, SHA-256 `0b496e5afc8a5a3902fae99df43d0780c0b4e2a1b48dcddc04b8d1a49810153a`. Three additional genuine source bodies replace five direct queue/critical imports and expose the one live critical-depth byte contract. Source completeness remains false.

The two substantive WSF leaves are now C candidates. `display_ble_wsf_os_signal.c` reconstructs WsfSetOsSpecificEvent 0x52b8d8: it reads a live FreeRTOS task handle at 0x20074ef0, checks privileged exception mode through the already selected CONTROL/IPSR helpers, calls the actual task or ISR notify children, and performs native SCB ICSR PendSV write with task-path DSB/ISB when notification requests a yield. `verify_ble_wsf_os_signal_native.py` passes 16 bounded native/compiled-C cases covering absent/present handle, task/ISR, notify return and higher-priority-woken results. `display_ble_wsf_buf_alloc.c` reconstructs WsfBufAlloc 0x530446 from the live pool table pointer at 0x20074eec and class count at 0x20075044, scanning 12-byte size classes, entering/exiting the real WSF critical section, popping a free block, clearing its second word, and logging exhausted pools. `verify_ble_wsf_buf_alloc_native.py` passes 15 native/compiled-C class and log cases. Live task/pool RAM initialization and notification children remain separate real contracts; these tests intercept those children and do not prove full OS scheduling.

Fresh Main target candidate `g2/build/c-firmware/20261011/peripherals-pair-wsf-signal-pool-round/receipt.json` passes with 1,974 definitions, 774 unresolved imports, zero duplicate strong, SHA-256 `0a69c81c0f2f44598dbd1e023cef9346b0f631ba173cba44ca35ee7904f49c97`. The pool and OS signal names are now definitions. This hash-bound snapshot exposed two notification imports and three live product cells (pool table pointer, pool count, OS task handle). Subsequent address mapping showed the notification functions at 0x47ee4a/0x47ed76 are the already selected pinned FreeRTOS `xEventGroupSetBitsFromISR`/`xEventGroupSetBits` bodies, so the OS signal C now calls those exact providers directly; the next receipt must capture that correction. The three live cells remain unresolved. This count is a relocatable candidate graph census only and is far from full Main source, RAM initialization, or physical hardware equivalence.

The WSF notification call map is corrected in the selected source: stock 0x47ed76/0x47ee4a are the pinned FreeRTOS `xEventGroupSetBits`/`xEventGroupSetBitsFromISR` functions already selected from `foundation/freertos_event_group/event_groups_subset.c`. The intermediate redundant ISR wrapper was removed. The WSF signal bounded native/compiled-C oracle remains PASS 16 after direct provider binding. Fresh Main target candidate `g2/build/c-firmware/20261011/peripherals-pair-wsf-selected-notify-round/receipt.json` passes 1,974 definitions, 772 unresolved imports, zero duplicate strong, SHA-256 `1b5d0ba978f982cae551cf09f1ffba725927c8e79fa3fd5b2fbabf1fbf904980`. Two code imports closed by proven selected providers; the three WSF live cells and many other Main source/data contracts remain.

A selected-source crosswalk resolved the five WSF RAM contracts previously described as external in this local round. `display_wsf_os_init.c` defines the event-group handle at native 0x20074ef0 and the 64-byte task state at 0x20073230; its WsfOsInit body zeros state and creates the event group if absent. `display_wsf_pool_data.c` defines the pool list pointer at 0x20074eec, count at 0x20075044 and critical depth at 0x20075045; selected `display_wsf_buf_init.c` sets pool pointer/count from a source-owned four-class product config and arena, while BSS initializes depth. The new WSF bodies now reference those actual selected producer symbols. Original/compiled-C WSF focused suites rerun PASS 16+15+12+9 after rebinding. The 1,974/772 receipt above predates this ownership correction; an aggregate rebuild is required. This proves source-level initializer ownership, not final linker addresses, scheduler execution or physical hardware timing.

Fresh corrected Main target candidate `g2/build/c-firmware/20261011/peripherals-pair-wsf-owned-ram-round/receipt.json` passes with 1,974 definitions, **767 unresolved imports**, zero duplicate strong, SHA-256 `4a5b0068e871254a2d0ba66389e87325e7d9df6b139f2c4d60f9d09783e9f273`. The five WSF source-owned RAM symbols are BSS definitions in the selected aggregate, and the selected WsfOsInit/WsfBufInit bodies provide their runtime initialization. This reduces the previous 772-import candidate by five without inventing product values. It remains a relocatable candidate: source placement at the authenticated RAM addresses, live FreeRTOS/WSF behavior, and the rest of the Main source/data graph remain unproven. The wider Touch and CASE gates remain as in the prior finite audits: Touch 534/964 reset bytes attributed with 430 not owned by a generated declaration/symbol map; CASE selected source graph has zero imports but unbounded formatter/malformed input, product linker and physical execution evidence gaps. All six full component completion flags remain false.

The next connected DM/SMP source unit `display_ble_dm_pair_children.c` defines six authenticated native bodies: DmPrivClearResList 0x4d28b0, DmDevReset 0x4b3026, DmConnRole 0x4b73c4, DmSecGetCompareValue 0x534948, DmSecCompareRsp 0x534910 and pair key ready 0x4bb030. The clear/reset messages use the now selected real WsfMsgAlloc/Send graph; the DM state byte/handler ID use selected `audio_ble_dm_handler_state`, while role lookup reuses the existing typed `audio_dm_connection_records` live data contract. The compare value is the four network-order bytes at offset 12 modulo the native ROM constant 1,000,000. Actual compiled-C/native oracle `verify_ble_dm_pair_children_native.py` passes 271 controlled cases across allocation failure/success, all 256 role IDs, value boundaries, SMP cancel versus success and key-ready child call order. This is bounded effect proof with deeper cancel, send and trace children intercepted. Final live record contents and packet controller effects remain separate.

Fresh Main target candidate `g2/build/c-firmware/20261011/peripherals-dm-pair-children-round/receipt.json` passes with 1,980 definitions, 766 unresolved imports, zero duplicate strong, SHA-256 `44c79f4fbdf6bf1d4331a737928c09dd6d95651d7574f9c5dd2e83504d3afd16`. Six complete source bodies close the direct reset/privacy/role/compare/key-ready names and expose three real deeper code contracts: `SmpScGetCancelMsgWithReattempt` 0x56d188, `SmpDmMsgSend` 0x537bd6 and the diagnostic trace body 0x4bd91e. The connection-record RAM base is the already existing typed `audio_dm_connection_records` contract, not a new synthetic table. No product data initializer or final linker ownership was inferred from link success.

`display_ble_smp_send.c` and `display_ble_pair_key_process.c` reduce native SMP send 0x537bd6, passkey process 0x4bafda and the 32-byte ring random getter 0x53634e to C. `verify_ble_pair_key_process_native.py` passes 36 actual compiled-C/native bounded cases, including direct ring cursor/count cases and connected passkey/SMP routing effects. Main target receipt `g2/build/c-firmware/20261011/peripherals-pair-key-process-round/receipt.json` passes with 1,983 definitions, 766 unresolved imports, zero duplicate strong, SHA-256 `68193c34ef144299ceb4ab94d6df9c74c7c5d3a0ba59f9455b5fcd465f0f3820`. The live random ring at 0x20072cb8 remains a typed product RAM contract; genuine newly exposed `DmSecAuthRsp` and passkey diagnostic trace remain deeper code at this snapshot.

`display_ble_dm_auth_rsp.c` now reduces native `DmSecAuthRsp` 0x4d24d4: allocate 22 bytes, set connection/event/length fields, conditionally copy the exact caller-specified authentication byte count, then deliver to `SmpDmMsgSend`. `verify_ble_dm_auth_rsp_native.py` passes 20 actual compiled-C/native controlled cases over allocation failure/success, lengths 0/1/3/4/8 and null/non-null source, comparing allocation/send effects and 24 message bytes. Cortex-M55 `-Werror` syntax passes. Coherent Main target receipt `g2/build/c-firmware/20261011/peripherals-dm-auth-rsp-round/receipt.json` passes with 1,984 definitions, 765 unresolved imports, zero duplicate strong, SHA-256 `4b01b89c7c3547f441125202c170275ec98e2f0b4ad27bd13a959e29707e88f9`. The connected cancellation, logger and live product configuration state remain source work; this is not final source or hardware equivalence.

`display_ble_smp_cancel_record.c` completes native `smpCcbByConnId` 0x5375fc, `SmpDbPairingFailed` 0x542838 and `SmpScGetCancelMsgWithReattempt` 0x56d188. It retains the native WARN/INFO diagnostic selection, selected formatter/WSF trace calls, CCB retry counter, SMP database record status update, and packet event choice. `display_ble_comm_registration_slot_storage.c` owns the BSS pointer at 0x200004b8: selected `bleCommHandlerInit` writes the authenticated ROM table address before these consumers read it. This declaration does not supply the ROM table or prove final RAM placement. `verify_ble_smp_cancel_record_native.py` passes 16 actual compiled-C/native controlled cases with diagnostic logging enabled and compares message, retry counter, record update, pointer return and call effects. Main target `g2/build/c-firmware/20261011/peripherals-smp-cancel-record-round/receipt.json` passes at 1,988 definitions / 764 unresolved / zero duplicate strong; SHA-256 `6ed7a5b37a0a2b98773cc55fc93fd5a62d2613cde36e2f5153fba2e561bb90fb`.

`display_ble_smp_db_records.c` reduces native `smpDbGetRecord` 0x541fb8, `smpDbAddDevice` 0x541e72, `smpDbRecordInUse` 0x541e50, plus six-byte address equality/copy wrappers. The nine 24-byte record search, allocation fallback to the authenticated database base when full, zero-and-copy creation, and INFO diagnostics are represented. `verify_ble_smp_db_records_native.py` passes 15 actual compiled-C/native cases over empty, occupied, matching and full database records. `display_ble_dm_peer_access.c` adds native peer address type 0x4b6ed8 and pointer 0x4b6eea over the existing typed DM record import; `verify_ble_dm_peer_access_native.py` passes 512 actual compiled-C/native cases across every byte connection ID. Final coherent Main candidate `g2/build/c-firmware/20261011/peripherals-smp-peer-closed-round/receipt.json` passes at 1,995 definitions / 763 unresolved / zero duplicate strong, SHA-256 `261837d9c93c193e4fd5f583267e8188438e4718b2ee0977430827e66c2afccf`. Remaining connected data contracts include live trace policy 0x2007502f, random ring 0x20072cb8, DM connection records 0x200712a4, and the ROM registration table 0x774d44; their layout/initialization provenance is not inferred from candidate compilation.

Direct DM/HCI continuation: `display_ble_dm_ecc.c` reduces full native `DmSecGenerateEccKeyReq` 0x5348ec, its 0x53673e WSF allocation/enqueue child, `HciLeReadLocalP256PubKey` 0x52b1f4 and `DmSecSetEccKey` 0x5348fc. It reuses selected `hciCmdAlloc`, `hciCmdSend`, WSF queue and DM handler state. `verify_ble_dm_ecc_native.py` passes eight actual compiled-C/native controlled cases across allocation failure/success and 96-byte key copying. `display_ble_hci_boot_public.c` binds the public `HciDrvRadioBoot` name to the existing full selected 0x4b48a6 source body, previously verified in five connected cases; this is a canonical-name binding rather than a new hardware proof. `DmDevVsInit` 0x4b308c remains an import: native returns incoming R7 via `pop {r0,pc}`, so a fabricated C return value would be wrong even though the caller ignores it. A tested provisional byte-truncation model failed and was removed before selection.

The live policy byte 0x2007502f has one authenticated literal reference at 0x4c9cd4, the selected getter; no source initializer is attributable from that reference. Random-ring base 0x20072cb8 has four stock literals at 0x5363e8/0x536498/0x5366d4/0x5367e0, with queue pointer 0x20072ce0 exactly base+0x28 and cursor at base+0x3a. This proves shared address arithmetic but not the storage object's full extent or startup owner. DM connection base 0x200712a4 has seven stock literal references, including the already selected 48-byte record accessors; `DmConnInit` writes callback/config tables but does not establish the full record/storage initializer. These remain typed imports, not guessed C globals.

`display_lv_application_root.c` reduces native LV active-screen getter 0x44fc62 and its application root 0x44ff38, preserving missing-display diagnostic and the active-screen return. The latter is passed as the first argument to page-manager initialization by native display-thread sequence; `display_thread.c` now uses the matching typed C return/argument rather than discarding R0. `verify_display_lv_application_root_native.py` passes eight actual compiled-C/native cases including direct, fallback and missing display.

`display_page_manager_new.c` reduces full native `page_manager_init` 0x45f15a: allocation, all three LV objects and style/layout calls, parent/callback links, the BSS manager pointer written on both allocation paths, and the genuine fatal callback/reset path. Product page-style and dimension addresses remain imports. `verify_display_page_manager_new_native.py` passes its 35-child successful construction sequence with page/root memory effects and the allocation-failure fatal callback branch against actual ARM-compiled C/native execution. That failure oracle exposed a wrong callback string assumption; source now passes the authenticated literal `"0"` at 0x45f3c4. Deeper LV object children and actual target display effects remain unverified; source graph expansion is expected.

Final coherent Main candidate `g2/build/c-firmware/20261011/peripherals-page-manager-qualified-round/receipt.json` passes with 2,004 definitions, 784 unresolved imports and zero duplicate strong, SHA-256 `1e89efb766a28008ba72872de0c3de1c45922815ea2b91a0f09138f7e7f6af0b`. Relative to the prior 1,995/763 receipt, complete parent bodies exposed roughly two dozen genuine LV object/style/callback lower contracts. Current 784 imports are a mixed code/data/runtime frontier, not 784 missing function bodies. The DM/HCI direct set is reduced to the special R7-return `DmDevVsInit` import; ECC/HCI hardware and product RAM remain open. UART/display now has the new LV page construction descendants plus many earlier product literal and runtime cell imports. Touch's 430 unowned reset bytes and CASE's formatter/layout/physical effects remain unchanged by this Main work. No component or firmware image is source-complete.

LV constructor descendant round: `display_lv_page_style_wrappers.c` reduces thirteen native style setters and a composite wrapper with exact property IDs; native 0x44129e truncates its value to one byte. `display_lv_page_style_apply.c` preserves the seven-effect set-local-style sequence. `display_lv_style_resolve.c` reduces selector extraction 0x44b860, property-flag test 0x44b844, and subscribed style-node removal 0x44ca18, including list traversal and owner notifications. `display_page_manager_clear.c` reduces page clear 0x45fb7c and conditional clear 0x45fba2. `display_lv_theme_attach.c` reduces native display-theme attachment 0x44fe0e. Compiled-C versus original ARM bounded oracles pass 36 style-wrapper, 26 resolver/selector/flag, and 16 theme-attachment cases. Remaining style-local allocation, style value mutation, style refresh, and some callback effects are genuine code contracts, so this does not close LVGL.

`display_lv_theme_apply.c` now reduces native theme lookup 0x44fe7e/0x482f74, theme application 0x482f8a, recursive theme-chain walker 0x482ff2/0x482fce, and style-removal wrapper 0x44bc3a. It uses the already selected display default/object lookup providers and the authenticated selector literal 0x000fffff at ROM 0x44c828. The deeper style-removal 0x44ba9a is a genuine unresolved source contract; theme-chain routines have target compilation and native pseudocode correspondence but no standalone full native/C oracle yet. Native 0x44104c, 0x44127e, and 0x488290 retain uninitialized upper-byte/word behavior, so they remain explicit ABI gates rather than fabricated deterministic C bodies.

Latest coherent Main candidate `g2/build/c-firmware/20261011/peripherals-lv-theme-refresh-round/receipt.json` passes with 2,031 definitions, 784 unresolved imports, zero duplicate strong and SHA-256 `a1894db7d4caf752c308293f6a38c2549bf495af7ec84c8fdb8b347f1b8724fe`. Relative to the page-manager round, 27 additional definitions are source-defined; the equal unresolved count reflects true newly exposed children. Main still has substantial LVGL style, UART, OS, ROM, product RAM, and layout work. No image source-completion or live-hardware claim follows from this build.

LV style core continuation: `display_lv_style_local_value.c` reduces full native get-local-style 0x44c5d4 and lv_style_set_prop 0x482868, including compact object style record insertion, 5-byte property/value allocation, constant-style diagnostic, invalid-property fatal path, and allocation effects. `display_lv_style_refresh.c` reduces full native refresh 0x44bc8c with live root refresh flag, layout/parent/layer/draw/child branches. `display_lv_style_remove.c` reduces full native removal 0x44ba9a: transition deletion, owned-style reset/free, record compaction, realloc, and conditional refresh. `display_lv_style_tree.c` reduces parent 0x44dca2, child count 0x44ddea, and recursive child refresh 0x44c9dc. `display_lv_style_helpers.c` reduces style flag scan 0x44ce2c and reset 0x482796, binding the already selected LV heap free provider. `display_lv_realloc.c` reduces LV realloc front end 0x44f76a and pool wrappers 0x48432a/0x484234 with genuine queue semaphore, TLSF reallocate, accounting, diagnostic, and typed live pool cell. `display_lv_style_position.c` reduces position getter wrappers 0x44b870/0x44b866 to their shared true lower.

The native/compiled-C oracles pass: theme walker four valid-object cases, local style two, style value four, refresh 56, remove five, tree six, style flags four, realloc front end four, pool realloc four, and position wrappers two. The theme walker oracle exposed a source bug: stock dereferences a null child before testing its next pointer; source now preserves that fault. Refresh oracle exposed the native OR short circuit between the two position getters; source now matches. These are bounded source/native comparisons with controlled children, not complete LV runtime equality. The preceding theme-chain note about missing standalone oracle is superseded by this bounded oracle.

Latest coherent Main candidate `g2/build/c-firmware/20261011/peripherals-lv-style-position-round/receipt.json` passes with 2,045 definitions, 785 unresolved imports, zero duplicate strong and SHA-256 `bf719f15098719edb83d142e3e7f488c064eee25401774b25a4e6e23b1590429`. The 785 names include newly exposed true LV style/runtime children, product RAM and other whole-image contracts; it is not a missing-function count. Direct LV code children now include shared property fetch 0x44bdea, TLSF reallocate 0x4d0868, property flags table lookup 0x482a6a, render/layout/layer effects, list/transition helpers, and genuine product RAM/ROM ownership. Main source_complete remains false, as do all other images.

The next connected property subtree is C. `display_lv_style_property.c` reduces native 0x44bdea, taking object state, trying selector property, and falling back to the native property-default child. Its initial `value_act` seed is the pinned LVGL zero initializer and equals stock ROM 0x78f26c. `display_lv_style_selector_fetch.c` reduces 0x44ce8a direct, special coordinate, and inheritable-parent paths with the authentic object layout and runtime extension flags. `display_lv_style_entry_find.c` reduces native 0x44c834 selection over transition and normal style records and the style get-property 0x44b7ce. `display_lv_style_property_flags.c` reduces native 0x482a6a special property values, built-in flags and bounded extension lookup. Bounded actual compiled-C/native oracles pass four property, four selector, four entry-search, and all 512 property-flag matrix cases.

`display_lv_style_builtin_flags.c` defines the 138-byte built-in property flag table from the pinned LVGL 9.3 designated initializer with property names and flag meanings retained. FLEX and GRID entries are enabled as demonstrated by authenticated stock ROM. A separate ARM compilation yielded a 138-byte `.rodata` section byte-equal to original 0x6d439c..0x6d4425. This is source-owned static data, not an opaque copied binary payload. The extension flag pointer/length under live LV root remain runtime product cells.

Latest coherent Main candidate `g2/build/c-firmware/20261011/peripherals-lv-style-data-round/receipt.json` passes with 2,052 definitions, 784 unresolved imports, zero duplicate strong and SHA-256 `d322da9bde90b9320c90782000274e1563612bbcd7d4b060c1ae73f2440d4d0f`. Remaining direct LV code contracts include property default 0x48297c with a native partial-word ABI edge, render/layout/layer effects, style list/transition helpers, and TLSF realloc 0x4d0868; heap pool/static slot and LV root extension cells remain live RAM ownership contracts. Whole Main and all six image source-completion flags stay false.

The linked layout/list/transition path is now C: `display_lv_mark_layout.c` reduces native 0x43f648, mutating object and screen layout flags and dispatching the actual display event child. The refreshed 56-case style-refresh oracle now compares the mark-layout R0 argument, which exposed and corrected an omitted object/parent argument in the earlier C. `display_lv_style_list.c` reduces generic intrusive list tail/previous/remove 0x482ce4/0x482cfa/0x482c0e, including product base-offset node links. `display_lv_style_remove_prop.c` reduces native 0x4827b0 with mutable compact allocation, original buffer release, and constant-style diagnostic. `display_lv_style_transition_unlink.c` reduces 0x450500/0x450b0c with the live transition list, callback cleanup and timer rescheduling. `display_lv_transition_schedule.c` reduces 0x4509da/0x46453e/0x464696, preserving pause/resume choice and timer callback state. Bounded actual compiled-C/native oracles pass mark-layout two, list twelve, style property removal five, transition unlink two, and schedule/resume four cases. The live transition list and timer state at LV root 0x2006f548 remain typed RAM contracts.

Latest coherent Main target candidate `g2/build/c-firmware/20261011/peripherals-lv-transition-schedule-round/receipt.json` passes with 2,062 definitions, 780 unresolved imports, zero duplicate strong and SHA-256 `bccc405f58adbc25a3f9393cc6d66d4c4846512f3703029f2f06bbe9737346e8`. Four imports net closed despite genuine new children. Remaining direct LV code includes display/object event dispatch 0x44fdbe/0x451670, property default 0x48297c with partial-word ABI, refresh-draw/layer effects 0x452d42/0x44c50e, and an authenticated source-empty style-removed 0x44ce2a; product heap, lock, tick and transition-list RAM are external. Whole Main still has 780 mixed unresolved names across firmware, so LV local progress is not whole-image completion.

The connected event and draw subtree now has authentic C for display event 0x44fdbe, event-list dispatch 0x44ffe6, event descriptor count/slot/disabled 0x450388/0x450390/0x45037e, event compaction 0x4502e0/0x450346, array clear/resize 0x488478/0x48849c, draw extent refresh 0x452d42/0x452dc8, layer-type refresh/predicate 0x44c50e/0x44cd9e, and object-specific attribute allocation 0x43e1fa. These reside in `display_lv_display_event.c`, `display_lv_event_list_dispatch.c`, `display_lv_event_array.c`, `display_lv_event_compact.c`, `display_lv_draw_layer_refresh.c`, `display_lv_layer_type.c`, and `display_lv_object_spec_attr.c`. Actual ARM-compiled C versus stock Thumb effect oracles pass 4, 8, 9, 8, 8, 4, and 2 bounded cases respectively. The event dispatcher retains nesting, stop state, phase filter and data compaction; the object allocator retains the native 0x34-byte allocation and flag mutation. All deeper event callbacks remain genuine lower effects at their ABIs in these oracles.

The transition list head previously exposed as a separate external symbol is now addressed via authenticated LV root offset +0xac, equal to stock 0x2006f5f4. Its focused transition oracle still passes 2 actual C/native effects. Final coherent Main candidate `g2/build/c-firmware/20261011/peripherals-lv-root-layout-round/receipt.json` passes **2,076 definitions, 776 unresolved imports, zero duplicate strong**, SHA-256 `0586f500fb7107c4700ee41b8602110196b5c6e0ec1289dca4f43bbb4b4661b4`. The remaining 776 mixed imports are neither 776 missing bodies nor proof of image completeness; true direct LV code still includes object-event 0x451670, property-default 0x48297c with a partial-word native ABI, and render invalidation 0x4534be, while heap, LV root, display and callback state remain typed runtime cells. Whole Main source and physical firmware remain incomplete.

`display_lv_event_scope.c` now reduces native nested-event enter/leave 0x44ffd0/0x44ffdc. The stock literal at 0x4502b4 authenticates the LV root at 0x2006f548; its active-event word is +0x6c, and the previous event is stored at event+0x14. `verify_display_lv_event_scope_native.py` passes 6 actual ARM-compiled C/stock RAM comparisons. Coherent Main receipt `g2/build/c-firmware/20261011/peripherals-lv-event-scope-round/receipt.json` passes **2,078 definitions, 776 unresolved imports, zero duplicate strong**, SHA-256 `e47b4a745abc2f94fb51f85f7eb9a238a087839001d96e584092a7bcee98d65a`. The unresolved count remains equal because the immediate object-event parent 0x451670 is still unimplemented; this adds real child bodies without claiming parent closure.

`display_lv_render_invalidate.c` now reduces the complete stock control flow at 0x4534be: default-display resolution, enabled and rendering checks, zero-input reset, viewport clipping, 8-pixel alignment, direct/full refresh mode, event cancellation, containment scan, 32-area overflow reset to the full screen, storage and refresh event. Its rendering-in-progress assertion retains the authenticated source path, line 0x117 and source strings; the fatal memory-write path is not exercised by the bounded oracle. Actual compiled ARM C versus stock controlled-child effects pass **9** branches. The stock/C oracle caught and corrected an overflow branch discrepancy: when the area count reaches 32, native stores the full-screen rectangle, rather than the clipped input.

The directly connected source children `display_lv_render_area_helpers.c` and `display_lv_render_contains.c` reduce native display width/height 0x44fa7e/0x44faa8, area intersection/copy 0x450bcc/0x4530fc, and area containment 0x450f28. Bounded actual C/native oracles pass **24** dimension/area cases and **18** containment/corner-order cases. The rounded-corner child 0x450dd4 is a newly exposed genuine code import. Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-render-children-round/receipt.json` passes **2,085 definitions, 776 unresolved mixed imports, zero duplicate strong**, SHA-256 `26d50154a03e30ce21a1960bf4d76ba1554a3ded67ee3af386d4bf04e27657e5`.

`display_lv_property_default_model.c` models all 256 native 0x48297c branches with the incoming R1 word explicit. The stock function saves R1 and copies only three bytes into it for 0x1c and nine other property IDs, leaving the original high byte. `verify_display_lv_property_default_model_native.py` passes **768** ARM C/native comparisons across 256 IDs and three R1 seeds. The public one-argument source call at 0x44bdea does not capture the post-selector R1 value, so this exact mathematical model remains distinct from the unresolved public provider `audio_uart_lv_property_default_48297c`; binding it without authentic caller ABI evidence would change those returned high bytes. The model compiles in the candidate archive but does not close that public import. Remaining LV source includes this caller ABI, object-event 0x451670 with uninitialized flag bits, rounded-corner geometry, and deeper event/render children; live RAM and whole-image layout/hardware gates remain separate. All image source-completion flags remain false.

The prior property-default public-import gate is superseded by an exact ARM ABI entry bridge in the same C translation unit. Its naked tail branch preserves incoming R1 unchanged and enters the verified C model, so all 256 property IDs and three incoming R1 seeds pass the direct **768-case public-entry** compiled-C/stock oracle. The one-argument caller therefore retains the authentic ambient R1 behavior without fabricating a second C call argument. This qualifies the public function body at its native entry ABI; it does not prove that the separately compiled caller and selector produce register-identical R1 on every path. Coherent Main receipt `g2/build/c-firmware/20261011/peripherals-lv-property-abi-round/receipt.json` passes **2,086 definitions, 775 unresolved mixed imports, zero duplicate strong**, SHA-256 `0939d88ad3426ffba35065125ac43b1a7eeef6d2a0e563972b048fd9a8c9240e`. The public `audio_uart_lv_property_default_48297c` import is closed; whole image source/layout/runtime remain incomplete.

`display_lv_round_corner.c` now reduces the complete native 0x450dd4 rounded-containment body: rectangle rejection, signed radius clamping to half extents, four recursive radius-zero corner tests in stock order, transformed circle bounds and final acceptance. `display_lv_round_geometry.c` reduces authentic extent 0x451598/0x4515a4 and circle predicate 0x45163c using wrapping 32-bit fixed integer arithmetic. Bounded compiled-C/stock oracles pass **36** corner traces, **36** direct geometry values and **63** connected round/extent/circle results, including outside, edge, internal, and clamped-radius points.

`display_lv_object_event.c` reduces native 0x451670 from pinned LVGL 9.3 `lv_obj_send_event`: null-object success, five event fields, three individually cleared bitfields, push, core dispatch, pop and byte return. The stock prologue reads the flags-storage byte from entry SP-16 and clears only bits 0–2; an ARM target ABI bridge reads that exact byte before entering the C model, preserving its five unnamed bits. The initial C model passed the named-field oracle but differed in those bits, so it was corrected. Full-byte compiled-C/stock call/effect oracle now passes **18** cases. The connected property caller 0x44bdea to public default provider 0x48297c also passes **21** direct compiled-C/stock cases with controlled post-selector R1 values across the partial-byte property families; this strengthens the previous standalone ABI proof, while full selector runtime equality remains separate.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-round-object-event-round/receipt.json` passes **2,092 definitions, 774 unresolved mixed imports, zero duplicate strong**, SHA-256 `018068b3eddabe36defbd52d580a126873f128935161bf198fe9a2c2147c42e4`. The newly exposed event core 0x451a6c is genuine code; live LV root, display, heap, callback state, final image layout and hardware effects remain open. This closes the named rounded-corner/object-event providers, not LVGL or Main source completion.

The next connected event graph is source-defined. `display_lv_event_core.c` reduces native 0x451a6c from pinned LVGL 9.3: active input gate, deleted/stop flag exits, target spec-attribute event list, preprocess/base/normal dispatch, result/stop checks, parent lookup and recursive bubbling. `display_lv_event_core_children.c` reduces active input 0x452ef8 from authenticated LV root+0x50, base-class event callback 0x4516f8, event bubbling selector 0x451b34 with the product's numeric code exclusions, and object flag check 0x43e0e0 including its exact source diagnostic and fatal path. Actual ARM-compiled C versus stock bounded effect oracles pass **10** core branch/recursive cases and **396** child cases covering all 128 event codes over three flag configurations plus callback/flag/active-input samples. Child effects are controlled at their ABIs in the core oracle; this is not full callback-runtime equivalence.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-event-core-round/receipt.json` passes **2,097 definitions, 774 unresolved mixed imports, zero duplicate strong**, SHA-256 `48d5be229333c123cad3d1ac035f960a3b5f0ea27943455a7e081e37f490ece4`. Five true code providers were added while the net unresolved count remained 774 due other connected symbols; no direct `audio_uart_lv_*event*` or `audio_uart_lv_*flag*` imports remain in this snapshot. Main still has extensive other code, data, tool/runtime and placement gates; source_complete stays false.

The next LV display path is now source-defined through native 0x440494. `display_lv_visible_area.c` reduces 0x4406c4 screen/layer membership, object and ancestor clipping, overflow expansion, and scrollbar path. `display_lv_visible_area_helpers.c` reduces area expansion 0x450b98 and scrollbar ancestor predicate 0x440a18. `display_lv_screen_layer_getters.c` reduces previous/top/system/bottom layer accessors 0x44fc90/0x44fcbe/0x44fcfc/0x44fd38 with their native offsets and log calls. `display_lv_scrollbar_clip.c` reduces 0x440494 inclusive-rectangle normalization plus recursive clip dispatcher 0x4403e6, retaining its parent-before-child order for flag bit1. Two direct imports were corrected to already selected exact providers: draw size 0x452dc8 and parent 0x44dca2. Actual compiled-C/stock bounded oracles pass **7** visible-area, **16** helper, **12** getter, and **6** null-object scrollbar clip cases. The active scrollbar child 0x440dda and scrollbar-mode getter 0x452dd8 remain genuine direct code imports; the six clip cases do not validate their non-null effects.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-scrollbar-clip-round/receipt.json` passes **2,106 definitions, 774 unresolved mixed imports, zero duplicate strong**, SHA-256 `025151e14be7b6384cd1e24d852b8ebefa224620ab590e97468f95b16bf6d7dc`. The selected LV root and display state refer to product live RAM 0x2006f548. Pinned LVGL's global initializer establishes generic library construction behavior, but current product-native startup evidence has not established placement, initialization order, or producer for this exact RAM cell, so it remains a typed external runtime contract. The 774 imports mix code, live RAM, ROM, and integration contracts, and cannot be read as 774 missing bodies. Main and the other five images remain source-incomplete; final link/layout, product configuration, physical peripherals and runtime equality are unproved.

Follow-on scrollbar source adds exact 0x452dd8 mode extraction from the object's spec-attribute word and the native 0x440dda transform dispatcher in `display_lv_scrollbar_transform.c`, including no-transform early return, percent-style pivot decoding, integer-scale reversal, and the 7-argument geometry effect. The mode getter's four bitfield outcomes and preceding six null-object scrollbar cases pass **10** actual compiled-C/stock comparisons. The larger transform body compiles with target `-Wall -Wextra -Werror` and links in Main; its style children and geometry transform effects have not yet received a connected native/compiled-C oracle, so its full behavioral qualification remains open. Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-scrollbar-transform-round/receipt.json` passes **2,108 definitions, 778 unresolved mixed imports, zero duplicate strong**, SHA-256 `5d15504d512626118a5c51cb828fb5ae91a0ab52fde2122bdc571c42126200a5`. The increase is six authentic style/geometry child contracts exposed by the full transform body, not regression by duplicate providers. Full source/runtime/image completion remains false.

The six newly exposed connected transform contracts are now source-defined. `display_lv_transform_style.c` implements native style property wrappers 0x43ef2a/0x43ef34/0x43ef3e and clamped scale wrappers 0x43f07e/0x43f08c over the already selected 0x44bdea property getter. `display_lv_transform_points.c` implements full native point-array transform 0x4513c8: pivot subtraction, scale-only, interpolated trig rotation, before/after scaling, and signed fixed-point shifts. `display_lv_trig.c` supplies the 91-entry named `sin0_90_table` initializer from pinned LVGL 9.3 `src/misc/lv_math.c` and native sin 0x4885f0; it is attributed source data, not an opaque stock byte array. Connected actual ARM-compiled C/stock comparisons pass **8** scrollbar transform effects under controlled property getter responses, **9** point transform cases including rotation/reverse scaling, and **360** direct trig angles (377 total). These controls do not prove all product style-property or hardware state configurations.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-lv-transform-children-round/receipt.json` passes **2,115 definitions, 772 unresolved mixed imports, zero duplicate strong**, SHA-256 `f7c7d3ae5155ade88bdaa2dbae17e3d9b6d397e4b612518c802e3ce4464189f4`. No `audio_uart_lv_*transform*`, scrollbar, or 0x4885f0 sine imports remain in that selected graph. Pinned LVGL `lv_global_init` zeroes generic `lv_global_t`, initializes display/input linked lists, and seeds style/layout/event fields; product startup/configuration still has no authenticated mapping proving the exact live root at RAM 0x2006f548 is that source-owned object with matching layout and initialization order. Keep that RAM cell typed external. Main and all six final source/layout/runtime/hardware gates remain open; the 772 mixed imports are not a body count.

A separate Audio/BLE-to-ring event provider is now C: `display_ring_event_task.c` reduces full native `Thread_SendEvtToRingTask` 0x4c543e with all three log-policy checks, authenticated source/module/function/format literals, and the real CMSIS thread-flags effect. The native prologue saves R0 but overwrites its stack slot with source line 374 on the extended-log branch; a five-level actual compiled-C/stock call/effect oracle found this return difference and the C now preserves it. The ring manager's thread pointer is read from live RAM 0x20004120+8; producer and initialization ordering remain typed external state. Coherent Main receipt `g2/build/c-firmware/20261011/peripherals-ring-event-round/receipt.json` passes **2,116 definitions, 772 unresolved mixed imports, zero duplicate strong**, SHA-256 `6e5cbc1da3b2cc7cacabca5d7dacb417c82b25a2636b40fb7e9d8b599c166227`. One true code import closed and one genuine live RAM contract exposed. Other Main source, product state, final layout and hardware gates remain open.

The ring thread pointer producer has now been authenticated and source-reduced. Stock literals at 0x4c5648 and 0x4c9c80 both address manager RAM 0x20004120. Native `thread_ring_create` 0x4c4da4 stores the `osThreadNew` result at +8; queue init 0x4c4d66 stores the `osMessageQueueNew(3,4,NULL)` result at +12; terminate 0x4c4dd0 clears +8 after the actual CMSIS termination call. `display_ring_task_producer.c` implements all three, retaining native interrupt-mask plus invalid-address store/infinite-loop allocation-failure behavior. Its CMSIS thread attributes are source-owned with an authenticated ROM 0x75b8a4 field layout: name `ring`, callback storage RAM 0x20072290/112 bytes, stack RAM 0x2036be40/4096 bytes, priority 46, TZ module 1. Three actual compiled-C/stock successful-state oracles pass, including normalized attribute fields and manager writes. The failure fault/MMIO behavior is statically represented but not executed in this bounded oracle.

`display_ring_task_entry.c` reduces native entry 0x4c4cec with authenticated start/queue/hooks/ready order, 0x00ffffff wait, notification loop, and failure logging. The two adjacent one-instruction hook bodies are source-empty because their actual stock entries are `bx lr`; deeper notification handler 0x4c507e remains a genuine separate body. `display_ring_task_sync.c` reduces native manager start/end transitions 0x4c9b86/0x4c9be2, including synchronization wait, all log policy branches, native saved-R0 return values, and event flag set from manager RAM 0x200040d8+0x1c. Ten actual compiled-C/stock controlled-child comparisons pass across five log levels for each transition. The initial task entry itself has target compilation/link but no connected looping runtime oracle yet.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-sync-round/receipt.json` passes **2,126 definitions, 776 unresolved mixed imports, zero duplicate strong**, SHA-256 `7adb4f33173c9b98eaff84c38ef5986bd6cfe35b2c5c1e29615dee62b2dd9533`. The live manager object and callback/stack RAM are explicit external storage contracts. The create body proves the producer write to +8, while the product lifecycle caller that invokes creation and the initial zero/placement contract are not yet authenticated. Ring notification handling, other source bodies, final image layout and hardware execution remain open.

The full 808-byte native ring notification dispatcher 0x4c507e is now source-defined in `display_ring_notify_event.c`. It handles message bit22, service discovery bit2, disconnect bit3, pairing bit4, heartbeat bit5, pair enable bit6, reconnect bit11, advertising bit8 and exit bit23 in stock order. Authenticated ROM strings and delayed callback addresses drive remove/re-enqueue intervals of 200, 500, 700 and 3000 ms where the original branches use them. It preserves repeated log-policy checks and the saved-R1 return word; callers do not depend on the return but the bounded oracle compares it. Actual compiled-C/stock **24** event-bit traces pass for log levels 0 and 7, including combined flags and normalized callback identities. This controls children at their native ABIs and does not prove each delayed callback's later effects.

Connected `display_ring_task_messages.c` reduces the native 252-byte queue drain 0x4c4de8 with IDs 2, 0x80, 0x400 and 0x1000, format diagnostics, packet lengths, and heap free on all dequeued messages. Six actual compiled-C/stock successful receive/dispatch/free cases pass. `display_ring_task_exit.c` reduces native 0x4c53a6: manager sync, queue deletion/zeroing, diagnostics, and the infinite `osDelay(UINT32_MAX)` loop; two actual compiled-C/stock cases compare present/absent queue effects through the first delay. `display_ring_task_sync.c` also provides its adjacent 0x4c9c3c event-set child. `display_ring_notify_callbacks.c` reduces four callback entries 0x47257c/0x472588/0x4a285c/0x4c5032 and the connected 0x472630 event-send wrapper, with genuine lower imports for their own effects.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-callback-round/receipt.json` passes **2,135 definitions, 784 unresolved mixed imports, zero duplicate strong**, SHA-256 `0f0a6ca3ad60c60c8f07fc8e05c726a6475eab46fac362425e81ce2a17d835fe`. The import increase exposes genuine packet/PHY/publish/pair/status children and live product data rather than duplicate providers. Ring manager live RAM 0x20004120 has a proven create/terminate producer for its thread pointer, but initial placement/zero and lifecycle dispatch into `thread_ring_create` remain unowned. Full ring descendant behavior, Main source, final layout and hardware gates remain open.

The connected ring packet/PHY chunk now source-defines native `APP_MasterSetPhyEvent` 0x4a2254, three packet constructors 0x472378/0x4723d6/0x4722d8, and `APP_BleRingSendDataMsg` 0x4c4b7e in `display_ring_phy_event.c`, `display_ring_packet_messages.c`, and `display_ring_ble_send_data.c`. The send body preserves the disconnected/zero handle gate, wait, 12-byte Cordio descriptor, allocation-failure notify, and stock log branches. Authenticated strings, 0xac message ID, state RAM 0x20074074, and the selected WSF alloc/send providers are explicit. Actual compiled ARM C versus stock comparisons pass 4 PHY, 10 packet and 10 send cases, including logging levels 0/7 and allocation failures. The packet tests control `APP_BleRingSendDataMsg`; the send tests control its WSF and semaphore children, so these are bounded effect proofs rather than an end-to-end BLE radio trace.

`display_ring_ble_tx_sync.c` source-defines native `threadBleWsfTakeTxReady` 0x4d0b36, `thread_ble_wsf_wait_tx_ready` 0x4d0b64 and `thread_ble_wsf_tx_complete_notify` 0x4d0c36, including the 20-iteration timeout, 10-tick poll/delay, elapsed tick log, and counted semaphore release. `display_ring_ble_sem_count.c` binds native osSemaphoreGetCount 0x449a0e to the already selected equivalent CMSIS FreeRTOS queue-count implementation at 0x449bc8. Ten bounded compiled-C/stock comparisons pass across acquire, timeout, missing handle, release and max-count paths. The native literal 0x4d0cdc locates the BLE WSF task descriptor at RAM 0x20004068, with semaphore handle at +0x14. Thread manager native 0x4c953e invokes the descriptor's offset-zero entry, and 0x4c963a reads its +8 thread handle for start, establishing a lifecycle edge. Its initial placement/copy and semaphore creation remain unowned typed data/source contracts.

Final coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-tx-sync-final-round/receipt.json` passes **2,144 definitions, 780 mixed unresolved imports, zero duplicate strong**, SHA-256 `9a398dbf733d1a3bfea860fac5d663a304725c17e6600bfbbd78068db865ed7e`. The connected direct code gap now includes publish-link-ready 0x4a271e and its ring owner/event children, while BLE WSF task state, ring handler state, packet templates, final placement, whole Main source and hardware validation remain open. Source completion for Main and for the full six-image firmware is false.

`display_ring_publish_link_ready.c` now reduces the complete native `APP_MasterPublishRingLinkReady` 0x4a271e and its one-call event bridge 0x4a153c. It preserves the already-published, nonconnected-state and absent active-connection exits, then performs the native flag writes, security-state update, owner-gated policy notify, UX/App event and diagnostics. Direct children 0x4b82e8, 0x4a2914, 0x4ac16c and 0x49f828 were already selected C providers and are reused. Actual compiled-C/stock effects pass **8** cases, including both log levels and owner/no-owner success paths. The four bytes at 0x20074f84/85/88/89 and master context pointer cell 0x200742fc remain typed external RAM. Native `_masterConnect` 0x4a02e8 demonstrably clears +88/+89 when opening a new connection; that is a runtime producer, not a proof of initial placement.

`display_ring_policy_success.c` reduces native `RING_ConnectPolicyNotifyConnectSuccessSoon` 0x49f646, including pending-byte clear, both delayed-callback removals, owner-gated 200 ms success scheduling and diagnostics. The two callback addresses authenticate to selected timeout 0x49f500 and success 0x4bc418 bodies. Actual compiled-C/stock effects pass **4** owner/log combinations. Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-publish-round/receipt.json` passes **2,147 definitions, 780 mixed unresolved imports, zero duplicate strong**, SHA-256 `cc1d6793c733081c52ee9d3e568ba2e76d6fe8a882f7bd61637518b88284e6f9`. The unchanged import count reflects newly explicit live product cells, including 0x20074f88, balancing code closure. BLE WSF descriptor RAM 0x20004068 has a manager call edge, but the retained native decompilation contains no authenticated semaphore-construction write at +0x14; its startup copy/placement remains unresolved. Main source, complete image layout and hardware validation remain open.

The next connected task transport round reduces native `ring_task_msg_send` 0x4c549c in `display_ring_task_msg_send.c`. The complete body validates null payload and queue, allocates length+8, writes the ID/length header, copies payload, puts the owned pointer into the CMSIS queue, signals the task on success, and frees on put failure. It reuses selected zero/copy/queue/flag/free providers and leaves native `file_heap_allocate` 0x474cd2 as the existing genuine allocator import. Ten actual compiled-C/stock cases pass across null, missing queue, allocation failure, put failure, successful dispatch, and log levels 0/7. This closes the shared transport import used by touch follow-up, status, and ring task callers.

`display_ring_mode_update.c`, `display_ring_pair_mode.c`, and `display_ring_heartbeat.c` reduce native 0x472362, 0x472546, and 0x472244. Their actual compiled-C/stock oracles pass **4** mode/pair and **2** heartbeat cases, comparing the 0x1000 task message's two payload bytes, 254-byte buffer-zero request, four transmitted packet bytes, log effects and selected hex dump call. Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-task-protocol-round/receipt.json` passes **2,151 definitions, 776 mixed unresolved imports, zero duplicate strong**, SHA-256 `3ea1cbc1bb7bb178f7617fa1f968bf7c1f06411e95ccf4542b8d942decbde121`. In the exact `audio_uart_ring_*` unresolved subset, one true code body remains (`audio_uart_ring_send_packet_472988`) and 18 product RAM/template/descriptor symbols remain. Other Main interfaces outside this prefix remain among the 776 mixed imports; these are not 776 missing bodies. No authenticated producer for BLE WSF descriptor+0x14 semaphore was found in the retained native call/decomp subset, so it stays a typed runtime contract. Final image layout and hardware execution remain unverified.

`display_ring_send_packet.c` now reduces the full native `RING_CmdPackageParse` 0x472988 dispatcher. Its branches cover touch update 0x61, publish/ack 0x85, touch time 0x8a, battery 0x8b, wear 0x8c, touch error/heartbeat 0x94, and invalid glasses MAC 0x96. It preserves the authenticated delayed callbacks 0x4bc418/0x4a285c and 0x4c4fe4/0x4c4ee4, owner-gated publish or notify, 100/500 ms rescheduling, reverse MAC diagnostic and unpair call. Eleven actual compiled ARM C/stock branch traces pass. The selected `audio_ble_master_success_delayed` is native `PB_TxEncodeNotifyRingConnectInfo` 0x4bc418 and is reused for the 0x85 branch rather than adding an alias import.

`display_ring_send_packet_children.c` reduces six complete native children: HID touch ack 0x47263c, throttled touch report 0x47269e, battery report 0x4727aa, wear status 0x4728b2, target address/name copy 0x4a2190, and disable-touch callback 0x4c4fe4. The target name copies the authenticated seven bytes at ROM 0x78c9cc; battery message bytes use the authenticated zero high word at ROM 0x78e464. Fifteen actual compiled-C/stock cases pass across touch event modes, throttling, HID ack, battery success/failure, wear transitions, both target-copy branches and callback logging. Deeper genuine code imports now exposed are touch event 0x4c5916, wear persistence 0x48eb32, and master unpair cleanup 0x4a2c9c, plus three live RAM cells 0x20074900/904 and 0x2007500c. The wear-persistence native call uses authenticated key 0x60102; it is not a fabricated storage success.

Final coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-dispatch-final-round/receipt.json` passes **2,158 definitions, 781 mixed unresolved imports, zero duplicate strong**, SHA-256 `db376fded52536e49fb9b38afd0b7091eb833f0cf86cf665a438b26ce5fb21ce`. The original direct ring packet code frontier is closed, but the newly exposed three code children, 21 ring-prefixed data contracts, broader Main source, placement and hardware remain incomplete. The import increase records these real dependencies and is not a regression in defined body count.

The next connected source round defines native `INPM_EventSend` 0x4c5916 in `display_ring_touch_event.c` and persistence gateway 0x48eb32 in `display_ring_wear_persist.c`. Two actual compiled ARM C/stock touch event comparisons pass for the bytes the original initializes and six actual compiled ARM C/stock wear cases pass for clamping, initialization, submit and wake gating. The stock 12-byte touch packet writes bytes 0..1, 4..9 only; bytes 2..3 and 10..11 are ambient stack and cannot be claimed equal as portable source data. The persistence initializer/submit/wake children 0x48eac8/0x48ea66/0x47dd92 remain authentic code contracts; its queue and flags are product RAM contracts.

`display_ring_unpair_cleanup.c` source-defines native `APP_MasterCleanupRingUnpair` 0x4a2c9c with its five delayed removals, auth and retry reset, target clear, hand-state publication/commit calls, role status, pair-record removal, security clear and three final connection-state branches. It reuses selected actual 0x4a23ac and 0x4a01fc bodies rather than behavior aliases. `display_ble_master_security_clear.c` reduces native `AppMasterSecClearAddr` 0x4d8ff6; its literal at 0x4d9128 authenticates the seven-byte RAM cell at 0x200003d8 and the final 0xff type byte. Both compile for ARM `-O2 -Wall -Wextra -Werror`; the unpair and security full effect trees have static native correspondence, with no connected execution oracle yet. Genuine newly exposed code children include input event send 0x464d1c, persistence 0x48eac8/0x48ea66/0x47dd92, and hand publish/commit 0x4661a6/0x466016. Live RAM initializers, final placement, full Main source and hardware remain open.

Coherent target `g2/build/c-firmware/20261011/peripherals-ring-lower-final-round/receipt.json` passes **2,162 definitions, 790 mixed unresolved imports, zero duplicate strong**, SHA-256 `7f56f72434b5d25c6fd9b38404a8364b5b619cee8cdd3c206db71c2224c9cb9c`. The rise from 781 imports is the explicit native child and product-data frontier, not a whole-image completeness metric.

The next lower pass defines native `SendDataToBoth` 0x464d1c in `display_input_event_send.c`: two allocations, 12-byte descriptor, eight-byte sync header, payload copy, 2000-tick queue put, bit-2 wake on success and both failure frees. Five actual compiled ARM C/stock queue and ownership cases pass, including missing queue, both allocation failures, success, and queue-put failure. It binds selected allocator/free/queue/event providers; queue and event pointer cells RAM 0x200749cc/0x20074b10 remain external.

`display_ring_persist_notify.c` and `display_ring_persist_event_set.c` reduce native 0x47dd92 and 0x47dd62. Native 0x47dd92 reads a 32-bit event object at 0x20074acc, clears a 32-bit pending word at 0x20074ad0 and invokes the next event set body. The latter uses the selected 0x443484 wake predicate, selected bit-8 event signal on failure, and preserves 0x47e7b0 as a genuine lower contract. The persistence initialize/submit 0x48eac8/0x48ea66 remained open at this snapshot; their subsequent native ABI resolution and C bodies are recorded below.

The hand-state chain now defines native 0x4661a6 publish, 0x466016 checksum commit, 0x49acd4 CRC16 and 0x448e34 mismatch signal in `display_ring_hand_publish.c`, `display_ring_hand_commit.c`, `display_ring_hand_checksum.c`, and `display_ring_hand_mismatch.c`. Actual compiled ARM C/stock publish effects pass for both role values, including its 48-byte packet layout and five-argument peer send. The CRC C matches all 256 authenticated native ROM table entries at 0x6c0b50 plus four data vectors; the table corresponds to polynomial 0x1021 and seed 0xffff when null. Security clear 0x4d8ff6 passes three actual compiled ARM C/stock seven-byte cases. The hand record RAM 0x200736d4 and snapshot source struct RAM 0x200036fc are typed live data contracts; producer/placement is revisited below.

`display_ring_persist_buffer.c` defines native ring word read/write/size 0x48e8e2/0x48e8d4/0x48e8f0, validator 0x48e900 and reset 0x48e99c. Seven actual compiled ARM C/stock validator states pass, covering empty, one valid record, invalid header, invalid magic/alignment and overfull span. The ring storage RAM 0x200761f4 and six-word metadata RAM 0x200771f4 remain live product data. Coherent target `g2/build/c-firmware/20261011/peripherals-ring-deep-children-round/receipt.json` passes **2,174 definitions, 793 mixed unresolved imports, zero duplicate strong**, SHA-256 `cde29ebb5607907ee4f4bf5fc6deb8a831996710da2123f76af0c374dcc39a52`; `source_complete` remains false. The exact ring-local true code frontier is initialize 0x48eac8, submit 0x48ea66 and resident event op 0x47e7b0. Broader Main source, product data ownership, final layout and live hardware remain open.

Native disassembly resolved the apparent fourth-register ambiguity in 0x48ea66: entry R3 is only saved/restored. At 0x48eaa0 and 0x48eab8 it explicitly loads R3 from the clock-derived value before append. `display_ring_persist_initialize.c`, `display_ring_persist_submit.c`, and `display_ring_persist_append.c` define queue initialization, early-time preface, and circular record eviction/write without an invented timestamp. `display_ring_persist_clock.c` and `display_ring_persist_metadata.c` define timing and metadata wrappers with RTC/kernel/division/parser lower calls explicit. The native critical mask helper 0x47dce4 is exactly `MRS PRIMASK; CPSID i`; C uses those instructions and the native restore `MSR PRIMASK`. Actual compiled ARM C/stock controlled-child cases pass **4** initialize, **3** submit, and **3** append, including eviction and physical ring wrap. The metadata reader pins the authenticated ROM version string `2.2.6.10` at 0x78c740. These bounded tests do not prove lower RTC/parser or persistent storage hardware effects.

Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-persist-full-round/receipt.json` passes **2,181 definitions, 800 mixed unresolved imports, zero duplicate strong**, SHA-256 `3415373c7b1fb4f5dca5268bc9aa654633e3c0be890bceb501d721a99f43b7d8`, `source_complete=false`. Ring-local unresolved true code now includes kernel state, RTC refresh/snapshot, 64-bit divide, decimal parser, and event operation 0x47e7b0, plus live product RAM. The event operation reads an unusual fifth stack argument in its running-kernel branch despite four explicit register arguments from 0x47dd62; no fixed value has been assigned to that stack word. Main full source, data placement, and hardware execution remain open.

The native settings-manager call graph proves a hand-record producer: `DEV_ResourceInit` 0x4c632c calls `svc_universal_setting_init` 0x466660, which zeroes only the first 0x2c bytes of RAM record 0x200736d4, copies three settings-manager source records from struct base RAM 0x200036fc at pointer fields +0x14/+0x0c/+0x10, logs, and publishes. `display_ring_hand_initialize.c` implements this complete body. One actual compiled ARM C/stock connected comparison passes and confirms the final four record bytes remain unchanged rather than being fabricated as zeros. The settings-manager struct at 0x200036fc was corrected from a pointer-cell interpretation after the controlled oracle exposed a native memory-address mismatch. Its three source pointer fields remain live storage contracts.

`display_device_resource_init.c` defines full native `DEV_ResourceInit` 0x4c632c, including battery/clock/BLE/settings/hand call order, 50-by-8 queue creation at manager+0x0c, one-shot timer construction with authenticated 44-byte control block and `device_mgr_timer` name, and 1000-tick start on success. Four actual compiled ARM C/stock cases pass for queue success/failure and timer absent/failure/preexisting states. The battery/clock/BLE initializer and timer callback descendants remain authentic separate code contracts. Coherent target `g2/build/c-firmware/20261011/peripherals-device-resource-round/receipt.json` passes **2,183 definitions, 807 mixed unresolved imports, zero duplicate strong**, SHA-256 `dd72df949b346b83ecf968b28638c6a14b4850bfdff7e5363eec4312018d16ac`, `source_complete=false`. The hand-record runtime producer is now source-owned; initial settings-manager source pointers, product RAM placement, broader Main bodies, and hardware execution remain open.

The next device-init pass reduces actual native timer callback 0x4c661c, CHG battery sync 0x4acf7c, BoxDetect constructor 0x4ac02a, ring battery callback wrapper/init 0x4ff8d4/0x500380, and BoxDetect callbacks 0x4ac016/0x4ac020. Target ARM compilation passes with `-Wall -Wextra -Werror`; actual ARM C/stock controlled comparisons pass one timer callback, two battery sync, four BoxDetect, and four connected `DEV_ResourceInit` cases. The device timer packet has only its first four bytes native-defined; the remaining four are ambient stack and are not asserted equal. Queue/timer handles, callback manager, record bytes and charger flags are typed live RAM at their authenticated addresses. Coherent Main target `g2/build/c-firmware/20261011/peripherals-device-children-round/receipt.json` passes **2,190 definitions, 816 mixed unresolved imports, zero duplicate strong**, SHA-256 `904bc1f74aa5906e37150f9f1eb7a98cc5a378eb3958b6c924fb461b0b73402a`.

The RTC/kernel pass reduces full native snapshot 0x4d3554, CMSIS `osKernelGetState` 0x44906c, unsigned 64-bit quotient helper 0x47cc60, and RTC refresh 0x44a1ea. The latter connects the already-selected calendar reader 0x4d3c0a to selected epoch converter 0x44a108. Actual compiled ARM C/stock comparisons pass **4 snapshot**, **9 kernel-state**, **30 division**, and **2 refresh** cases. The snapshot preserves the zero-cache hardware read from MMIO 0x4000885c and writes the 15 native-defined output bytes. The divide helper uses a restoring algorithm, preserves the native zero-divisor dividend result, and introduces no compiler division import. Coherent Main target `g2/build/c-firmware/20261011/peripherals-rtc-kernel-round/receipt.json` passes **2,194 definitions, 814 mixed unresolved imports, zero duplicate strong**, SHA-256 `956ef92e2b1324d9b9c2e918d48864981446c5fbd8e23a5b684cc587232ac359`.

Direct disassembly of native persistence event operation 0x47e7b0 resolves the previously reported fifth-argument uncertainty: caller 0x47dd62 explicitly stores zero at `[SP]` before its BL, which is the callee's entry fifth argument at `[SP+0x20]` after the eight-register push. `display_ring_persist_event_operation.c` implements the complete 12-byte queue packet, signed priority split, scheduler-gated fifth-argument wait, ISR woken-pointer path, queue return propagation and native null-event fault after the selected interrupt-mask operation. `display_ring_persist_event_set.c` now passes explicit zero as the fifth argument. Twelve actual compiled ARM C/stock queue and return comparisons pass, including absent queue, task, ISR, scheduler 1/2 and negative priority. The null event branch is statically matched to the native fault path and excluded from the bounded execution oracle. Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-event-round/receipt.json` passes **2,195 definitions, 814 mixed unresolved imports, zero duplicate strong**, SHA-256 `a523ad9a3c97524137fbfdf80084cdddd241e301f09b54f57b8815a13ab02235`, `source_complete=false`. The remaining ring-local genuine code contract is decimal parser 0x48d874/0x48d724; authenticated live RAM includes the event queue handle 0x20074ab0, kernel flag 0x20074384 and RTC cache 0x200742ac. Broader Main source, source-owned RAM initialization, image layout and hardware execution remain open.

`display_ring_unsigned_parser.c` now reduces native parser wrapper 0x48d874 and core 0x48d724, including whitespace/sign, base 0 and 2..36, optional hexadecimal prefix, leading zeroes, end pointer, negative wrap and range overflow. The ROM base threshold table at 0x6f1208 was authenticated against its digit widths; source computes the equivalent threshold without embedding an opaque table. `display_ring_locale_dispatch.c` reduces native character wrappers 0x4d58ae/0x4d58c2 as actual function-pointer calls through the locale vtable at RAM 0x200044c0 offsets 0x20/0x28, plus native range-errno write 0x439cb2 to RAM 0x20074f14. Actual compiled ARM C/stock parser comparisons pass **100** deterministic ASCII-locale cases including bases, invalid strings, signs and overflow. The runtime locale vtable and errno cell remain typed product RAM contracts; arbitrary locale callback behavior was not executed in this oracle. Coherent Main target `g2/build/c-firmware/20261011/peripherals-ring-parser-round/receipt.json` passes **2,199 definitions, 815 mixed unresolved imports, zero duplicate strong**, SHA-256 `f6f8f912c439278b8fe60f3d9d2235953ba7bbfb50582915658c5b0ee70ba1c0`, `source_complete=false`. The ring-local genuine code imports exposed by this connected source path are now closed; ring product RAM/template/descriptor sources, broader Main code/data, final layout and hardware execution remain open.

The subsequent Cordio discovery chunk reduces full native `appDiscStart` 0x531d60, `appDiscCfgStart` 0x531bd4, `AppDiscReadDatabaseHash` 0x5336e0 and byte comparator 0x44b610 in `display_ble_service_discovery_*.c`. The authenticated 0x78f54e database-hash UUID is represented as two source bytes, while the service dispatch pointer at RAM 0x20074348 and three per-connection rows at 0x200733fc remain typed live data. The sources preserve trace-level gates, profile row status transitions, connection dispatch 3/6/7, database hash request and selected 0x439be4 copy. Actual compiled ARM C/stock comparisons pass **12 start** and **10 child** cases across invalid connection, log levels, active row, callback, copy and request branches. Coherent Main `peripherals-ble-discovery-children-round` passes **2,205 definitions, 815 mixed unresolved imports, zero duplicate strong**, SHA-256 `3cb9976282dc40fb135663ba0b4aca5923d755e07fddffb7a2dcde117170fdec`.

The ATT descendants now reduce native `AttcReadByTypeReq` 0x56c4ee, `attMsgAlloc` 0x4b50ae, `attcSendMsg` 0x4b5640, `attcExecCallback` 0x531ad6, `attExecCallback` 0x4b5074 and `attcCcbByConnId` 0x531820 in `display_ble_att*.c`. The message assembly writes only stock-defined bytes and retains ambient allocation bytes; queue success and error ownership use selected WSF alloc/send/free/lock providers. The CCB lookup reuses the already-selected `audio_ble_attc_state` storage and `AttcInit` producer at RAM 0x2006f904, rather than introducing a second alias for the same region. Actual compiled ARM C/stock comparisons pass **2 read-by-type**, **6 send**, **4 callback**, and **6 CCB lookup** cases; null, blocked, oversize, allocation failure, queue success, inactive connection and diagnostic paths are represented. Coherent Main `g2/build/c-firmware/20261011/peripherals-ble-att-final-round/receipt.json` passes **2,209 definitions, 814 mixed unresolved imports, zero duplicate strong**, SHA-256 `ff0354936cd7d883d41118f611a1b8fc1be295f4ec874c334cb8b22b0064d86d`, `source_complete=false`. The connected discovery/ATT true code imports are closed; the native ATT client table ROM contract and service dispatch RAM0x20074348 remain unresolved, as do the broader Main code/data graph, final layout and live hardware gates.

### Cordio discovery connection events (2026-10-11)

`display_ble_discovery_events.c` adds the complete native dispatcher at 0x5322bc
and its five event children at 0x5320c2, 0x532124, 0x532174, 0x53228e,
and 0x53223c. The 0x5320c2 close path calls the selected zero-fill provider,
not memcpy; disassembly at 0x53210e also establishes that 0x20074360 holds a
pointer whose first bytes select the discovery branch. The selected profile
initializer 0x535488 already produces this cell as
`audio_ble_profile_dispatch_slot`, pointing to the authenticated ROM entry
0x5fa056; the event source now binds that producer directly. The native 0x532174 active-record
query and connection-record table remain explicit imported contracts. The
startup reset producer for the 0x200733fc rows was already selected at 0x532e52;
the row storage placement and dispatch callback producer remain unproven.

Focused actual compiled ARM C/native Unicorn comparison:
`verify_ble_discovery_events_native.py` PASS for two defined-input close/resume
cases, comparing row mutations and lower call arguments. Other event branches,
diagnostic paths, and product-state initialization have static native evidence
but no runtime equivalence receipt yet. Qualified target compilation and the
coherent Main experimental relocatable link PASS at
`g2/build/c-firmware/20261011/peripherals-discovery-events-round/receipt.json`:
2215 defined, 820 mixed unresolved, zero duplicate strong providers, candidate
SHA-256 `d0696835cdec5a3c4f24b113df75cc75524da2a949eaa753340f88ac2a33c086`.
Source completeness remains false. New imported code descendants include
`audio_ble_dm_conn_set_idle`, `audio_ble_discovery_config_resume`,
`audio_ble_connection_is_active_4bad26`, and
`audio_ble_pair_record_attach`; live table/callback cells remain data contracts.

Follow-on selected source adds `display_ble_discovery_record_attach.c` for
native 0x47b48e (42-byte descriptor copy, privacy rewrite, record validation)
and `display_ble_discovery_config_next.c` for native 0x56c3a6/0x56beb6
(descriptor/handle walk and ATT read/write request dispatch). The latter is
target compiled and statically matched to native index, count, handle, and
request branches; its connected request effects still need runtime comparison.
Latest coherent Main receipt:
`g2/build/c-firmware/20261011/peripherals-discovery-config-round/receipt.json`,
2218 defined, 820 mixed unresolved, zero duplicate strong, candidate SHA-256
`366ab4cde26f96b8b23cad3098619d5364fec1be4ebc3c677cf2577fd42f3dec`.
The new direct ATT read/write request imports are genuine native descendants.

The next four connected native providers are implemented in
`display_ble_att_requests.c` and `display_ble_discovery_conn_state.c`:
`AttcReadReq` 0x4b575a, `AttcWriteReq` 0x4b579c, the app connection-state
query 0x4bad26, and `DmConnSetIdle` 0x4b71dc. The request bodies construct
the native ATT headers and invoke the selected allocator/send path. The
connection-state body uses the actual 0x200717b0 row stride and the DM idle
mask at RAM 0x200712a4. Product RAM remains imported. The invalid-connection
and trace paths have source-backed literal strings/branches but no focused
runtime trace comparison yet. The connected config-next walk has actual
compiled ARM C/native Unicorn comparison PASS for four cases (empty, skipped,
read, write), including request call arguments and index effects, in
`verify_ble_discovery_config_next_native.py`.

Coherent target receipt:
`g2/build/c-firmware/20261011/peripherals-discovery-descendants-round/receipt.json`,
2222 defined, 817 mixed unresolved, zero duplicate strong, SHA-256
`9d01fdb11e6ea053726d4175d2ea9d0e2a9b932454f88ab8ce46a2b9b010e87b`.
No full Main image or live BLE execution claim follows from this build.

After binding the selected 0x535488 profile initializer producer for RAM
0x20074360, the focused discovery close/resume oracle remains PASS 2. The
corrected coherent receipt is
`g2/build/c-firmware/20261011/peripherals-discovery-mode-corrected-round/receipt.json`:
2222 defined, 816 mixed unresolved, zero duplicate strong, SHA-256
`0565bb69d58b82e8a638f6fdd251b98ff9796adc95305c15c9202ee5a63bb05c`.

### Connected Cordio characteristic and descriptor walk

Additional complete native bodies are selected from pinned Cordio/native
operations: `AttcDiscCharStart` 0x56c1b8, `AttcDiscConfigCmpl` 0x56c396,
`AttcDiscCharCmpl` 0x56c1f8, `attcDiscProcChar` 0x56be30,
`attcDiscProcDesc` 0x56ba82, `attcDiscDescriptors` 0x56b86a,
`attcDiscVerify` 0x56b834, and `AttcFindInfoReq` 0x4b571e. Sources are
`display_ble_discovery_char_config.c`, `display_ble_discovery_char_complete.c`,
`display_ble_discovery_parse.c`, `display_ble_discovery_descriptors.c`, and
`display_ble_att_requests.c`. The characteristic UUID is the authenticated
0x2803 pair at ROM 0x78f53e. The code retains source-owned handles,
descriptor traversal, error statuses, buffer zeroing, and ATT request effects;
two deeper parse helpers remain genuine imports.

Actual compiled ARM C/native Unicorn comparison PASS 2 for characteristic
start/config completion (`verify_ble_discovery_char_config_native.py`) and
PASS 3 for empty/required-missing/find descriptor transitions
(`verify_ble_discovery_descriptors_native.py`). Characteristic completion's
diagnostic branches and parse helper effects remain static qualified only.
Latest coherent Main target receipt
`g2/build/c-firmware/20261011/peripherals-discovery-parser-descriptors-round/receipt.json`
passes with 2230 defined, 818 mixed unresolved, zero duplicate strong,
SHA-256 `f0453b9a98e75cb9c737789ada35134de820d758f01a644e4ab363bc556f86fc`.
Full source, product data placement, and device execution remain incomplete.

The connected parser children are further reduced in
`display_ble_discovery_desc_pair.c` and
`display_ble_discovery_char_decl.c`: native `attcDiscProcDescPair` 0x56b8fa,
`attcUuidCmp` 0x56b7ec, `attUuidCmp16to128` 0x4b5014, and
`attcDiscProcCharDecl` 0x56bb1c. The native mutable 128-bit UUID template at
RAM 0x2000044c remains a typed data contract. Descriptor and characteristic
handle writes, pending-next state, UUID matching, and source-backed log paths
are represented in C. Actual compiled ARM C/native PASS 2 for defined-input
matching descriptor and characteristic transitions in
`verify_ble_discovery_pair_decl_native.py`; other logging and malformed packet
paths remain untested. The coherent target receipt
`g2/build/c-firmware/20261011/peripherals-discovery-decl-round/receipt.json`
passes 2234 defined, 817 mixed unresolved, zero duplicate strong, SHA-256
`63b7e5bbe40d5d3ce1703cccf126eba3221055fe9810f8cf5b00922948fe884f`.
Direct parser code children are now source-defined, while whole discovery event
processing 0x532924 and full service-completion 0x56bf32 remain larger genuine
native parents. RAM row/table/callback placement and startup ownership remain
unproven; the selected 0x532e52 reset is the only established row producer.

`display_ble_discovery_restart.c` reduces native
`appDiscRestartDiscovery` 0x531f20: invalid-connection diagnostics, four row
field resets, buffer zero/record persistence, stage-2 pending flag, and
profile-mode restart dispatch. It binds the already selected 0x535488 profile
dispatch pointer cell. Actual compiled ARM C/native PASS 4 for valid stage,
mode, and already-closed row transitions in
`verify_ble_discovery_restart_native.py`. The coherent target receipt
`g2/build/c-firmware/20261011/peripherals-discovery-restart-round/receipt.json`
passes with 2236 defined, 817 mixed unresolved, zero duplicate strong,
SHA-256 `e03cf708c78f5b268cc733bbcfe9f637919dd112c6adb1fa36e598a7ff802db0`.
Product row/table/callback placement remains an explicit image data contract.

`display_ble_discovery_process.c` reduces the full native
`AppDiscProcAttMsg` parent 0x532924 across discovery stages 3, 1, and 2:
database-hash comparison and pair record, service/characteristic/configuration
completion, security wait, recovery, status dispatch and logging. The native
0x56c396 configuration-complete wrapper was corrected to return its child's
R0 status, which the parent consumes; the focused characteristic/config oracle
now compares this return. Actual compiled ARM C/native parent comparison
PASS 4 for stage-3 failure, successful service handoff, config restart, and
config failure in `verify_ble_discovery_process_native.py`. Diagnostic printing
and pair creation have newly exposed genuine code imports, and broader
payload/status branches remain outside that bounded runtime receipt. Coherent
Main target `g2/build/c-firmware/20261011/peripherals-discovery-process-round/receipt.json`
passes with 2237 defined, 822 mixed unresolved, zero duplicate strong,
SHA-256 `3bfdb45a7a846537b7b2e6b5ccd3e6f39407f69b7b00b6448a79e623afb97611`.
Compilation does not settle product RAM/ROM ownership, whole image placement,
or live BLE operation.

`display_ble_discovery_pair_children.c` reduces native `DmConnSecLevel`
0x4b71b2 and the 0x47b3ae pair-name update. `display_ble_pair_record_create.c`
reduces `AppDbNewRecord` 0x47a71c and oldest-record selection 0x47a6b4 with
real privacy-list eviction, table clearing, timestamp, address, and role
effects. Actual compiled ARM C/native record creation comparison passes two
bounded free-slot and saturated-unbonded cases in
`verify_ble_pair_record_create_native.py`; bonded-oldest eviction and privacy
hardware effects remain untested. The coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-discovery-pair-create-round/receipt.json`
passes with 2241 defined, 819 mixed unresolved, zero duplicate strong,
SHA-256 `de94667221965f91984af9c7e2c15adf3311c78a1cd41042f61d44d62935fc6a`.

`display_ble_discovery_print.c` reduces native `appDiscPrintCharInfo`
0x5322f6 and `appDiscPrintDescInfo` 0x532644 across UUID16/128, all seven
characteristic-property bits, and descriptor families. Text and source tags
come from authenticated stock literal pointers. ARM target compilation and
coherent Main link pass with 2243 defined, 817 mixed unresolved, zero duplicate
strong, SHA-256 `9891e2c24a5272f01ce2fc5725b553c0e5b23aaac1a422364eaf152fbe436e87`
at `g2/build/c-firmware/20261011/peripherals-discovery-print-round/receipt.json`.
Variadic compressed-log runtime effects have static source evidence only;
there is no all-format actual-C/native equivalence or hardware claim. The
discovery row, connection table, pair rows, and callback storage are typed
live external RAM contracts pending whole-image producer and placement proof.

`display_ble_smp_pairing.c` reduces native `smpProcPairing` 0x56e6e0 with
the registered SMP product configuration pointer as a typed live contract,
including IO-capability, secure-connection, authentication, and key-size
decisions. Actual compiled ARM C/native comparison passes three no-dispatch
cases in `verify_ble_smp_pairing_native.py`; `smpSmExecute` event paths are
source-derived but not runtime-qualified yet. `display_ble_fast_mode.c` now
passes the already selected native `_connectParamReq` 0x47761c function as the
delayed callback directly instead of importing a second name for that same
original address. The coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-smp-pairing-round/receipt.json`
passes with 2244 defined, 816 mixed unresolved, zero duplicate strong,
SHA-256 `725058694b2f6d0addb886e307d30d58f20e39d7c823acb6c060d83a101da773`.

`display_ble_smp_dm_callback.c` reduces native `smpDmConnCback` 0x537502,
including open-event role/state setup and close-event failure count, synthetic
state-machine message, connection reset, and queued-message release.
`display_ble_smp_resume.c` reduces native `smpResumeAttemptsState` 0x53749c,
including legacy/secure state and timeout timer scheduling. These units have
authenticated native static mapping and qualified target compilation; their
complete callback/timer effects have not yet had an actual-C/native runtime
comparison. The latest coherent Main target receipt
`g2/build/c-firmware/20261011/peripherals-smp-resume-round/receipt.json`
passes with 2246 defined, 818 mixed unresolved, zero duplicate strong,
SHA-256 `953493f6be6af979d65eda4034cc4973bc7df9dff4f767ba0fd63bc44922e22b`.
Fresh SMP code frontier: `SmpDbGetFailureCount` 0x54257c,
`SmpDbSetFailureCount` 0x542418, `SmpDbGetPairingDisabledTime` 0x5422c4,
and table-driven `smpSmExecute` 0x56ee62. The first three use selected
`smpDbGetRecord`; the state machine depends on source-owned table pointers and
action callbacks. Main's 818 unresolved entries are mixed code, live RAM,
resident ROM and layout contracts, so they are not 818 unimplemented bodies.

`display_ble_smp_failure_state.c` now reduces the three DB state bodies:
`SmpDbGetPairingDisabledTime` 0x5422c4, `SmpDbSetFailureCount` 0x542418,
and `SmpDbGetFailureCount` 0x54257c. The record reads/writes and nonzero-count
timestamp copy use selected `smpDbGetRecord` and the authenticated live
registration slot. Their INFO diagnostics retain stock source/function/format
strings and trace gating. ARM target compilation and coherent Main link pass
with 2249 defined, 815 mixed unresolved, zero duplicate strong, SHA-256
`f7687dd8e6339e649797964f1950f35a32c7aa1acc248f0cd5c0bfd86300c64a`
at `g2/build/c-firmware/20261011/peripherals-smp-failure-round/receipt.json`.
Trace routing and actual record effects await connected compiled-C/native
runtime qualification. The remaining SMP state-machine body 0x56ee62 includes
table-driven dispatch and genuine source-owned table/action contracts.

`display_ble_smp_sm_execute.c` reduces native `smpSmExecute` 0x56ee62:
numeric/named trace selection, role-specific transition descriptor, per-state
row scan, fallback row, state write, and action-vector dispatch. The selected
`SmpiInit`/`SmprInit` families already install the descriptor pointers;
their ROM table objects and action callbacks remain authentic typed imports.
Actual compiled ARM C/native comparison passes two controlled table cases,
matched transition/action and fallback/no action, in
`verify_ble_smp_execute_native.py`. This bounds core dispatch only; product
transition tables, all actions and trace formatting are not runtime-qualified.
Coherent Main target receipt
`g2/build/c-firmware/20261011/peripherals-smp-execute-round/receipt.json`
passes with 2250 defined, 816 mixed unresolved, zero duplicate strong,
SHA-256 `0f1103b63e283a532e8e1264b0f981e812b3608b1974ea7024de854fab429139`.

`display_ble_smp_strings.c` and `display_ble_smp_state_strings.c` reduce
native `smpEventStr` 0x56d31e, `smpStateStr` 0x56d454,
`smpiStateStr` 0x537f24, and `smprStateStr` 0x538114. Event and state names
are source-owned strings read from authenticated stock literal pointer cells;
the role switch reads the selected SMP handler-state storage. Actual compiled
ARM C/native string results match for all 256 byte inputs for the three direct
mapping routines (768 cases) in `verify_ble_smp_strings_native.py`.
Coherent Main target receipt
`g2/build/c-firmware/20261011/peripherals-smp-strings-round/receipt.json`
passes with 2254 defined, 814 mixed unresolved, zero duplicate strong,
SHA-256 `2f1cf5e6fbe5b7a8ee2e8a516d748a23c5b80d3f1fb66265aa39914a46d1c32a`.
The SMP state-machine callback/data graph and whole Main placement remain
open; these exact string mappings do not establish BLE hardware operation.

`display_ble_smp_l2c_control.c` and `display_ble_smp_state_idle.c` reduce
native `smpL2cCtrlCback` 0x537444 and `smpStateIdle` 0x537bb8. Connected
credit/closed transitions update CCB, release a pending packet through the
genuine `smpSendPkt` child, and trigger state-machine event 0x0c when active.
Actual compiled ARM C/native comparison passes two credit transitions with
no pending packet in `verify_ble_smp_l2c_control_native.py`; pending-packet
send and state-machine action execution are untested here. Coherent Main
receipt `g2/build/c-firmware/20261011/peripherals-smp-l2c-round/receipt.json`
passes with 2256 defined, 814 mixed unresolved, zero duplicate strong,
SHA-256 `10fdf5bc3433024bd129e93e0449b56f415636baed796a3398377499323ce582`.
The newly exposed `smpSendPkt` path carries native inherited registers into
`L2cDataReq`; that ABI needs separate proof before importing or implementing
the child as a fully equivalent provider.

The SMP packet ABI is now resolved from native Thumb instructions:
0x537ba4–0x537bb2 explicitly loads R0=6, R1=CCB handle, R2=packet-size table
entry, and R3=packet before BL 0x530bbc. `L2cDataReq` 0x530bbc reads only
these four arguments and writes the 8-byte ACL/L2CAP header; extra arguments
shown by Ghidra are inherited register artifacts. `display_ble_smp_packet_send.c`
reduces `smpSendPkt` 0x537a5a, `L2cDataReq`, and the authenticated 16-byte
SMP packet-size table at ROM 0x7890c0 as source-owned typed C data. Exact
`smpSendPkt` warning string and source role come from stock literal pointers.
Actual compiled ARM C/native comparison passes send and pending-queue cases
in `verify_ble_smp_packet_send_native.py`. Coherent target receipt
`g2/build/c-firmware/20261011/peripherals-smp-send-round/receipt.json` passes
with 2259 defined, 814 mixed unresolved, zero duplicate strong,
SHA-256 `a3f90e37fcf5d9cfbd1dd496bff42f67d0e021cf3db8d174db85185e13351ef2`.

`display_ble_hci_acl_send.c` and `display_ble_hci_acl_queue_count.c` reduce
native `HciSendAclData` 0x52ad04 and `WsfQueueCount` 0x538cf6. The HCI body
uses the selected connection lookup, WSF enqueue/critical-section providers,
buffer-size provider and TxReady, plus the live HCI stack callback slot whose
producer is already selected. Actual compiled ARM C/native comparison passes
missing-connection/free and connected queue/fragment-counter effects in
`verify_ble_hci_acl_send_native.py`; live controller transmission and callback
threshold branches remain outside that receipt. Coherent Main target
`g2/build/c-firmware/20261011/peripherals-smp-hci-send-round/receipt.json`
passes with 2261 defined, 813 mixed unresolved, zero duplicate strong,
SHA-256 `d0a9c7579d57f1d9c86f1ab27b47eb306e40b98419890b3f597d03b6b77e28e3`.
Whole Main source, product RAM placement and hardware operation remain open.

`display_ble_smp_ccb_handle.c` reduces native `DmConnIdByHandle` 0x4b6e96
and `smpCcbByHandle` 0x5375c8 using selected three-row DM records and SMP
CCB storage. `display_ble_smp_l2c_data.c` reduces native `smpL2cDataCback`
0x537278: command/length/expected-opcode validation, authenticated warning
format, and state-machine event construction. The non-command-5 event's
fourth byte is native ambient stack data. A named Thumb entry shim now
recreates the native push/sub frame and passes that exact slot to the C body,
which writes only the stock-defined fields. Actual compiled ARM C/native
comparison passes Pairing Failed, normal-command ambient-byte preservation,
and invalid opcode in `verify_ble_smp_l2c_data_native.py`. Corrected receipt
`g2/build/c-firmware/20261011/peripherals-smp-l2c-ambient-round/receipt.json`
passes with 2264 defined, 812 mixed unresolved, zero duplicate strong,
SHA-256 `bdf5d79054ff8b1776916eb0fcc281d3ce499de1e1e67b8a65843f37589ba99b`.
The SMP action vector and live DM/CCB placement remain separate contracts.

The pinned Cordio SMP state-machine sources compile as four separate ARM C
units. `verify_ble_smp_tables.py` compares their relocatable object tables
against native: **107 indexed state rows**, **four common tables**, and **158
action-vector symbol names** all match. Four wrapper units under
`peripherals/smp_tables/` export distinct legacy/secure-connection initiator
and responder table symbols while preserving authentic Cordio bodies. An
isolated relocatable link against Main passes with zero duplicate strong
providers; it exposes 88 real action-function imports. These wrappers are
not yet selected by the root manifest, and the live `smpCb` CCB storage and
final ROM placement remain explicit contracts.

Six further pinned Cordio action translation units are wrapped under
`peripherals/smp_tables/candidate_*_act.c`. They compile for ARM M55 and
define **99 unique action/helper bodies** across common, secure connection,
initiator and responder roles. Only `smpSmExecute` overlaps a selected native
body, so the pinned copy is explicitly renamed and remains unused. An
isolated relocatable link with the corrected Main candidate passes at **2363
defined / 854 mixed unresolved / zero duplicate strong** before adding the
four transition-table wrappers. The additional imports are genuine WSF,
cryptographic and DM descendants; the source units do not close the whole
SMP runtime. `verify_ble_smp_action_cleanup_native.py` passes four actual
compiled-C/stock `smpCleanup` cases, comparing the full 0x50-byte CCB and
free/timer-stop effects. This bounded oracle supports the pinned source body,
while the other action branches still need per-path qualification. The six
action wrappers remain outside the selected manifest until the root table
snapshot settles.
`verify_ble_smp_action_failed_native.py` additionally passes four compiled
ARM C/stock `smpActPairingFailed` cases, including scratch-buffer cleanup,
timer stops, DM idle transition, and callback event/argument effects.
Root-selected ten table/action wrappers now form a coherent Main candidate:
`g2/build/c-firmware/20261011/peripherals-smp-actions-round/receipt.json`
passes at **2374 defined / 850 mixed unresolved / zero duplicate strong**,
SHA-256 `ed128a0e588fd2ab9b640d87375c87eaae67673a0797352df915b9ad233cb56d`.
This is C source inclusion and relocatable linking, not full SMP behavior or
product runtime data placement. The next authentic action descendants include
roughly 42 distinct SMP/WSF/DM/security imports newly exposed by these bodies.

`display_ble_smp_action_children.c` reduces `smpMsgAlloc` 0x537bca,
`SmpScAlloc` 0x56cf04, and `WsfTimerStartSec` 0x52a4b8. It binds the already
selected exact-ABI C implementations of WSF message data allocation and
timer insertion; buffer allocation and state-machine execution remain their
real selected providers. `verify_ble_smp_action_children_native.py` passes
four actual compiled-C/stock cases across ordinary allocation, scratch
allocation success/failure, and the 100-tick-per-second timer conversion,
comparing defined arguments, returns and message bytes. Full SMP cryptography,
DM live state and hardware effects remain unqualified.
The coherent Main target build capturing these three children passes at
**2377 defined / 847 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-action-children-round/receipt.json`,
SHA-256 `64be2fbaf7291f5762f8d58f7e69e3a84779f84b0d0e6d6dbb7f363cbb8f3f9d`.

`display_ble_wsf_buf_free.c` reduces native `WsfBufFree` 0x5304d4 using the
already selected pool-list/count RAM producers. The exact stock marker
`0xfaabd00d` comes from native literal 0x530534. It scans pool classes in
reverse, compares the block against each class base, then locks and pushes
the block onto the matched free list. Four actual compiled ARM C/stock cases
pass in `verify_ble_wsf_buf_free_native.py`: empty class list, lower class,
upper class and below-range return; all descriptor/block bytes and critical
section effects match. Pool table initialization and placement remain live
product RAM contracts, not hardcoded values.
The coherent Main snapshot including `WsfBufFree` passes at **2378 defined /
846 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-wsf-free-round/receipt.json`,
SHA-256 `4056619505bf208a8f7454586671372064dbf67158e98082c2bbda83795e00e3`.

Two further direct children are source-reduced: `display_ble_wsf_msg_free.c`
implements native `WsfMsgFree` 0x4bf9b0 by returning the authenticated
8-byte message header to `WsfBufFree`; `display_ble_dm_conn_sec_level.c`
implements native `DmConnSecLevel` 0x4b71b2 from the live 0x30-byte DM
connection rows. The latter uses the exact native arithmetic even for ID
zero and passes four compiled-C/stock reads in
`verify_ble_dm_conn_sec_level_native.py`. The DM row storage is an existing
unresolved live RAM contract; no default connection records are invented.
The coherent build with these two direct children passes at **2380 defined /
844 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-wsf-dm-round/receipt.json`,
SHA-256 `c0cc511c146aa9ca7d21ffdf71c5232885ac82967ae407343135bb6356502e43`.

`display_ble_dm_smp_callback.c` further reduces `DmSmpCbackExec` 0x4d24a8:
events 0x2a/0x2c go first to the optional ATT callback at DM connection
state +0x90, then all events reach the required DM client callback at handler
state +8. These are live callback slots, not fabricated no-ops. Six actual
compiled-C/stock cases pass in `verify_ble_dm_smp_callback_native.py`,
comparing callback order and argument across both event classes and ATT slot
present/absent. Coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-smp-dm-callback-round/receipt.json`
passes at **2381 defined / 843 mixed unresolved / zero duplicate strong**,
SHA-256 `15f77cb46378f43d4026b773bc544c0bb4f83148d8c7f7e4ca8279bcb1831b5c`.

The pinned Cordio utility sources `bda.c`, `calc128.c`, `wstr.c` are wrapped as
three separate candidate units under `peripherals/smp_tables/`. They compile
for ARM M55 and add twelve source-defined providers, including the actual
16-byte `calc128Zeros` C data object. An isolated relocatable link against the
preceding Main snapshot passes with zero duplicate strong providers and
reduces seven newly exposed utility names. The current decompilation corpus
does not assign direct stock entry addresses to the BD/128-bit utility
helpers, so this is pinned-source ABI inclusion rather than behavioral
equivalence proof. The wrappers await root manifest selection.
The three utility wrappers are now selected experimentally. Coherent Main
`g2/build/c-firmware/20261011/peripherals-smp-util-round/receipt.json` passes
at **2393 defined / 838 mixed unresolved / zero duplicate strong**, SHA-256
`7e2d2eebbc31b14d92dcd0f54529c21b308df9a45f471af17bfcfe9f0ac942f9`.
`WStrReverseCpy` additionally has direct stock entry 0x56d8c4; its pinned
source's signed-16-bit loop and reverse-store order match the native
decompilation. `verify_ble_wstr_reverse_native.py` passes five actual
compiled-C/stock buffer cases with lengths 0, 1, 6, 16 and 31. The other
utility bodies remain pinned-source candidates without direct native runtime
qualification.

`display_ble_smp_sc_scratch.c` reduces complete pinned/native
`SmpScAllocScratchBuffers` 0x56cdc0 and `SmpScFreeScratchBuffers` 0x56ce4e.
The five scratch fields at secure-connection offsets 0x14, 0x08, 0x18,
0x0c and 0x10 use the exact native sizes 0x60, 0x40, 0x20, 0x40 and 0x20.
The native allocation order, reuse, aggregate success result, and conditional
free/clear order are preserved. `verify_ble_smp_sc_scratch_native.py` passes
eight actual compiled-C/stock cases, comparing the full secure-connection
state and alloc/free call sequence across existing buffers and one failure.
The CCB and scratch storage remain live runtime data; no particular buffer
address or allocation outcome is assumed by the selected implementation.
The coherent Main snapshot with the scratch lifecycle passes at **2395
defined / 836 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-sc-scratch-round/receipt.json`,
SHA-256 `18c4ea64ee14f4f60591acfb4ffd49e0e8427067802b30bd1133b6c0bfb24279`.

`display_ble_smp_sc_f4.c` further reduces native `SmpScCat` 0x56cfc2 and
`SmpScCalcF4` 0x56cf2c from pinned Cordio. The latter allocates 65 bytes,
concatenates two 32-byte public-key coordinates, writes the Z byte, and
passes the authenticated sixth stack argument as the CMAC key; allocation
failure has no CMAC call. `verify_ble_smp_sc_f4_native.py` passes two actual
compiled-C/stock connected cases with source-defined buffer bytes and
child-call argument sequences. The cryptographic `SmpScCmac` child and its
security hardware/provider effects remain genuine unresolved contracts.
The coherent Main snapshot with F4 and Cat passes at **2397 defined / 834
mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-sc-f4-round/receipt.json`, SHA-256
`07bb29d8a33de5fba9c9e7b6267e46f0bdcfb50e988d9fac8e5d19046b11b316`.

`display_ble_smp_sc_cmac.c` then reduces native `SmpScCmac` 0x56cec2:
handler token from live SMP state +0xec, connection ID from CCB +0x3d,
native event 0x1c, and conditional text free/status/event/SM execution on
security request failure. `verify_ble_smp_sc_cmac_native.py` passes two
actual compiled-C/stock branches, including six-argument `SecCmac` call
state and failure effects. `display_ble_sec_cmac_request.c` reduces the
native `SecCmac` producer 0x53665c from pinned Cordio: 100-byte WSF
allocation, authenticated queue/callback field offsets, source-owned 16-byte
key copy, live token increment, and subkey-generation call. The last
routine passes two actual compiled-C/stock allocation success/failure cases
in `verify_ble_sec_cmac_request_native.py`, comparing the full 100-byte
request, key bytes, token and child calls. `secCmacGenSubkey1` is the next
genuine crypto child; the existing `audio_ble_stack_state_20072cb8` contract
is the typed live secCb RAM whose placement and initializer ownership remain
unproven.
The coherent Main snapshot through `SecCmac` passes at **2399 defined / 835
mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-sc-cmac-request-round/receipt.json`,
SHA-256 `f048cde7b7277783b5a064a7874ef73021dc808b56d6971d52626448225d9f6c`.

`display_ble_sec_cmac_subkey.c` reduces native `secCmacGenSubkey1` 0x53653a
from pinned Cordio: it extracts the key at CMAC CB +4, supplies a 16-byte
zero block, and calls the genuine LE encryption child with handler at +0x28.
`verify_ble_sec_cmac_subkey_native.py` passes three actual compiled-C/stock
cases comparing the child arguments and all zero bytes. The connected child
`display_ble_sec_le_encrypt.c` reduces native `SecLeEncryptCmd` 0x5363ae:
two 16-byte reverse copies, enqueue to live secCb AES queue at +0x20, then
HCI LE encrypt command. `verify_ble_sec_le_encrypt_native.py` passes two
actual compiled-C/stock cases comparing enqueue order/arguments and both
reversed command blocks. `HciLeEncryptCmd` is the next genuine controller
command provider; transmission and controller response remain hardware gates.
The coherent Main snapshot through both subkey and LE encrypt source bodies
passes at **2401 defined / 835 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-sc-encrypt-round/receipt.json`,
SHA-256 `27225ff0d77c5a53ae59372eb049cc4f91aace868f1b4b3a90434c47aac64621`.

`display_ble_hci_le_encrypt_cmd.c` reduces the genuine next provider
`HciLeEncryptCmd` 0x52b266 from pinned Cordio `hci_cmd.c`. It allocates LE
Encrypt opcode 0x2017 with 32-byte payload, writes 16-byte key and plain
blocks at command offsets 3 and 0x13, and sends only on allocation success.
`verify_ble_hci_le_encrypt_cmd_native.py` passes two actual compiled-C/stock
allocation branches comparing full command bytes and alloc/send arguments.
The selected HCI command allocator and sender are real connected providers;
controller execution remains a hardware contract.
The coherent Main snapshot including the HCI LE Encrypt command passes at
**2402 defined / 834 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-hci-encrypt-round/receipt.json`,
SHA-256 `d53aa0e17b88612ae3ca99a246b87c92e2e6a578d14aab41416b0aedbac0050b`.

The pinned `sec_main.h` supplies an attributable 0x50-byte `secCb_t` BSS
layout at native RAM 0x20072cb8. `display_ble_sec_cb_storage.c` now defines
the existing `audio_ble_stack_state_20072cb8` symbol as a typed object, with
compile-time offset/extent checks for its 32 random bytes, three WSF queues,
token and five callback slots. The already selected initializer
`audio_ble_stack_lower_536324` clears queue words and token; selected callback
initializers write the authenticated table slots. This owns C storage and
proven source layout; final linker placement and runtime initialization order
remain separate gates.
The coherent Main snapshot after reusing and defining the existing secCb
symbol passes at **2403 defined / 832 mixed unresolved / zero duplicate
strong** in
`g2/build/c-firmware/20261011/peripherals-smp-seccb-storage-round/receipt.json`,
SHA-256 `a749d34900ecee8322dd2e5a9d5033a709b2b80de951ad74c55f51442b4be386`.
The earlier `audio_ble_sec_state` alias was removed before this snapshot.

`display_ble_dm_conn_idle.c` reduces native `DmConnSetIdle` 0x4b71dc from
pinned Cordio. It uses the existing live DM rows, locks around `DmConnInUse`,
updates the 16-bit idle mask with native zero/nonzero idle semantics, unlocks,
then follows the authenticated INFO diagnostic policy and exact source
string/line. `verify_ble_dm_conn_idle_native.py` passes four actual compiled
ARM C/stock cases for in-use/unallocated rows and clear/set masks with trace
disabled, comparing mask bytes and lock/unlock/WSF trace effects. The
trace-enabled INFO branch additionally passes two actual compiled-C/stock
cases in `verify_ble_dm_conn_idle_log_native.py`, comparing the mask and
complete path/name/line/format/argument log tuple. Other trace-policy
levels remain outside these bounded tests. The
`DmConnInUse` child is a genuine newly exposed provider; DM row storage and
callback initialization remain live product-data obligations.
The coherent Main snapshot with `DmConnSetIdle` passes at **2404 defined /
832 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-dm-idle-round/receipt.json`,
SHA-256 `8d945aa16f770c0c1054ba011aa931f6c937eeb24d10f0c7ce9888acf409a43e`.
`display_ble_dm_conn_in_use.c` reduces its native `DmConnInUse` child
0x4b6ec6 from pinned Cordio using the authenticated 0x30-byte DM row stride
and in-use byte offset. `verify_ble_dm_conn_in_use_native.py` passes four
actual compiled-C/stock reads, including ID zero's exact native address
arithmetic. The shared DM row object remains a live RAM/storage placement
contract; this getter does not invent connection state.
The coherent Main snapshot with `DmConnInUse` passes at **2405 defined /
831 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-dm-in-use-round/receipt.json`,
SHA-256 `37b388519dca16b44012c2f26e04610c5ddf085ece077555c8608b7dd004f8ce`.

`display_ble_smp_sc_small_children.c` reduces three further pinned/native
SMP descendants: `SmpScCat128` 0x56cfdc, `smpGetPkBit` 0x56d150 and
`smpGetScSecLevel` 0x537c00. It reuses selected `Calc128Cpy`, reads the
authenticated secure-connection scratch and passkey position fields, and
classifies LESC/MITM security from native CCB bytes. Twelve actual compiled
C/stock cases pass in `verify_ble_smp_sc_small_native.py`, including passkey
positions across the byte boundary and 127/128/255, security-level branches,
and exact 16-byte append. Scratch and CCB objects remain live runtime state.
The coherent Main snapshot including the three small SC helpers passes at
**2408 defined / 828 mixed unresolved / zero duplicate strong** in
`g2/build/c-firmware/20261011/peripherals-smp-sc-small-round/receipt.json`,
SHA-256 `ebe62a00385d8a285f9129569f4f6ac09c0a7d27124110e82064ff719a63a27f`.

`display_ble_smp_sc_send.c` reduces four complete pinned/native outgoing
secure-pairing packet bodies: public key 0x56cfec, DH key check 0x56d054,
random 0x56d0a8 and confirmation 0x56d0fc. Each marks the connection busy,
starts the response timer, allocates the authenticated size, writes the
native opcode and reverse-order payload, and either sends or emits the exact
cancel event on allocation failure. `verify_ble_smp_sc_send_native.py`
passes eight actual compiled-C/stock cases (success and allocation failure
for all four) comparing packet/message bytes and every child-call argument
and order. The selected HCI/SMP send descendants are source defined, while
actual controller transmission remains unmeasured.

`display_ble_discovery_service_complete.c` now reduces the full
`AttcDiscServiceCmpl` 0x56bf32 parent, including event/status branches,
start/end handle extraction, and authenticated trace paths. Actual compiled
ARM C/native comparison PASS 4 for found service, empty data, explicit status,
and unexpected event in `verify_ble_discovery_service_complete_native.py`.
Coherent target receipt
`g2/build/c-firmware/20261011/peripherals-discovery-service-round/receipt.json`
passes with 2235 defined, 817 mixed unresolved, zero duplicate strong,
SHA-256 `b59179a56833dd955441d523074518b42f879845951487c76a8ec7cb3a977c59`.
The remaining substantial connected processor is 0x532924; it uses live
discovery rows and a product callback pointer and has additional Cordio
children, so it is not yet a source-complete whole subtree.

`display_ble_smp_sc_fail_retry.c` reduces native 0x56d304 with an ARM entry
shim that preserves the original incoming R2/R3 event-frame bytes. Its actual
compiled-C/native oracle passes two ambient seeds. `display_ble_smp_generate_ltk.c`
reduces native 0x5379f4 and pinned Cordio `smpGenerateLtk`, including random
key generation, zero remainder, EDIV/RAND copy, security level, and the DM
callback. Its actual compiled-C/native oracle passes six key-length and
authentication combinations. The coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-smp-fail-ltk-round/receipt.json`
passes with 2414 defined, 822 mixed unresolved, zero duplicate strong,
SHA-256 `a21972dc2962588d1ff8ceec46927303137bedbb2f9e57f62e4b4f794a58bdd8`.
Full Main source, final RAM placement, and controller behavior remain open.

`display_ble_sec_rand.c` reduces pinned Cordio/native `SecRand` 0x53634e.
It copies from the source-owned 32-byte `secCb` circular random ring and
requests one real HCI refill per eight requested bytes. The actual
compiled-C/native `verify_ble_sec_rand_native.py` passes 21 cases across
lengths 0, 1, 7, 8, 9, 16, 32 and ring positions 0, 1, 3; it compares
output bytes, ring state, and HCI refill count. The coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-sec-rand-round/receipt.json`
passes with 2415 defined, 821 mixed unresolved, zero duplicate strong,
SHA-256 `d472ab8fadfefbd2182afd66346e004df23be12fd6992d36965c4c52a9922cb2`.
Source ownership of the ring does not prove hardware entropy or final RAM
placement.

`display_ble_smp_calc_s1.c` reduces full native 0x537998, including two
64-bit random halves, AES request, token, and exact cancellation event.
`display_ble_sec_aes.c` reduces native 0x536426 and its token child 0x5363fc,
including 56-byte message allocation, token rollover past 0xff, queueing,
and actual HCI encryption call. `display_ble_smp_calc_c1.c` reduces full
native 0x537742 and 0x53786c, including both connection roles, RPA/address
selection, 16-byte XOR inputs, AES request, and invalid-token event.
Actual compiled-C/native oracles pass 2 S1, 4 AES, and 16 C1 cases,
including cancellation and allocation failure. The coherent Main receipt
`g2/build/c-firmware/20261011/peripherals-smp-c1-round/receipt.json`
passes with 2419 defined, 822 mixed unresolved, zero duplicate strong,
SHA-256 `15d6dbf99c1582e7c2e7a46225645569ced70a7aa2ff3b697e3e8cad88b9795f`.
The two C1 bodies expose genuine DmConnLocalRpa/DmConnPeerRpa imports; their
source/data producers and `SmpDbMaxAttemptReached` remain to reduce.

The connected SMP database and DM RPA scope is now source defined:
`display_ble_comm_registration_config.c` provides the authenticated 24-byte
typed `smpCfg_t` initializer at stock 0x774d44; its compiled ARM `.rodata`
equals all 24 stock bytes. `pSmpCfg` is the exact same native RAM pointer
cell at 0x200004b8 as the selected registration slot, written by
`bleCommHandlerInit`. `display_ble_smp_db_max_attempts.c` reduces native
0x5426c0 with the selected diagnostic path, multiplier, timeout cap, record
state, and service timer; actual C/native record and timer comparison passes
eight trace-disabled cases. `display_ble_smp_db_service_timer.c` reduces
0x541e34; actual C/native passes two timer-state cases.
`display_ble_dm_rpa_access.c` reduces 0x4b6f28/0x4b707c with exact record
offsets and the zero-connection WARN diagnostics; actual C/native passes
six pointer/trace cases plus two enabled-WARN logging cases. Coherent Main
receipt `g2/build/c-firmware/20261011/peripherals-smp-rpa-timer-round/receipt.json`
passes with 2426 defined, 817 mixed unresolved, zero duplicate strong,
SHA-256 `5b41feb3f62cd0be683758497b391cde50951f5a0ed3419498e965e2114826b5`.
The formerly named C1/DB/RPA/pSmpCfg import group is closed in this
candidate graph. Final data placement, startup order, and whole Main source
and runtime equivalence remain unproved.

The next DM/security and ATT connected bodies are source defined from
authenticated native and pinned Cordio providers. DM local address/type,
HCI local address, local CSRK, ECC-key getter, SMP encryption request, and
connection-row lookup resolve their exact native state roles. Actual C/native
oracles pass eight DM-local, two encryption-request, and six connection-row
cases. The full ATT database hash builder 0x53527c, hashable attribute
classifier 0x534ea8, and CMAC wrapper 0x53525c are compiled. Controlled
native/C cases pass two allocator/assembled-message cases, twenty UUID and
characteristic-skip cases, and three CMAC ABI cases. The UUID128 setting is
native bit 0, confirmed by the comparison; an initial bit-1 interpretation
was corrected before the coherent build. `HciLeStartEncryptionCmd` 0x52b5a2
passes two command-byte/alloc-failure comparisons.

The ATT CSF hash status getter/setter 0x52c914/0x52c6c0 use the existing
live CSF state and perform complete/pending transitions. Actual C/native
cases pass four state transitions and two enabled INFO diagnostic paths.
The connected pending database-hash response 0x534dd8 handles all three
connection rows, allocation error, absent attribute, data response, free,
and pending clear; three actual C/native cases compare response bytes, row
state, and lower-call effects. This is candidate source evidence; final
physical RAM ownership/placement and runtime equality are separate gates.

The pending ATT response exposed its own three genuine children. The pinned
`attMsgAlloc` 0x4b50ae, `attsErrRsp` 0x534c9a, and `attsFindByHandle`
0x56c5d4 are now C-defined, preserving allocation, error packet fields,
L2CAP dispatch, group traversal and the successful group-out pointer.
Five actual compiled-C/native cases compare alloc, error success/failure,
and group hit/miss effects. The separately reconstructed HCI LE Start
Encryption packet uses opcode 0x2019 and a 28-byte payload; two actual
C/native cases compare the full packet and allocation failure.

The connected ATT hash code graph now closes through the native
`WsfMsgDataAlloc` 0x4bf990 and `attL2cDataReq` 0x4b50ba. Four actual C/native
cases cover allocation, legacy ATT dispatch, extended bearer callback, and
free-on-absent-callback behavior. The pinned 16-byte `attsCsfCb_t` is
source-owned as `audio_ble_connection_state_table`, with client rows at +0,
callback at +8 and hash status at +12. The coherent selected+experimental
Main receipt `g2/build/c-firmware/20261011/peripherals-atts-csf-storage-round/receipt.json`
passes with 2447 defined, 808 mixed unresolved and zero duplicate strong,
SHA-256 `479820192889f07e5cd24303fad1da9cc0d0b415f355295a94d2e7621b0c956d`.

`hciCmdAlloc` 0x52ae38 has a full source body and actual C/native PASS2.
The canonical `hciCmdSend` entry branches to the already source-defined
0x52ae5e body with previously qualified ARM C/native PASS5; the entry
preserves all incoming registers needed by that body. The coherent Main
receipt `g2/build/c-firmware/20261011/peripherals-hci-cmd-public-round/receipt.json`
passes with 2449 defined, 806 mixed unresolved and zero duplicate strong,
SHA-256 `673eb0df2af0d5b177f96eb36cfb918b6692dc585391fb44ef062fd515f401a3`.
The remaining import count mixes code, live RAM, product tables, and compiler
ABI contracts; it is not a missing-body count or final image completion.

The advertising entry group now has native-backed full source bodies for
`AppAdvStart` 0x4b2d22, `AppAdvStop` 0x4b2d62, `AppSetAdvType` 0x4b2d7c,
`appAdvStop` 0x4b43fc, `appSetAdvType` 0x4b4510 and
`appSlaveResetAdvDataOffset` 0x4b334c. The already selected
`audio_ble_app_adv_state` is the exact native 0x4b46a8 child used by
`appAdvStop`. Four actual compiled-C/native test scripts pass 6, 3, 6 and
16 bounded cases respectively. They compare handles, pointer-referenced
configuration, calls and state mutations including the stopped, active,
suppressed-type, and fragmented-data branches. Pinned Cordio
`app_slave_leg.c` and `app_slave.c` provide independent source attribution.
The coherent `peripherals-app-adv-reset-round` target receipt passes with
2455 defined, 807 mixed unresolved, zero duplicate strong, SHA-256
`e2651517e31f11c60aede23c2ecef50d9a06c126d8261a95737ea1e8b7a76302`.
Connected children `appSlaveAdvMode`, `appSlaveAdvStart`, `appAdvStart`,
`DmAdvStop`, and the application state/configuration RAM remain genuine
interfaces. Final source, placement, boot initialization and device proof
remain open.

The connected scan fragment emitter `appSetAdvScanDataFrag` 0x4b3416 and
packet transport `DmAdvSetData` 0x4b319e are now complete pinned Cordio C
bodies. Actual compiled-C/native comparison passes ten fragment cases across
both locations and 0/5/251/252/500-byte lengths, and four data packet cases
including allocation failure and 251-byte payload. `appSlaveConnectableAdv`
0x4b32e2 and `appNumConns` 0x4bacf0 are source-defined using the existing
live app-state and connection-row contracts; seven native/C cases cover
advertising types/handles and role counts. The next coherent selected build
is `peripherals-app-adv-capacity-round`; its terminal receipt must be checked
before using its counts. The connected remaining bodies include
`appSlaveAdvMode` and `appSlaveAdvStart` plus their logging/callback children.

The subsequent advertising chain includes full native-backed C for
`appSlaveAdvMode`, `appSlaveLegAdvStop/Restart/Start/TypeChanged/NextLegAdvState`,
`_bleAdvInit`, `AppAdvSetData/appAdvSetData`, `DmDevSetRandAddr`,
`DmAdvSetAddrType`, `HciLeSetRandAddrCmd`, and `appSlaveConnOpen`. Six
application pointer cells are source-owned as four-byte BSS objects with
existing native initialization writes; their final absolute placement remains
open. The coherent `peripherals-adv-pointer-cells-round` Main relocatable link
passes at 2488 defined, 799 mixed unresolved, zero duplicate strong, SHA-256
`97a5efeb6bce8be09fd952272f5812321fd35982730ea510846eafb34d3e86ab`.

`APP_StartServiceDiscovery` 0x5354c2 now has a C body at
`display_ble_service_discovery_enqueue.c` and a named ARM entry shim that
preserves the incoming R4 consumed by stock diagnostic calls. Actual compiled
C/native comparison in `verify_ble_service_discovery_enqueue_native.py` passes
16 bounded cases across record presence, allocation success, and log flags
0/1/2/4. The first aggregate attempt had one callback function-pointer type
compile failure and no Audio archive; the corrected round passed a coherent
Main relocatable link at 2490 defined, 798 mixed unresolved, zero duplicates,
SHA-256 `1bbe7521338d5dfea883e920ead0f726b614bf9de5bc09b8a989bbbd6c134df1`.
The final aggregate snapshot after the diagnostic R4 correction is pending.
`audio_ble_discovery_handler_id_20074f8a` remains a genuine live data
contract; no initializer is attributed. Full Main source, RAM placement,
boot layout, and physical behavior remain unproven.

The corrected diagnostic R4 round passed Main at 2490 defined, 798 mixed
unresolved, zero duplicate strong, SHA-256
`6caa4e51e3a7d398831959d4e4df379d8ee01a759b0dbd8d40dade2e189aa72a`.
Two connected delayed callbacks are now source-defined: connection timeout
diagnostics 0x4b81b8 (`verify_ble_connect_timeout_check_native.py` PASS5), and
ring follow-up 0x4722cc (`verify_ble_comm_notify_followup_native.py` PASS1).
The coherent `peripherals-comm-callbacks-round` passed at 2492 defined, 796
mixed unresolved, zero duplicates, SHA-256
`06286c7b23882cc9c3cd648f540e42ae26010e5d0b31a52a99ff91bf97a02197`.

The native getter at 0x4b8122 returns the direct product struct address
0x200727f0. Older candidates had typed `audio_ble_controller` as a pointer
cell. Both uses were corrected to a direct byte-array contract; refreshed
actual compiled-C/native oracles pass four master callback cases and five
connection-request cases. Product storage placement and initialization are
still external. Full `PB_TxEncodeNotifySecAuth` 0x4bb92c is now source-defined
in `display_ble_comm_recovery_delayed.c`: all diagnostics, controller handler
check, allocation failure, message fields, send and return branches pass 16
actual C/native comparisons. Coherent `peripherals-comm-recovery-round` Main
passes at 2493 defined, 795 mixed unresolved, zero duplicates, SHA-256
`a6f089472b1cf4e607a681b78dc5d577cd5c7a959e68cccf9bd07bbc5819680c`.

Two original caller names for native 0x4bc418 now branch to the already
source-defined `audio_ble_master_success_delayed` body with the same ABI.
This is an exact shared entry and does not stand in for the separate larger
`PB_TxEncodeNotifyRingConnectInfoImpl` 0x4bc1b4, which remains genuine work.
The coherent `peripherals-ring-notify-alias-round` Main relocatable link passes
at 2495 defined, 793 mixed unresolved, zero duplicate strong, SHA-256
`ad86dd13cf10a63c203be018699cad024ac6dc80eb10e07c7eaf781aff5abd93`.
The mixed unresolved count is neither a body count nor a full-image coverage
measure. Remaining named work includes 0x4bc1b4, many BLE/HCI product table
and live state contracts, source-backed audio/driver code, linker/startup
placement, and physical device qualification.

The genuine 0x4bc1b4 parent has since been source-defined in
`display_ble_ring_connect_notify_impl.c`. It implements the native 0x1a8
allocation, 20-byte nanopb ostream copy, packet fields and auth state,
encoding and direct BLE send, all log/failure/free returns. Ten actual
compiled-C/native cases pass, including log-enabled allocation, encode and
send branches. Coherent `peripherals-ring-connect-notify-impl-round` Main
passes at 2496 defined, 794 mixed unresolved, zero duplicates, SHA-256
`37ff37e45ed62de07df3e3d520091929845ab09326c00f114e0ff42e4a31c795`.
Its protobuf descriptor at native ROM 0x7766dc remains a typed genuine data
contract. The distinct `Thread_MsgPbNotifyByBleDirect` 0x475aa6 child is now
source-defined with OTA gate and exact six-register/stack Tx forwarding;
`verify_ble_notify_direct_native.py` passes eight actual C/native cases.
That child postdates the parent receipt; the next coherent target build is
pending. Source completeness, descriptor ownership, final layout, and device
behavior remain open.

The subsequent coherent `peripherals-ring-connect-direct-round` Main build
passes at 2497 defined, 793 mixed unresolved, zero duplicate strong, SHA-256
`2aa3ce9e616ac3c87309074a1bf60b9201bdde49c595e9c94b46e67c49fca8ed`.
The recent complete routine group is the advertising start/stop/data path,
service discovery enqueue, three connected delayed callbacks, ring
notification parent, and direct BLE send child. Whole Main remains incomplete:
793 is a mixed code/data/runtime/ROM interface count, and final source layout
and physical validation have not been shown. Immediate concrete work includes
the authenticated ring protobuf descriptor extent/ownership, the separate
SecAuth notification implementation, other connected BLE/HCI providers and
live product table initializers; none are implied complete by this link.

The ring protobuf data graph rooted at native ROM 0x7766dc has now been
decoded using nanopb v0.4 `pb_msgdesc_t` and generated field-info semantics.
`generate_ring_pb_descriptors.py` asserts the official OTA SHA-256 before
emitting semantic `FIELD1`/`FIELD2` C initializers and typed child references.
The finite graph has 20 unique descriptors, 71 fields, and 22 submessage
relocations. `verify_ring_pb_descriptor_bytes.py` compiles the target source
and verifies all 20 field-info arrays (488 bytes) and all descriptor count
fields against authenticated stock bytes. The coherent
`peripherals-ring-pb-descriptor-round` Main relocatable link passes at 2498
defined, 792 mixed unresolved, zero duplicates, SHA-256
`955e81f0c1556e01103a9176468a1cd76263a1606fde8949373c60f18f13d08b`.
The actual `audio_pb_encode` parent and its iterator/field children remain
genuine code imports; descriptor source bytes and pointer graph do not prove
runtime encoding or final ROM placement. Whole Main remains incomplete.

The source-defined nanopb encoder entry at native 0x490c32 now traverses the
40-byte field iterator and dispatches extension/ordinary fields with authentic
error exits. Actual compiled C/native child-cut comparison passes eight cases.
The coherent `peripherals-pb-encode-parent-round` Main link has 2499 defined,
795 mixed unresolved, zero duplicate strong symbols, SHA-256
`efad021f77fa57909ae9866da7800390f1897709af4d103fee6c7a56335dbe9c`.
The true iterator begin/reset/next bodies at 0x4d94ba/0x4d9384/0x4d93d8
passed four C/native cases and coherent `peripherals-pb-iter-begin-next-round`
has 2501 defined, 795 mixed unresolved, zero duplicates, SHA-256
`4d5bb6bf31fd6f1a11e341d3b3c2e8a0bf6a8fa0d5fbd2f269b53afad97144cd`.

The complete iterator field decoder 0x4d916e and advance 0x4d930a are now
source-defined. A focused actual compiled C/native oracle passed 132 cases
across four authenticated descriptors, nullable messages, and all field
positions, including native unchanged-data behavior on a null message.
Coherent `peripherals-pb-iter-decode-advance-round` Main link has 2503 defined,
793 mixed unresolved, zero duplicates, SHA-256
`c49232c8e32b61f55b5028ebe1af63e01c3ff216be4410aa3b8f5ac62c07490c`.
The extension-list encoder 0x490bf8 passes six compiled C/native callback
cases and coherent `peripherals-pb-encode-extension-round` has 2504 defined,
793 mixed unresolved, zero duplicates, SHA-256
`3c0bb25677f9506ff8942317d53f23be80120265b44dc5e7c9a085c39f04bc94`.
The field dispatcher 0x490b1e passes ten compiled C/native branch cases;
its five genuine child encoders/predicates remain explicit imports. The
diagnostic is source-owned from native literal 0x779fc4 via 0x4910c8 pointer
cell. Its coherent target link has 2505 defined, 797 mixed unresolved, zero
duplicates, SHA-256
`3218930d6d20a741007ac5175aed5677262cfe0cd904a94ca6b552bc132c48ed`.
The callback dispatcher 0x490aea and first-char predicate 0x490678 pass six
compiled C/native cases, including the authenticated callback-error literal;
the coherent link is 2507/795/0, SHA-256
`229d8b1c1daafa8ba860236a32c4e6f5ffdab235f4e20f26592536ccee231cc7`.
The default predicate 0x49087a and callback marker 0x4d94e6 pass twelve
bounded primitive cases; coherent link is 2509/794/0, SHA-256
`57ebbe00b535af9b15451911ba19373255f9fc4739f25b07c4ae354528f95f85`.

The full single-field dispatch 0x490a46 passes 48 compiled C/native cases
across all 16 field type values, null data, and tag failure; coherent link
is 2510/801/0, SHA-256
`3efaeb133dd4ef935a6940aeb9ef451d8586df196f5d3214253d7864c44f1d82`.
The native wire-key constructors 0x490d66/0x490d4a pass 32 cases and link at
2512/801/0, SHA-256
`f8446f01e8b073cf76c039ecdee71228fdd184c1d67faf0fb7f00070e07231b0`.
The varint dispatch/emitter 0x490ce0/0x490c84 and stream writer 0x490616
pass 24 actual compiled C/native byte/effect cases, including capacity and
callback failures; coherent link is 2515/800/0, SHA-256
`13c603b4bbb4fb83a651e37e9a8269db2fb53d535305bd3d10be58b336aff698`.
The integer scalar 0x490eae and zigzag 0x490d08 pass thirty child-cut native/C
cases; coherent link is 2517/799/0, SHA-256
`c90baa6046718c80047c74863f29e958958b3ad9b3097b29ae7719b0e768f440`.
The fixed-width writers, length-delimited writer, bytes, and string bodies
pass eleven C/native cases; coherent link is 2523/796/0, SHA-256
`fb2aba8e3015a6cfae1729e99e0f578a82f8fac250d2295959f0d0341dfb3bff`.
The bool, fixed-length bytes, and submessage dispatch bodies pass seven
native/C cases; coherent link is 2526/794/0, SHA-256
`fb394f56a69b9bef723b699a50d3757003f6cad1baa1262dfd2288b86207353a`.
The two-pass nested-message writer 0x490ddc passes six C/native branch cases
with counted size, length prefix, capacity, second pass, and error propagation;
coherent link is 2527/793/0, SHA-256
`4bcd018ce18a13a4e81b9935cd65c50ac2a15f00319b738221d147b045cb06dc`.
The full repeated-field encoder 0x490690 passes ten packed/nonpacked and
pointer-array child-cut cases. The default extension 0x490bc8 and iterator
setup 0x4d93a4 pass four cases; this found-cell verification corrected its
source offset to extension+12. Coherent Main link is 2530 defined, 791 mixed
unresolved, zero duplicates, SHA-256
`16060fa9bab7550b2d26f91c6116b93e3f9b28cb5e111ddf30e663b0194f0d77`.
There are zero `audio_pb_*` unresolved interfaces in that link. A connected
standalone ARM ELF containing the source-owned descriptor graph and full
reconstructed encoder passes nineteen actual C/native message comparisons against
stock 0x490c32/0x7766dc. The cases cover optional scalar values and oneof
submessage tags 3 through 14, 128, and 129, comparing output bytes, byte count, return,
and diagnostics. The `audio_uart_buffer_zero` oracle shim performs actual
zeroing; this is not arbitrary nanopb corpus equivalence. Mixed imports count
is not remaining body count.
Main source completeness, final layout, live product cells, and hardware
behavior remain open.

The native 496-byte `PB_TxEncodeNotifySecAuthImpl` 0x4bb73a has a full
source-defined allocation, packet, encoding, direct BLE send, free, and
diagnostic body. It reuses the authenticated source-owned ring descriptor and
nanopb encoder. The product auth-enable byte at 0x20074ffc remains a typed
live RAM contract, not an invented initializer. Actual compiled C/native
comparison passes nine bounded allocation, encode, send, and logging paths;
the comparison caught and corrected an initially reversed send-result branch.
Coherent Main link is 2531 defined, 790 mixed unresolved, zero duplicates,
SHA-256 `f76ed51905dafa71082194d053eb21e5b3e4898a5bb9a0a4424d54ccb9b100a7`.
The next connected genuine frontier includes LE IQ report parsers, protobuf
decoding for UART dashboard, and remaining live product RAM ownership.

The native Cordio HCI connectionless IQ report parser 0x56a908 (448 bytes)
is source-defined with 192-byte WSF allocation, exact event field offsets,
two sample copy effects, callback/free, and trace/log selection. Native
instructions verify that its second copy reloads the first destination
pointer, rather than the separately stored second pointer. Authenticated
`INFO`/`WARN`/`ERR`/`APP`/`HCI` literals are now source-owned const arrays.
Actual compiled C/native comparison passes five allocation, logging, trace,
and sample-count cases. Coherent Main link is 2537 defined, 784 mixed
unresolved, zero duplicates, SHA-256
`0d24ce5bf2e03b8f029f7045292ede37ae415115e944eb950dcf1ccbc72a053a`.
The connected HCI connection IQ report parser 0x56a63e (708 bytes) is also
source-defined with its two diagnostic stages and distinct 13-byte header.
Five actual C/native fixtures pass. Both IQ parsers link coherently with 2538
defined, 783 mixed unresolved, zero duplicates, SHA-256
`f7a228776eb20f064e3a0b27c1f496d368acd3e6e0ae4a0231b93f23c6c7e6c7`.
The HCI callback table at 0x20073870 remains live product RAM and final
hardware behavior is unverified.

The UART nanopb decoder entry 0x490120, descriptor iterator tag search
0x4d93f8/extension search 0x4d946e, and input byte/varint/tag parser
0x48f454/0x48f4b8/0x48f66c are source-defined. Actual compiled C versus
stock passes 3 entry, 48 iterator search, and 14 parser cases, including
overflow, truncated varints, stream errors, and preserved diagnostics.
The coherent Main candidate link at `peripherals-pb-decode-tag-round` has
2544 defined, 783 mixed unresolved, zero duplicate providers, SHA-256
`d4e00ea7d398b915447b27153ae0cf4a4a3f04150c5bb513ad235a55fdfe8bc9`.
The genuine decoder parent 0x48fe98 and field/skip/default children remain
unreduced; dashboard schema/stream initialization are separate product data
and source contracts. No full decoder or Main image claim follows from these
bounded comparisons.
The unknown-wire dispatcher 0x48f6a0 and varint-skip loop 0x48f628 are now
source-defined; twelve stock/C child-cut cases pass for four valid wire types,
invalid wire type, and lower success/failure. Their actual input stream reader
0x48f3be and length skip 0x48f64c remain typed authentic code imports. The
coherent Main candidate link at `peripherals-pb-skip-wire-round` has 2546
defined, 785 mixed unresolved, zero duplicate providers, SHA-256
`dc82db0a13a2742de98873757d2df9ead2ecc23cf354262641a0661a589b2038`.
The connected input buffer reader 0x48f3a4, callback-aware stream read
0x48f3be, and length-delimited skip 0x48f64c are source-defined. Eight
actual compiled C/native cases pass direct and generic callbacks, null
destinations, lengths, stream state, and failure behavior. The coherent
Main link at `peripherals-pb-decode-stream-round` has 2549 defined,
783 mixed unresolved, zero duplicates, SHA-256
`15564de1c10e377ff8f87e1abb5e84da89e57760e7cf566ef0aaca9b7ff1a925`.
The sole directly unresolved `audio_pb_*` code provider is the full decoder
parent 0x48fe98; implementing it will expose real field/default children.
The native storage-mode field dispatcher 0x48fbe4 is now source-defined and
passes sixteen actual compiled C/native child-cut cases, including inherited
diagnostics and invalid storage mode. Its three genuine static, callback,
and pointer field bodies are now explicit typed code imports. The coherent
Main link at `peripherals-pb-decode-dispatch-round` has 2550 defined, 786
mixed unresolved, zero duplicate providers, SHA-256
`e2598ab14b312d298815b21eb2906486e54c0cc73bdf4874e3ff77eb544a5d28`.
The native pointer-field branch 0x48fb1c is a complete no-malloc failure body
in this build, not a generic success stub. Source-owned diagnostic text
matches stock and preserved prior errors. Two actual compiled C/native cases
pass. Coherent Main link at `peripherals-pb-decode-pointer-round`: 2551
defined, 785 mixed unresolved, zero duplicates, SHA-256
`29a0fae1c176ccb1de956d1ee6550fbd044fec77e6079ceb3ae7e71c43a9effe`.
The UART dashboard input-stream constructor 0x48f49c now uses the actual
source-owned buffer callback and initializes the four native words. Four
actual compiled C/native cases pass callback identity, buffer pointer,
length, and null diagnostics. Coherent Main link at
`peripherals-pb-decode-init-round`: 2552 defined, 784 mixed unresolved, zero
duplicates, SHA-256
`bd0b28c685c804cac456437fa671fdb20551ab641be358fd4fd8b405f02aaabe`.
The full source candidate for static-storage field mode 0x48f968 and scalar
wire dispatcher 0x48f7f4 now builds. Actual compiled C/native child-cut
comparisons pass six optional/repeated/oneof/packed/overflow cases and sixty
scalar type/wire combinations. The bounded cases do not yet cover the nested
default-setting branch or a connected arbitrary decoder message. Coherent
Main link at `peripherals-pb-decode-static-round`: 2554 defined, 794 mixed
unresolved, zero duplicates, SHA-256
`2d140667998afb65e05702ff888cd4a4c3c0383df3076b76fa97158a6264f4da`.
Real scalar, submessage, substream, and defaults lower bodies are now typed
imports to reduce next.
The bounded substream begin/end pair 0x48f77e/0x48f7ca is source-defined,
including length prefix, parent reservation, child drain, state propagation,
and inherited diagnostics. Five actual compiled C/native connected buffer
cases pass. Coherent Main link at `peripherals-pb-decode-substream-round`:
2556 defined, 792 mixed unresolved, zero duplicates, SHA-256
`dd8fd835ed886f78457ca18f2a0ba1af9f8f67c338eb8bc67697c7bc9f943034`.
The bool, fixed32, fixed64, 64-bit varint, zigzag, and sized integer decoders
are now source-defined. Actual compiled C/native comparisons pass eight
bool/fixed stream cases and 135 type/width/value/truncation cases. Coherent
Main link at `peripherals-pb-decode-scalar-round`: 2562 defined, 788 mixed
unresolved, zero duplicates, SHA-256
`89631eba502497fb8881a9c2732dedb870a1e39ef1efc118c961470a360fbf0b`.
Remaining direct nanopb code is callback field, bytes, string, submessage,
extension, defaults, and decoder parent; mixed imports include unrelated
runtime/product data.
The bytes, string, and fixed-length bytes readers are now source-defined.
Ten actual compiled C/native buffer cases pass lengths, contents,
terminators, bounded overflow, zero length, and diagnostic effects. Coherent
Main link at `peripherals-pb-decode-text-round`: 2565 defined, 785 mixed
unresolved, zero duplicate providers, SHA-256
`7be9822c08e99ee1873f9d9a1b8ca738ee697d6f256a26d7821b14c04715709f`.
Direct decoder code remains callback field, submessage, defaults, and parent.
The full native submessage wrapper 0x49048c now has a source-defined
substream, descriptor failure, optional callback, recursive parent, and
substream finalization path. Eight compiled C/native child-cut cases pass,
including callback consumption/failure and nested flags. Coherent Main link
at `peripherals-pb-decode-submsg-round`: 2566 defined, 784 mixed unresolved,
zero duplicates, SHA-256
`9c38ef90725b3bf9defc6823a4dfaca9ca410fd73f55381ea73ebd71cc4f0ca1`.
The remaining direct code set is callback field, defaults, and parent.
The native callback-storage field body 0x48fb30 and callback scalar payload
copier 0x48f6ea are source-defined. Actual compiled C/native child-cut checks
pass eight callback dispatch/diagnostic cases, and eight connected payload
byte/length/error cases pass. Coherent Main link at
`peripherals-pb-decode-callback-round`: 2568 defined, 783 mixed unresolved,
zero duplicates, SHA-256
`c2d047247149d7759859ee7bfef0da3fc6a4fce562ebc8c0128f27a159ac4fbe`.
Direct decoder code remaining is default initialization 0x48fdf2 and parent
0x48fe98. Product dashboard schema and Main source/layout gates remain open.
Both default-field 0x48fce2 and default-iterator 0x48fdf2 bodies are now
source-defined. Nine native/C field-type reset cases pass, as do three
connected ring-descriptor default sweeps using the actual compiled iterator
and default bodies. This checks initial zero/default paths on the sampled
descriptors; encoded default streams and arbitrary extension chains remain
unqualified. Coherent Main link at `peripherals-pb-decode-defaults-round`:
2570 defined, 782 mixed unresolved, zero duplicates, SHA-256
`62eee755cf11be021907a6deabdb41ff6bf89e4a837be0ec88b4d31da484e40c`.
The sole direct `audio_pb_*` import is decoder parent 0x48fe98.
The full native message decoder parent 0x48fe98 and extension handlers
0x48fc88/0x48fc26 are now source-defined. Ten actual compiled C/native parent
branch cases pass; three extension-list/native cases pass. A standalone
connected ARM ELF with all reconstructed nanopb decoder units and the
source-defined ring descriptor passes 26 C/native message comparisons,
including scalar, oneof submessages, unknown and malformed tags. This remains
a bounded message corpus, not arbitrary decoder equivalence.

The UART dashboard schema is now source-owned rather than an unresolved ROM
pointer: literal 0x502664 loaded at native callsite 0x501ff8 points to
descriptor root 0x776574. Its six descriptor records, 24 semantic fields,
and five submessage relocations are generated as typed C initializers from
the authenticated OTA. All six records and 164 field bytes match native
source, and ten connected stock/C dashboard decode cases pass. Coherent
Main link at `peripherals-pb-dashboard-source-round`: 2575 defined, 780
mixed unresolved, zero duplicates, SHA-256
`9c0915a1406a2e88219ce95965431d2853057864e28a14c92d9421a036a3af0b`.
There are zero unresolved `audio_pb_*` and dashboard schema symbols in this
link. This closes the selected nanopb decode source graph for the ring and
dashboard bounded scopes. Main as a whole still has hundreds of mixed
runtime/data/code imports, other unreduced functions, and final layout and
hardware gates. The generated schema's final ROM placement remains open.

## Connected dashboard layout and BLE/settings source round

The product dashboard layout translator at native 0x502174 is source-defined
as `audio_dashboard_apply_layout_pb`. It reads the selected decoded 188-byte
dashboard object and ready byte, constructs the native 128-byte layout,
rejects unsupported position/widget/watchface values, and invokes the real
layout setter. Native 0x558376 setter, 0x558148 default restoration,
0x558030 widget predicate, 0x558040 watchface slot predicate, and 0x558050
watchface validator have full source bodies. The 128-byte default layout at
0x6d52d8 is a semantic C initializer (15 meaningful bytes, rest zero), and
all directly referenced diagnostic strings are byte-authenticated source
data. `audio_dashboard_layout_current[128]` remains a typed live RAM placement
contract at 0x200e7934. The native 0x44b5a0 bounded copy is source-defined;
its alignment fast path is replaced by equivalent byte operations. Actual
compiled C/native checks pass 12 parent child-cut cases, 11 connected parent
cases, eight direct setter cases, and 96 bounded-copy cases. They cover
defined decoded inputs, RAM layout effects, failure fallback, and selected
logging-disabled branches; arbitrary runtime layout integration and final
placement are unqualified.

Native queue drain functions `Thread_BleMsgrxQueueClear` 0x48f018 and
`Thread_BleMsgtxQueueClear` 0x475524 now have C bodies. They bind to the
already selected `audio_cmsis_queue_get_count` 0x449bc8,
`audio_uart_queue_receive` 0x449b3c, and `audio_file_heap_free` 0x474d16
providers, with typed live thread state cells 0x20003ffc/0x20004020.
Twelve actual compiled C/native effect cases pass across null/empty/multiple
queues, failure, and null-message exits. Native `dmConnGetAdvState` 0x46ef60,
used by the communications handler, is source-defined as the single-byte
read of live RAM 0x20074f8d; all 256 byte inputs match stock. The large
`SVC_Settings_DumpSettingConfig` 0x46b458 diagnostic body is source-defined
from the live settings record 0x20072da8 and byte-authenticated formats.
Ten actual compiled C/native cases compare all extended/compact call
sequences, line numbers, formats, and scalar values under five log-flag masks.
Its native inherited register only appears as an unused extra argument to
the no-placeholder opening banner; no source value is invented.

The coherent Main selected-plus-experimental archive at
`g2/build/c-firmware/20261011/peripherals-dashboard-ble-settings-round`
compiles and relocatable-links with 2620 defined symbols, 779 mixed
unresolved symbols, zero duplicate strong providers, and candidate SHA-256
`2e08358562fa3287007831b0e74b320657d74bd73694325afacb60824d8ef788`.
All seven named new entry providers above are defined and neither CMSIS queue
child is an unresolved import. This is a source candidate, not a flashable
whole image: the mixed unresolved set still includes live RAM/product data,
resident/runtime lower interfaces, and other true code providers. The
dashboard current layout RAM, decoded protobuf RAM and ready byte, settings
record, two BLE thread states, and final section placement remain external
ownership or hardware gates.

The thread-pool worker 0x49110c now has a full C loop. The selected pool
constructor requests 20-byte queue items, proving that the native queue-get
call fills the callback pointer and four arguments in one stack record.
Sixteen actual compiled C/native first-dispatch cases match preliminary
failed/null receives, callback register arguments, and diagnostic calls.
The rollback mutex delete call is source-defined from the actual native
osMutexDelete entry 0x44986e (an older caller comment named an interior
address 0x449852 and is corrected). Eight stock/C cases match its IRQ,
tag-bit, null, and selected queue-delete effects. Coherent Main at
`peripherals-pool-rollback-round` has 2622 defined, 777 mixed unresolved,
zero duplicate providers, SHA-256
`2b7c089e580be873c0367654dd89956c8d364add75998c0cee1a5e33f6c22701`.

The thread-pool queue and thread attribute records at native 0x77ccac and
0x75bd00 are now semantic typed C data. The six queue fields bind the exact
name `threadpool_Queue`, 0x50-byte control RAM, and 0xbb8-byte message RAM;
the nine thread fields include the native priority 0x2b and 0x1000 stack
size. The constructor still supplies per-thread name/control/stack pointer
fields at runtime. A target object check verifies record sizes 24/36 bytes,
all constant fields against native, and three actual pointer relocations.
The two RAM backing extents remain typed linker placement contracts, and
neither this source data nor the pool runtime is physical-hardware proof.

Two additional native byte getters are source-defined: settings terminal mode
0x46c630 reads the shared settings record at offset 0x1d, while device role
0x45a568 reads live cell 0x20075024 already used by the selected service
mode getter. Each matches all 256 possible byte values in actual compiled
C/native comparisons. The coherent Main archive at
`peripherals-settings-getters-round` has 2626 defined symbols, 775 mixed
unresolved symbols, zero duplicate strong providers, and candidate SHA-256
`29d27586e144318a3ba715d68dbe0695e8b5c5432b6e281589dc22144f7f09f5`.
The code bodies are completed at this bounded source/oracle level; live RAM
initialization, the final image layout, and hardware effects remain open.

At this receipt, scanning the Audio C corpus for unresolved symbols declared
as direct external functions yields 119 distinct names (47 `audio_uart_*`,
50 `audio_ble_*`, 22 others). This is a scoped callable-interface census,
not 119 independently recoverable bodies: some names are runtime/resident
contracts, and callbacks in data tables or Main sources are outside this
declaration scan. The 775 total mixed imports must not be interpreted as a
body count. Prominent remaining direct callable groups include BLE ANCC,
Cordio L2CAP/HCI handlers, display layer/transport effects, time/delay
contracts, OTA receive timeout, and allocator/logger lowers. Product RAM
placement and initialized data ownership remain separate work.

The Cordio L2CAP callback cluster now has source-defined flow, default
control/data/CID, ACL dispatch, and signaling receive bodies. The native
flow callback 0x530aa4 uses an ARM entry branch to preserve inherited R3;
72 actual compiled-C/stock cases match callback mutations and returns.
Default data 0x530538 and CID 0x530640 retain repeated live log-enable
reads and match 42 native/C diagnostic cases. The default control callback
0x53076c is the authenticated empty `bx lr` body. The ACL callback
0x5308e6 routes CID 4/5/6 and arbitrary CIDs through the initialized
table, logs malformed lengths, and always calls the selected WsfMsgFree;
24 native/C cases match routes, diagnostics and release. Signaling receive
0x53076e dispatches master/slave role callbacks and authentic invalid-role
diagnostics; 28 native/C cases match. The live log-enable cell at native
0x2007502f remains an external RAM contract. Target Cortex-M55 C
compilation passes with `-Werror` for these sources. These bounded
checks do not establish callback return values that callers ignore,
device execution, or final image placement. Remaining connected L2CAP
children include master/slave signaling handlers and WsfTrace formatting;
other Main/Audio callable and product-data frontiers remain open.
The final coherent Main candidate at `peripherals-l2c-signaling-round` compiles
and relocatably links with 2635 defined symbols, 769 mixed unresolved imports,
zero duplicate strong providers, and candidate SHA-256
`8e9680457aec5ac69bd6dab73ef796f65c3a02fba66100d03371b838ad8d228b`.
This is a source-link checkpoint, not a finished firmware image.

The native master/slave signaling receive callbacks 0x536fbc/0x536c5c
are now source-defined with complete parsed/invalid branches. The master
path checks the 12-byte command and native connection interval, latency,
and timeout bounds before passing the six-field stack parameter record or
sending an update response. The slave path reads the connection-indexed
live L2CAP state at 0x20073bd8, clears the outstanding identifier,
stops its timer at the state base, then delivers the update confirmation
or command rejection; the invalid path logs and conditionally rejects.
Native disassembly corrected the decompiler's mistaken timer argument:
WsfTimerStop receives the state base, not a pointer inside the packet.
Twenty-five actual compiled-C/native cases match branch effects, state
bytes, diagnostics, and selected child arguments. The source-owned code
compiles for Cortex-M55 with `-Werror`.

The connected signaling response and command-reject children 0x537230 and
0x530ae0, plus 0x530b28 message allocation, are source-defined. They
write authenticated six-byte command headers into a 14-byte allocation
and pass the allocation as L2cDataReq's fourth argument (native R3).
Twelve stock/C allocation-success/failure and packet-byte cases match.
The existing selected WsfMsgDataAlloc and L2cDataReq providers are reused.
The next DM indication/confirmation/rejection children retain incoming
register/stack bytes in their event records; native source shows ambient
fields whose ownership must be resolved before a complete C binding.
The coherent Main candidate at `peripherals-l2c-responses-round` passes
compilation and relocatable link with 2640 defined symbols, 770 mixed
unresolved imports, zero duplicate strong providers, and SHA-256
`0e7e12c6dfe5f06d340c7d8b2baab59397e1005653bdfce6cc93f3fd131e0a5c`.
The three named DM children above and the live L2CAP log-enable RAM cell
remain directly connected imports; the 770 mixed imports are not a count of
missing C bodies.

Three DM event bridge children 0x55bc96/0x56e580/0x56e5a4 are now C
bodies with named ARM entry shims. Their original frames copy incoming
R3, R2/R3, or R5 bytes before replacing the event type/result fields;
the source preserves those ambient bytes and passes the full event to
the real selected callback or the still-unresolved dmConnUpdExecute.
Eighteen actual compiled-C/native cases match event bytes and callback
effects for found/missing connections and varied inherited registers.
This closes these three bridge bodies at the bounded ABI level while
leaving the transitive DM update executor and live callback table as
separate contracts. Native dmConnCcbByHandle 0x4b601c is also source-
defined: it searches exactly three 0x30-byte records at live RAM
0x200712a4, preserves miss diagnostics, and matches 16 actual C/native
cases. These sources compile for Cortex-M55 with `-Werror`.
The lookup-inclusive coherent Main candidate at
`peripherals-l2c-dm-lookup-round` passes compilation and relocatable link:
2647 defined, 768 mixed unresolved, zero duplicate strong providers,
SHA-256 `6a1d0e0075a653eece8713b86d3583b2af525c3e6a156e20649e9e682f54d500`.
The directly connected L2CAP imports now reduce to dmConnUpdExecute
0x4b6532 and the live log-enable RAM cell. Native executor action mapping
indexes `(event[2]&7)` through a pointer to 0x78eff0, where only four
bytes are attributable table data; index 7 reaches adjacent instructions.
The pinned Cordio `dm_conn.c` now authenticates this as the complete
four-byte `dmConnUpdActTbl`, with events 0x70-0x73 and action bytes
0x10/0x20/0x11/0x21. Its API and L2CAP producers set only those four
events; the earlier 0x77 concern is outside the executor's routed event
domain. Native arbitrary-input indexing beyond the four entries remains
an explicit invalid-domain/layout gate. The executor's diagnostic branches
and action-set callbacks are still to be bound. Broader Main/Audio source
and image gates remain open.

The high-connectivity Cordio WsfTrace wrapper at 0x52a63c was already
source-defined as `audio_ble_wsf_trace`. The distinct HCI/L2CAP caller
name now aliases that same entry in the defining object, with no second
body. It reserves the native 1024-byte stack buffer, forwards ARM
varargs to the genuine custom formatter contract 0x473036, sends that
buffer through the selected native print hook 0x4733ee, asserts at a returned count
of at least 1024 with the authenticated `wsf_trace.c` path/line 0x89, and
prints the source-owned newline. Five actual compiled-C/native cases match
lower call arguments, output order, and assertion threshold. The
formatter and print hook are selected source candidates, but their full
grammar/equality and live sink state remain open; these tests substitute
their lower effects and do not prove arbitrary formatting or physical
output. Target Cortex-M55 `-Werror` compile passes.

Native ANCC message dispatcher 0x4bf780 is now a C body with all nine
event classes and the role/action/delayed-event branches represented.
Fifty-four actual compiled-C/native cases match child call order and
arguments. Its service-context argument now reads the existing typed
0x200748a0 pointer cell. The four connected state children
0x4bea04/0x4bea14/0x4bea24/0x4bea36 (open, close, active query,
action-list pop) are complete C bodies using the authenticated 64-entry
12-byte ANCC list and selected reset child. Sixteen compiled-C/native
cases match RAM and reset effects, including empty, first, second, and
unrelated list entries. Cortex-M55 `-Werror` compile passes. The coherent
Main candidate at `peripherals-ancc-state-round` compiles and relocatable
links with 2653 defined symbols, 769 mixed unresolved imports, zero
duplicate strong providers, SHA-256
`aa15a6831cf908911693b26d0077d9a592b13748f0a5211c99d947704d97dabe`.
Remaining direct ANCC code children are delayed notification, attribute
write, and value update. Five ANCC cells (state, cache, controller, mode,
service context) remain live RAM contracts; the last three have selected
initializer producers but final allocation/placement is still open.

The remaining three directly called ANCC bodies are now source-defined:
0x4bea7a delayed message generation, 0x4beae8 19-byte ATT attribute
request, and 0x4befce value-update gating. The native packet bytes,
log strings, 5-second wrap-safe tick comparison, transfer guards, and
WSF allocation/send effects are represented. Thirty-nine actual compiled-
C/native cases match their bounded effects, including no allocation,
logging masks, no handle, all three ANCC handles, OTA/EFS blocks, and
connection-age sides. Target Cortex-M55 `-Werror` compilation passes.
The pre-executor coherent Main candidate at
`peripherals-ancc-complete-children-round` passes with 2656 defined,
771 mixed unresolved, zero duplicate providers, SHA-256
`0b15d14d2b0949e3bd5fd7062651541cb942ffe31bff8596845f78799f3d1cab`.
New genuine child 0x4bee5a handles notification payloads; enabled,
EFS-transfer, and connection-tick cells remain live typed RAM.

The pinned Ambiq Cordio `dm_conn.c` and native four-byte extent at
0x78eff0 jointly authenticate `dmConnUpdActTbl` as 0x10,0x20,0x11,0x21
for routed events 0x70-0x73. The source now owns that const table and
native 0x4b6532 dispatch over the source-owned DM action-set RAM,
including absent action sets. Eight actual compiled-C/native cases
match ordered trace and callback effects for the four events with action
sets present/absent. The native diagnostic macro is a typed unresolved
lower; arbitrary invalid event indices depend on adjacent stock layout
and remain a separate typed contract. This is an experimental valid-
event provider, not a full arbitrary-input/equality claim.
The executor-inclusive coherent Main candidate at
`peripherals-ancc-dm-executor-round` passes compilation and relocatable
link: 2658 defined, 773 mixed unresolved, zero duplicate strong providers,
SHA-256 `2b9a0f5702a794b36003e5b0915de72b72566b61d12b5b0f357066c7f15c886e`.
The three new executor imports are the genuine diagnostic prelude,
invalid-action diagnostic, and invalid-event layout contract; the last
is outside the authenticated 0x70-0x73 routed domain. ANCC's next full
source body is the native notification-value handler 0x4bee5a, whose
connected action-list push, remove callback, and attribute parser need
separate reductions. Mixed imports are not a missing-body count.

The next connected ANCC graph is source-defined at 0x4bee5a
(notification value), 0x4bec20 (64-row action-list push), 0x4bee0a
(remove callback), and 0x4bf228 (attribute parser). The parser preserves
state 0/1/2 transitions, 512-byte cache append/overflow behavior,
attribute counting and callback order, four whitelist classifications,
notification result/reset branches, and authenticated diagnostics.
Actual compiled-C/native comparison passes 19 notification/list cases
(including log-mask paths) and 32 parser state/cache/callback cases.
Cortex-M55 `-Werror` compile passes. The coherent Main candidate
`peripherals-ancc-notification-parser-round` passes target compilation
and relocatable link with 2662 defined symbols, 777 mixed unresolved,
zero duplicate strong providers, SHA-256
`f86c375b863b10361c70fbf044d815467b5a0a56168d8cf4b760c9e3b5434db4`.
The directly connected parser imports now are whitelist type 0x4d67b8,
not-whitelisted encoder 0x4d71bc, send-complete 0x4bedac,
attribute callback 0x4bf06c, and perform-action 0x4beb82. The ANCC
state/cache/controller/mode/service pointer, enable byte, and connection
tick remain typed runtime-data/placement contracts. The 777 mixed
imports include unrelated data, ROM, hardware, and tool contracts; they
are not the count of missing ANCC or Main bodies.

The five direct ANCC parser child bodies are now source-defined:
whitelist lookup 0x4d67b8, not-whitelisted nanopb notification
0x4d71bc, send-complete 0x4bedac, attribute callback 0x4bf06c,
and six-byte perform-action ATT request 0x4beb82. Native RAM record
strides, product whitelist count/flags, the 0x9c-byte protobuf packet,
selected Nanopb stream/encoder calls, ATT payload, and authenticated
logging branches are represented. Actual compiled-C/native cases pass
35 whitelist, 20 protobuf allocation/encode/send/error, and 44
completion/action/callback comparisons. Target Cortex-M55 `-Werror`
compile passes. The coherent Main `peripherals-ancc-parser-children-round`
passes with 2667 defined symbols, 776 mixed unresolved imports, zero
duplicate strong providers, SHA-256
`b912561dcb1b2915617e7feb90313abc8d88604df1163034859f9d1207ce7562`.
Direct ANCC code frontier now consists of app-attribute writer 0x4bebc4
and sync-result callback 0x4bed0e; source-owned protobuf descriptor at
stock 0x7799f4 and live ANCC/whitelist RAM placements are separate data
obligations. The whitelist RAM initializer has not been attributed.

The ANCC app-attribute writer 0x4bebc4 and RX sync callback 0x4bed0e
are source-defined, and the product protobuf descriptor at 0x7799f4 is now a
source-owned typed graph of six records. The descriptor verifier confirms
140 field bytes and all six count/pointer relationships against authenticated
ROM. The writer's ARM entry shim preserves native `push {r4,r5,r6,lr}` plus
64-byte local frame before a C body fills the packet. This matters for IDs
of 62 or more characters: stock skips the copy, forwards existing stack
bytes to ATT, and writes its terminator past the local frame into saved
register slots. The source does the same, without zero-fill or a substitute
ambient provider. Twenty-eight actual compiled-C/native cases match packet
and log effects through 73-character IDs; larger corrupted-return paths are
not claimed as runtime-qualified. The ANCC value handler's state byte now
uses the same typed 0x200036c8 service-state cell as its other consumers;
its 39-case native oracle still passes. The first coherent Main candidate
`peripherals-ancc-app-descriptor-round` passed with 2670 defined, 774
mixed unresolved, zero duplicate providers, SHA-256
`ff7e233cfe25bb3505b256d6271e24877f6a4dc6304c0f5a43d8c063dc13cb91`.

The ANCC writer, attribute request, and action packet now call the already
selected `audio_ble_attc_write_request`, attributed to native AttcWriteReq
0x4b579c. Its length ABI was corrected from `uint8_t` to `uint16_t`, which
preserves ANCC's 64-257 byte packet route. Fourteen actual compiled-C/native
ATT request cases match allocation, packet copying, and send effects at
lengths 0, 6, 19, 64, 255, 256, and 257, including allocation failure.
The ANCC 28/39/44-case oracles still pass after this direct binding. The
source-owned descriptor does not establish final flash placement; live
ANCC state, service context, cache, and whitelist RAM remain typed placement
and initialization contracts. The selected image still has many unrelated
source, ROM, RAM, and hardware imports; ANCC packet proof is bounded to the
fixtures above and is not live-radio or whole-image proof.
The subsequent coherent `peripherals-ancc-attc-binding-round` passes target
compilation and relocatable link with 2671 defined, 772 mixed unresolved,
zero duplicate strong providers, SHA-256
`6b1392bb6679418d7e0808c8826e0562cf8cee0e87a4c0ffe180e6a420f34c9a`.
The former `AttcWriteReq` and invented ambient-write imports are absent.

The separate L2C slave handler/timeout pair at 0x536fa4/0x536b40 is now
source-defined. The handler has a named ARM entry shim for native IAR
`push {r7,lr}`/`pop {r0,pc}` so it returns inherited R7. The timeout
body preserves all five trace-policy reads/compares, source-owned WARN/L2C
strings and path, native log versus WSF trace routing, and DM update
confirmation. Actual compiled-C/native comparison passes 16 cases across
null, non-timeout, and timeout messages with trace/log flags. Cortex-M55
`-Werror` compile passes. The coherent Main candidate
`peripherals-l2c-slave-timeout-round` passes target compilation and
relocatable link: 2673 defined symbols, 771 mixed unresolved, zero
duplicate strong providers, SHA-256
`610b305ba7f4ba496ba551822c579925b6bbda5b9f766e61d53277bb765dcd11`.
The adjacent SMP handler 0x537d0c and BLE registration handler 0x4bae84
remain separate substantive callback bodies. Runtime BLE tables and final
image placement are still open.

The Cordio SMP handler 0x537d0c is source-defined across null message,
DB service event, scratch-buffer release, CCB-active and AES-token match/
mismatch branches. It preserves authenticated WARN/SMP strings, four log
levels, trace fallback, queue dequeue/free loop, and state-machine dispatch.
Twenty-five actual compiled-C/native cases match call order and effects.
The coherent Main `peripherals-smp-main-handler-round` passes target
compilation and relocatable link: 2674 defined symbols, 773 mixed unresolved,
zero duplicate providers, SHA-256
`9a1cdf90e30deeda4e0e4f3d3af134287dc1436d22d21bd69b74b030c0fb9277`.
Two genuine contracts were exposed: SmpDbService code and SMP queue RAM.
The queued-message transport/storage remain live runtime data, not a
source-owned initialized table.

The SmpDbService child 0x542960 is also source-defined: ten 24-byte records,
three unsigned 1000-ms decrement paths per active record, count division
and reload from the authenticated pSmpCfg pointer cell, failure-count
clear, and timer restart. A named ARM entry shim preserves the native
entry-R3 return through IAR's saved-register pop. Twenty actual
compiled-C/native cases match all ten record effects and lower call order,
including zero divisor's ARM SDIV result, multiple active patterns, and
1000/1001 boundaries. Cortex-M55 `-Werror` compilation passes. The
registration pointer remains the selected source-owned pSmpCfg slot with
runtime placement still required.

The data-producer crosswalk then bound the SMP mismatch drain queue at
0x20072cd8 to the already selected Cordio `secCb` object at 0x20072cb8+0x20.
The pinned structure has a static assert for its AES queue offset and the
selected 0x536324 initializer clears it. The ECC request queue at
0x20072ce0 is the same object's public-key queue at +0x28, verified by the
native 0x5367d4 literal and eight actual C/native ECC request cases. The
0x60-byte ECC key storage at 0x200726d0 is source-owned because selected
DmSecSetEccKey writes exactly that extent and DmSecGetEccKey returns its
base; absolute SRAM placement is still open. A coherent Main build
`peripherals-smp-sec-data-round` passes with 2677 defined, 768 mixed
unresolved, zero duplicate providers, SHA-256
`168b8732357f8ef767115d50c2de80071b6c34ba309bb891b3333f2418a6818c`.
The succeeding `peripherals-ble-data-producers-round` additionally defines
the three 16-byte discovery rows at 0x200733fc and 0x80-byte advertising
link state at 0x200719c8, whose reset/initialization writers 0x532e52 and
0x4b3c02 were already selected. That target build passes 2679 defined,
766 mixed unresolved, zero duplicate providers, SHA-256
`d466a18385d62e90c5a58009b3b35f245fc33cebb1e97ea9a12fe58475814916`.
These are mutable RAM objects with source-owned producers, not extracted
fixed ROM data or proof of native placement.

A separate HCI storage audit found the preexisting `audio_ble_hci_state`
array only allocated 0x80 bytes at native 0x20071478, while selected
HciCoreInit 0x52ac02 writes a word at +0xa0 and bytes at +0x80/+0x81.
The native object's proven minimum extent is therefore 0xa4 bytes. Its C
storage was corrected to that lower bound and the unresolved
`audio_ble_hci_controller_state_20071478` name now aliases the same data
symbol in the object, with both symbols at offset zero and size 0xa4 under
the Cortex-M55 compiler. This is exact same-address data ownership, not a
behavioral provider alias; full product object extent and placement remain
unproven. The coherent target build is pending separately.

The last settled unresolved census has 766 mixed symbols. A lexical scan of
extern declarations in selected Audio sources previously classified 112
callable declarations, 611 data declarations, and 49 unclassified of the
772-symbol snapshot before these producer bindings. This classification is
an interface census, not a count of missing complete bodies: some callable
names are ROM/compiler contracts and some data declarations are reused
product cells. The DM connection base 0x200712a4 remains imported despite
its known three 0x30-byte rows: DmConnRegister writes callback slots after
+0x90, so the full containing object extent/initializer still needs a
pinned definition or native startup proof. The HCI callback table at
0x20073870 likewise remains typed because selected writes reach internal
fields but not an authenticated complete object boundary.

The subsequent coherent `peripherals-hci-storage-extent-round` completed
target compile and relocatable link with 2680 defined, 765 mixed unresolved,
zero duplicate providers, SHA-256
`86a174690f416d0e404a5a2ac33557109fe9a4ca7cb5ed5ebd66c9e9d12b92d0`.
Native Packetcraft AppHandler 0x4bae84, its link/reset callbacks
0x4bacc8/0x4bda34, and DmReadRemoteFeatures 0x4b6cb0 are now source-defined.
The AppHandler's four trace branches, event class dispatch, and IAR saved-R0
outgoing varargs effect passed 27 actual compiled-C/native cases. The remote
features CCB/no-CCB and synthesized callback packet paths passed four cases.
The connected HciLeReadRemoteFeatCmd 0x52b352 now uses the already selected
Cordio command allocator/send providers and passed two actual compiled-C/native
allocation/payload cases. `peripherals-app-remote-hci-round` passes target
compile and relocatable link with 2686 defined, 764 mixed unresolved, zero
duplicate providers, SHA-256
`6e511566af12f66cd085c666aa71afd6d024085874e302e57e39e628996a3c92`.
The App UI callback cell and DM connection object remain typed live imports.

A fresh lexical declaration scan of the 764 unresolved names yields 111
callable, 611 data, and 42 unclassified names. This scans declarations rather
than ELF object kind, so the 42 include compiler support and source strings;
the 111 are a callable interface frontier, not a missing-body count. The
largest concrete remaining code groups include Cordio security and discovery,
HCI driver/radio children, UART dispatch and parser descendants, plus
formatting/runtime helpers. The 611 data names include live application,
driver, and RTOS state, callback cells, selected product configuration, and
tables whose full extent or initializer still needs authentication. Whole Main
source closure, exact SRAM/ROM placement, and hardware behavior remain open.

Native HciDrvHandlerInit 0x4b4a7c is now source-defined with its handler-ID
write and the two timer event/type fields. Four actual compiled-C/native RAM
effect cases match for handler IDs 0, 1, 127, and 255. The primary timer
reuses the existing typed 0x20073e64 import; the adjacent second timer at
0x20073e74 remains a separate typed live object, without assuming either
timer's full extent or startup state. `peripherals-hci-driver-init-round`
passes target compile/link with 2687 defined, 764 mixed unresolved, zero
duplicate providers, SHA-256
`dab90856341b76b0dcc6123f0d6e4f4882128dbb268fddbfc162e845fa03b5bd`.

The native AppDbDeleteAllRecords 0x47acf8 and connected
`_evenEraseAllBondInfo` 0x4787a4 are now source-defined as a connected C
candidate. The parent clears ten exact 200-byte privacy rows (first six bytes
through the selected zero provider, plus fields +0x2f/+0x30) and preserves
the diagnostic call order and IAR saved-register return effects. The child
performs cache maintenance, clears the live staging buffer using a live
16-bit size cell, saves/restores ARM PRIMASK, and calls the selected NVM word
writer with the authenticated key, MRAM destination, and size/4 count. Its
success/failure diagnostics use authenticated strings and flags. Forty actual
compiled-C/native cases match record/staging effects and lower call order
across sizes 0/64/128/252, flash results 0/failure, and log masks 0/1/2/4/7.
This does not prove malformed size beyond the staging object's available
extent, flash hardware, or final address placement. Rows, staging buffer,
MRAM mapping, and size cell remain typed live contracts.
`peripherals-privacy-erase-round` target compile/link passes with 2691 defined,
765 mixed unresolved, zero duplicate providers, SHA-256
`443bfa5448adc742b594b20518d6eb3d0c4e7909aba8518d97a95758c6244b6c`.
The fresh lexical interface census is 109 callable, 614 data, 42
unclassified; the extra data names are now explicit staging/size contracts.

The connected Cordio `smpScAuthReq` callback 0x5e2aba now has a source C
body and a named ARM entry frame. The frame preserves the native 24-byte
incoming stack contents and writes only the native defined event bytes:
connection, event 0x2e with the two callback values, or event 4 with the
three zero fields and byte 20 set to 3. It selects the existing
DmSmpCbackExec or smpSmExecute providers using the authenticated CCB context
and auth bit. Twelve actual compiled-C/native cases match full event-frame
bytes and callback selection across both context states and auth bits. The
coherent `peripherals-smp-sc-auth-round` target build passes with 2693 defined,
764 mixed unresolved, zero duplicate providers, SHA-256
`80958f5c9bddf4fa6ca86683605597bdfa1c890c1753e95a8e8adccaeb795e4f`.
The larger `smpScProcPairing` 0x5e2784 processor remains the adjacent true
code frontier, with its selected scratch and state-machine children but live
SMP configuration/state data still requiring exact ownership proof.

The adjacent `smpScProcPairing` 0x5e2784 processor is now source-defined too.
Its named ARM entry keeps the native saved-R2/R3 frame for the outgoing event;
the C body covers MITM/passkey selection, SC enablement, scratch allocation,
three 32-byte ECC key copies, legacy branch, key-size/config rejection, and
security-level state update. It reuses already selected Cordio children and
the live pSmpCfg pointer cell. A 256-case actual compiled-C/native comparison
(56 branch fixtures and 200 deterministic varied cases) matched CCB and SC
state bytes, both outputs, complete 24-byte outgoing event frames, key-copy
buffers, return R0, and child-call order. Product configuration values and
state placement remain external contracts. The coherent
`peripherals-smp-sc-pairing-round` target compile/link passes: 2695 defined,
763 mixed unresolved, zero duplicate providers, SHA-256
`687286ba043e586008812a0213b6e369f4fbe5c2525eb8330580ab68562babcb`.
The fresh unresolved lexical census is 107 callable, 614 data, and 42
unclassified names (763 mixed). These are interface classes, not a count of
remaining complete native bodies. DM CCB full containing-object extent, HCI
callback state extent, privacy staging/size/MRAM runtime ownership, pSmpCfg
values, and final image placement remain concrete source/data obligations.

The legacy `smpAuthReq` callback 0x56e84c is now source-defined with the
native 24-byte stack frame; 12 actual compiled-C/native cases match full
frames and callback selection. An initial legacy pairing addition exposed an
already selected provider for `smpProcPairing` 0x56e6e0 at target link time.
The duplicate unit was removed and that selected source was corrected to
preserve the native saved-R2/R3 event frame, including ambient bytes outside
the four written failure-event fields. Its full CCB/output/event effects and
return R0 match 256 actual compiled-C/native fixtures. The corrected coherent
`peripherals-smp-legacy-corrected-round` passes target compile/link with
2698 defined, 762 mixed unresolved, zero duplicate providers, SHA-256
`01d93c60b64f7f70eb644649cdc6152345f28ae6eba58c4d9c2c0597fb1204c4`.

The authentic AppUiDisplayPasskey 0x4bd7fa and
AppUiDisplayConfirmValue 0x4bd91e diagnostic bodies now source-own their
NUL-terminated module/path/function/message strings, reproduce the native
trace level and extended logger selection, retain the incoming fourth ARM
register for level-one varargs, and invoke the live UI callback at the
authenticated cell +4 when registered. A named entry frame restores the
native R0-R3 outcome, including IAR outgoing stack arguments after an
enabled extended log. Eighty actual compiled-C/native cases match logger,
trace, callback, and return effects across five trace levels, two log masks,
and present/absent UI callback; an unused extra stack word at non-level-one
log calls was excluded from comparison because that argument is not consumed.
`peripherals-pair-ui-diagnostics-round` target compile/link passes with 2701
defined, 760 mixed unresolved, zero duplicate providers, SHA-256
`4f4155a8f3a4b8aece23ea2281894df3f51f1f9567fa5512ae43bb14911c0fb9`.
The fresh lexical interface census is 104 callable, 614 data, 42
unclassified. The UI callback cell remains live runtime state; source strings
alone do not establish its registration or final placement.

The connected TPL transport graph now has six additional native-backed C
bodies: `TPL_Init` 0x4b892c, `tpl_context_free` 0x4b8ba2,
`_rxNextPacketTimeout` 0x4b8c6c, `TPL_RxPacketTimeoutHandler` 0x4b8da2,
`_tplReponse` 0x4b9012, and `tpl_schedule_rx_timeout` 0x4b8c44. The
initializer source-owns the authenticated four-by-56-byte context clear and
send-mutex pointer cell. Service registration rows, response buffer,
three-byte delayed argument cell, and BLE controller are typed live RAM
contracts; their complete producer/extent and final addresses remain open.
The response source preserves the native IAR saved-R1/R2 return and outgoing
logger stack words through a named ARM entry shim; the scheduler similarly
preserves its inherited R3 return. Actual compiled-C/native comparisons pass
80 initializer cases, eight context-free cases, 18 timeout-callback cases,
20 timeout-handler cases, and 32 response cases covering buffer bytes,
callback-null/nonzero-pipe paths and R0/R1 results. Enabled response logger
and schedule effects remain source/static qualified rather than dynamic
equivalence claims. The coherent `peripherals-tpl-response-round` target
compile/link passes with 2713 defined symbols, 762 mixed unresolved and zero
duplicate providers, SHA-256
`2b3cb7ade39662bd4050c4ed77c8c6bdfc04f51699dbdb0a1bff1f98de38e90f`.
The TPL-local unresolved names include genuine live data
`audio_tpl_response_buffer`, `audio_tpl_service_table`,
`audio_tpl_timeout_ids` and next true code child
`tpl_reset_receive_contexts_004b9984`; these are not counted as six
completed product runtime objects or a complete Main image.

The next true TPL child `tpl_reset_receive_contexts` 0x4b9984 now removes
its authenticated delayed callback and releases each active row of the
source-owned context pool. All 16 active-row masks match original execution
against actual compiled C in call order and callback/row pointers. The
coherent `peripherals-tpl-reset-round` target build passes: 2714 defined,
761 mixed unresolved, zero duplicate providers, SHA-256
`28a96d4ff313068d023cf85ca076a7ea7f4688cf700432e18bdffba49abb9953`.
The TPL-local remaining unresolved names are three live data contracts:
`audio_tpl_response_buffer`, `audio_tpl_service_table`, and
`audio_tpl_timeout_ids`; final placement and their actual initialization are
not established by this source closure. Main as a whole remains incomplete.

A focused TPL storage xref audit found exactly one absolute ROM pointer to
response-buffer RAM 0x20004204 (`0x4b99ec`) and delayed-argument RAM
0x20074b04 (`0x4b9618`), and two to the service-table base 0x20071414
(`0x4b90e8`, `0x4b9a30`). The second service-table pointer lies in the
transport literal/data region. `TPL_Init` supplies an authenticated row
registration writer, but its byte service-index range does not by itself
prove a safe table extent. No initializer for the response buffer or delayed
cell was established. Those live-data definitions remain external.

The connected BLE slave MTU request parent `_bleSlaveRequestMtuExchange`
0x46dedc and pinned Cordio children `AttGetMtu` 0x4b5204 and `AttcMtuReq`
0x4b57fa are now source-defined. The parent uses the selected 0x20074330
slave-context pointer cell, writes the native MTU field at +0x22, preserves
both authenticated diagnostic branches with source-owned strings, and asks
for MTU 0xf7. The getter keeps the native ambient high R7 return word; the
request keeps incoming R3 on allocation failure and clears its saved word on
success. The children reuse selected ATT CCB lookup, message allocation,
and ATT client send providers. Twenty actual compiled-C/native parent cases
match the 64-byte connection row, child call order and args, and R0/R1 return
for five connection values and four current MTUs with logging disabled;
child packet paths and enabled diagnostic effects are static/source
qualified, not covered by that dynamic comparison. The coherent
`peripherals-slave-mtu-round` target compile/link passes with 2720 defined,
760 mixed unresolved, zero duplicate providers, SHA-256
`2ceced0ccce23f66347093bc0765dc41f685ec67ebab29ad4470c47907eef205`.
The live containing slave-context allocation/initializer and final placement
remain open, as do the wider Main/Audio source and runtime gaps.

The adjacent slave security request `_bleSlaveSecReq` 0x46df7e, native
Cordio policy child 0x4b4684, and `DmSecSlaveReq` 0x52bb00 are also
source-defined. The policy child reads the already selected live
0x20074358 profile pointer cell, requests security only when the selected
connection security level is zero, and allocates/sends the authenticated
six-byte event layout. The parent owns its two stock diagnostic strings and
preserves the native six-word ARM return frame. Twenty actual compiled-C/
native fixtures match connection truncation, level/allocator branches,
message bytes, call order, and R0/R1 return with logs disabled. Enabled
logging is source/static qualified; runtime profile-table initialization
remains a separate product contract. `peripherals-slave-security-round`
passes target compile/link with 2725 defined, 759 mixed unresolved, zero
duplicate providers, SHA-256
`0749ab825ee441ea61ec5ed23df1c301605344f0f9b9303da266b92e7d57fec0`.
This is a connected BLE slave source chunk, not full Main source completion.

The slave disconnect dispatch 0x4bb04a and Cordio `DmConnClose` 0x4b6c82
now use C bodies and the selected live dmCb handler byte at +0x0c. The
native 36-byte allocated event writes connection, event 0x19, reason 0x13,
and mode 3 at their authenticated offsets; the outer named ARM entry returns
the inherited R7 word. Ten actual compiled-C/native cases match allocation
failure/success, packet bytes, handler argument, call order, and return for
five connection inputs. The coherent `peripherals-slave-disconnect-round`
target compile/link passes with 2728 defined, 758 mixed unresolved, zero
duplicate providers, SHA-256
`2db0c09fc62c2a03779efbd16711faa2dcde9c003ca9003009913607904c910c`.
The live dmCb object remains a product runtime/placement obligation and the
wider Main source graph remains unfinished.

The next BLE slave callback graph is now source-defined:
`dmSlaveAdvStopOnDisconnect` 0x46dfd0, `GattValueUpdate` 0x4b5a1e, and
the Cordio discovery callback 0x533630. It reuses the selected source-owned
three-by-16-byte discovery rows at native 0x200733fc and selected restart
provider; the slave subcontext pointer cell at 0x20074334 remains live
runtime state. Thirty-two actual compiled-C/native cases match the outer
R7 return and restart-call effect across disconnect flag, connection handle
match, action 4 versus other, attribute range hit/miss, and row suppression
flag. The coherent `peripherals-slave-adv-stop-round` target compile/link
passes with 2733 defined, 757 mixed unresolved, zero duplicate providers,
SHA-256
`df811867ec9bf865919b313db8af6ab7b026ce34c72f5de1c2102e2f42059710`.
A fresh lexical scan of unresolved names against `extern` declarations in
all component and firmware C sources yields 97 callable, 653 data-like, and
seven unclassified (757 total). This method includes inactive candidate
source declarations and classifies function-pointer externs as data-like, so
these counts are not directly comparable with earlier selected-source scans
and are not missing-body counts. Remaining work spans genuine callable
interfaces, product runtime/data ownership and full extents, ROM string and
configuration ownership, complete image placement/link, and hardware proof.

The next pinned BLE stack callback 0x536470 and its exact 16-byte copy
child 0x542a44 are source-defined. The callback writes message+16 into the
message's +4 pointer field, copies payload+5 into that 16-byte span, and
sends the message through selected WSF. Its ARM shim retains the native
saved-R3 result. Twenty actual compiled-C/native fixtures match the full
40-byte message, copy offsets/count, WSF handler/argument, and R0 return for
five payload seeds and four handler IDs. The coherent
`peripherals-stack-callback-round` target compile/link passes with 2736
defined, 756 mixed unresolved, zero duplicate providers, SHA-256
`ed5b758f1a3b88b7ea79c8960e2c6c1261cdb81a9ad7d240b05a911a548f3695`.
The neighboring callback 0x536620 has an authenticated native state switch
and three called children 0x5364a4/0x5365a6/0x536608 whose retained
high-level decompilation is absent; they are a concrete next native-source
frontier rather than a reason to claim stack callback subsystem completion.

The connected BLE stack state graph is now source-defined through callback
0x536620, state-zero 0x5365a6, state-one 0x5364a4, state-two 0x536608,
and their exact 16-byte shift/XOR helpers 0x53655c/0x542a60. The state-one
path reuses the already selected `SecLeEncryptCmd` 0x5363ae, WSF queue,
and HCI encryption providers. It assembles a final padded block when the
signed remaining count is below 17, XORs the chaining block, advances the
16-bit offset, and submits the authenticated reversed key/plaintext path.
Actual compiled-C/native comparisons pass 12 callback state/null cases, 12
state-two handoff cases, 32 state-zero shift/transition cases, and 32
state-one valid-range block/crypto cases. The C compiler inlined the XOR
helper in some fixtures; the oracle compares the resulting block and crypto
arguments rather than requiring an artificial call. Negative or oversized
remaining counts that would overrun the native 16-byte stack block are outside
this bounded runtime comparison and remain a source/ABI safety gate.
Coherent target snapshots passed throughout; latest
`peripherals-stack-state1-round` passes with 2745 defined, 755 mixed
unresolved, zero duplicate providers, SHA-256
`a6d20133cf6c6af66d154ba426310790bbe839fc42305665a2cf310c26a048d7`.
The local state-graph code frontier is closed; the remaining
`audio_ble_hci_stack_state_20073870` is live controller RAM, not a missing
child body. Native callback 0x536234 and later stack callback 0x5366dc remain
separate larger source frontiers. Full Main source/layout and hardware proof
are still open.

The native stack key/command callback 0x5366dc is source-defined with its
0x25 dual 32-byte reverse copies and 0x26 special-status/normal paths.
Forty-eight actual compiled-C/native cases match full message bytes, reverse
call spans, and WSF sends across four opcodes, two statuses, three payload
seeds, and two handlers. The coherent
`peripherals-stack-callback-5366dc-round` target build passes with 2746
defined, 754 mixed unresolved, zero duplicate providers, SHA-256
`15db3f37079c92639fef218fb4ddddba027c39c095969f10fbbd526ff02af9a2`.
The remaining direct stack callback is native 0x536234. An updated lexical
all-component extern scan of 754 mixed unresolved names gives 94 callable,
653 data-like, seven unclassified; this remains an interface classification,
not a missing native-body count. Live controller RAM, TPL RAM ownership,
ROM/config data, whole-source coverage, final layout, and hardware proof
remain separate gates.

The final direct BLE stack callback 0x536234 is now source-defined together
with authentic WsfMsgDeq 0x4bf9ec and WsfQueueDeq 0x538c4a. It handles the
0x1c four-slot 8-byte rotation, 0x1b/0x25/0x26 queue selection, conditional
16-byte reverse, 0x14 three-queue drain/free, and the live callback table
at secCb +0x3c indexed by message state. Null dequeue on 0x1b retains the
native dereference behavior. The event/queue oracle exercises actual native
and compiled C queue transitions with controlled single-node heads and
matches 48 combinations of event, state, and rotation index. It exposed an
initial C selection of the +0x2c tail word for event 0x26; corrected source
selects the native +0x30 queue and the comparison passes. The fresh
post-correction `peripherals-stack-callback-536234-corrected-round` target
compile/link passes with 2749 defined, 753 mixed unresolved, zero duplicate
providers, SHA-256
`8851cc0083c2276295ed5b995b02ac64fbaa34c616583facc44078eb31981c2d`.
All four direct BLE stack callbacks 0x536234/0x536470/0x536620/0x5366dc
now have C source and bounded effect comparisons, but broader stack runtime,
product data, exact image layout, and device behavior remain open.
### Radio revision and identifier source round (2026-10-12)

The Main/Audio selected candidate now has native 0x4b47cc as `display_ble_hci_radio_revision_mismatch.c`: it compares bytes 3 through 0 in order and logs through the existing 0x4733ee provider. Its exact two source-owned strings come from literal pointer cells 0x4b4d44/48. The second formatter argument is the required revision left in native R2, not an invented value. `verify_ble_hci_radio_revision_mismatch.py` passed 22 actual compiled ARM C/native decisions, string bytes, and R1/R2 logger arguments. The coherent selected candidate was 2750 definitions, 752 unresolved, zero duplicate providers, SHA-256 `2ea0cc372f43919b9c51c139fedf0bc70c0214a9df15d1a9e5b37488423e1a0a`.

Native 0x480d72 is source-defined in `display_ble_hci_radio_identifier.c`, including all mode-0 register bits, mode-1 dispatch and invalid/null status. `verify_ble_hci_radio_identifier.py` passed 28 actual compiled C/native mode and byte-effect cases. Its mode-1 child 0x480874 is source-defined in `display_ble_hci_radio_identifier_details.c` with source-owned bounded 4- and 12-entry halfword tables at 0x78c97c/0x774bac; `verify_ble_hci_radio_identifier_details.py` passed 16 compiled C/native MMIO readout and delay cases. The details snapshot was 2752 definitions, 752 unresolved, zero duplicate providers, SHA-256 `d6fef05e04beaefda4bb80c554949ba1f524892e553b20a4a8366e16197a3e1f`.

Mode-0 capability child 0x480c7c is source-defined in `display_ble_hci_radio_identifier_caps.c`. The dispatcher explicitly forwards its native R2 output-pointer seed as the child's third ABI word; the child calls the real 0x4d3f3c hardware-read contract, retains its output word on failure, and updates the four-byte field. `verify_ble_hci_radio_identifier_caps.py` passed 90 compiled C/native revision, hardware-status, and output-word cases with the hardware read hooked to the same effect. Hardware selector 0x4d3f3c and full region reader 0x4d3dda are source-defined in `display_ble_hci_radio_read_word.c`/`display_ble_hci_radio_read_region.c`, including real MMIO controls, limits, source address arithmetic and selected `platform_copy_words`. Their actual compiled C/native oracles passed 256 selector branches and 336 region/copy cases. The coherent selected region graph passed 2755 definitions, 751 unresolved, zero duplicates, SHA-256 `1dbaba1da3b60ab6e691cee4146971456fe12558f3ff360a759444ed44e078f6`. Physical MMIO and copy effects are not hardware verified.

The 0x48162c HCI dispatch-table register body is source-defined in `display_ble_hci_radio_register.c` against two typed writable table bases at native 0x20068228/0x20068928; their startup initializer and final placement remain open. `verify_ble_hci_radio_register.py` passed 35 actual compiled C/native target-mode and table-write cases, including target 2 writing both planes. The settled selected graph passed 2756 definitions, 752 unresolved, zero duplicates, SHA-256 `330f89654cb2ff5303841d97228550ced44b42eb0f6f91b795e489e70f314fcd`. A relocation-based census of this graph found 92 directly branch-referenced and 660 only address-referenced unresolved symbols. This is a *relocation classification*, not a missing-body count: address references include callable callback pointers as well as RAM/ROM data, and directly branched symbols include resident/runtime contracts. The mixed count rose by one because the register body replaces one code import with two live table-base imports. Whole Main source, storage initialization, final placement, formatter grammar, and hardware behavior remain incomplete.
### Radio pin-function configuration and shared logger identity

Native 0x4c2b68 is source-defined in `display_ble_radio_power_config.c`: all sixteen active group/setting branches, ordered selected 0x480f0c pin-function calls, and authenticated live RAM value cells (literal pointers 0x4c3228..0x4c36a4) are represented. It does not supply values for those cells. `verify_ble_radio_power_config.py` passed 45 actual compiled ARM C/native call-sequence cases over all group numbers 0..8 and representative settings 0, 1, 2, 3, 255. The coherent selected graph passed 2757 definitions, 751 unresolved, zero duplicate providers, SHA-256 `639119c062941e502426fcebc68cbfb6a1a1c43f487406550e71807498334dc7`. Live pin values and physical pin configuration remain runtime gates.

The unresolved vendor log-flags name in three HCI sources was traced to native 0x43d0ce, already selected as `audio_log_flags`/`platform_log_flags` in `simple_ram_getters.c`, which reads exactly RAM byte 0x20004543. Those three callers now bind the existing same-address source provider. This is a provider-identity correction, not a new logger body; the selected direct 0x43d574 extended logger remains incomplete for the general formatter/fatal/output domains described elsewhere in this report. Fresh selected candidate `peripherals-radio-power-log-flags-round` passed 2757 definitions, 750 unresolved, zero duplicates, SHA-256 `15f399b0e71f21b8cb3398d1adc1bd1185d1b4ae9c367c3c1cd3e740708237ec`. Its relocation census has 90 directly branched and 660 address-only unresolved symbols, subject to the same callback-pointer/data distinction above. Exact native literal searches find the two radio dispatch table bases 0x20068228 and 0x20068928 only at literal cells 0x481810/14; no attributable per-table initializer has yet been found, so the writable storage extent and startup contents remain an explicit placement/data gate.
### TinyFrame ID-listener and queue logger identity

Native TinyFrame `TF_AddIdListener` 0x4918c2 is source-defined in `frame_extra_listener.c`: it scans all 128 24-byte entries, fills the exact ID/handler/context/sequence fields, advances the occupied count, and preserves the full-table extended and compressed diagnostic branches with authenticated source strings. `verify_frame_extra_listener.py` passed 12 actual compiled ARM C/native cases, including first/middle/last insertion and all eight diagnostic flag combinations on a full table. The input-event queue failure call at native 0x4733ee now binds the already selected same-address `audio_ble_hci_boot_log_4733ee` provider; this is an ABI identity correction, with its general unbounded formatter still a real lower gate. The coherent selected `peripherals-frame-extra-listener-round` passed 2758 definitions, 748 unresolved, zero duplicates, SHA-256 `2acbb8ab5968e8f50fe8e2561712e7c2223de54241ca4a8d163c44e1328846e1`. These source-body reductions do not establish final TinyFrame RAM initialization or physical display/transport behavior.
### Task-vote runtime graph

`task_vote_runtime.c` source-defines six native task-vote bodies: 32-slot find/find-free 0x46d67c/0x46d69a, acquire/release for handle 0x46d70e/0x46d78c, and current-task entrypoints 0x46d816/0x46d826. It binds the already selected current-task pointer read and architectural PRIMASK save/restore sources; the single 0x105-byte live state extent at native 0x200700e0 remains an explicit writable product-data/initialization contract. `verify_task_vote_runtime.py` passed 30 actual compiled ARM C/native lookup and state-transition cases across disabled, empty, existing active/inactive and full tables. The oracle cuts PRIMASK restore because Unicorn does not execute that instruction in this setup, so it compares RAM/return/call effects, not physical interrupt state. The coherent selected `peripherals-task-vote-round` passed 2764 definitions, 747 unresolved, zero duplicate providers, SHA-256 `156ed75c55b86f3f93ebfe712198691d92d8480069d71d3df7db6b7a76de3737`. Literal search finds 0x200700e0 only at pool cell 0x46d878; no independent startup initializer/placement proof was established. Full display thread, formatter, product RAM layout and live hardware remain open.
### Freestanding runtime and OTA/wear getter bindings

`freestanding_memory.c` supplies real C byte-copy/clear bodies for unresolved `memcpy`, `memset`, `__aeabi_memcpy`, `__aeabi_memclr`, and `__aeabi_memclr8`. An ARM EABI target object had all five providers with no undefined references; a host effect check passed 16 lengths (0..255) for byte content, untouched tails and standard return pointers. This qualifies the source/runtime contract, not original stock byte identity or overlapping-copy behavior. The coherent selected `peripherals-freestanding-memory-round` passed 2769 definitions, 742 unresolved, zero duplicates, SHA-256 `69c61ea4cb23334da0eae1a1c449b04d20eb8466db1a3b0d3a52ba470db5dc08`.

Native `ble_ota_mode_get` 0x46efec is source-defined in `display_ble_ota_mode_get.c` as the raw shared live byte at 0x20074f8b, already used by the slave unpair path. `verify_ble_ota_mode_get.py` passed all 256 actual compiled ARM C/native byte values. The two wear-status callers now bind selected `audio_log_wake_allowed`, whose source is the same native 0x443484 predicate reading 0x20074f2c; this is same-address provider reuse, not new behavior. The coherent selected `peripherals-ota-wear-round` passed 2770 definitions, 740 unresolved, zero duplicates, SHA-256 `1d0ed2fd478ad1d890b114d2275fac12427e28a85da336254a25fea64e949d00`. Both RAM bytes retain live producer/initialization gates.
### TLSF realloc source closure

`tlsf_reallocate.c` source-defines native realloc 0x4d0868, used-block trim 0x4d03f0, and predecessor-free flag clear 0x4cfdf6 from the pinned TLSF block ABI. The realloc body covers null/zero requests, size adjustment, free-neighbor growth, fallback allocation/copy/free, and used-block trimming with the selected real TLSF helpers. It source-owns the two authenticated assertion strings and source path from literal cells 0x4d09b0/0x4d097c/0x4d09a0. `verify_tlsf_reallocate.py` passed seven actual compiled C/native branch/call cases; `verify_tlsf_trim_used.py` passed four actual compiled C/native split/error/flag cases. Child effects were cut symmetrically, so the checks qualify composition, not physical heap persistence or all allocator layouts. The coherent selected `peripherals-tlsf-reallocate-round` passed 2773 definitions, 739 unresolved, zero duplicate providers, SHA-256 `22804956fdf06da49d363d0f2ee12373fac8ba4fc4071b1ad230e2a67bee4fa0`. Whole Main source, initialized heap/pool state and final layout remain open.
### Display audio release and event callback removal

`display_audio_release.c` source-defines native 0x45f7be list traversal, transition unlink, callback removal, page clearing, field resets, object deletion, ordered node frees and finalization. It reuses selected same-address `audio_uart_lv_style_unlink_450500` rather than importing a duplicate transition body. `verify_display_audio_release.py` passed four actual compiled ARM C/native null/empty/one-list/two-list ordered-call and state cases. `display_audio_page_deinit.c` defines native 0x45fb7c and 0x45fbae, including the full 0xc3-byte effect; `verify_display_audio_page_deinit.py` passed four actual compiled C/native null/non-null memory cases using the selected freestanding `memset` source. The coherent selected `peripherals-display-audio-page-round` passed 2776 definitions, 741 unresolved, zero duplicate providers, SHA-256 `48ff843f2409885ef6230c12f3ef71cbc446451c71fc915487e3a12506a5cc67`.

The next native child 0x451862, `lv_obj_remove_event_cb`, is source-defined in `display_event_remove_callback.c`: it preserves the fixed initial event count, forward index even after a removal, callback-pointer equality and the authenticated null assertion/log followed by an invalid-address fault. `verify_display_event_remove_callback.py` passed seven actual compiled C/native matched-index and null-fault cases with event-list child effects cut symmetrically. The selected target snapshot including this child is pending. Event list count/at/remove 0x451790/0x4517d6/0x45181c, object delete 0x44d7b8, finalize 0x45bbd2, and product page/list state remain genuine connected obligations.
### Event-list and display stop round (2026-10-12)

The selected Main/Audio candidate now includes authenticated LV object-event count,
lookup and removal wrappers (0x451790/0x4517d6/0x45181c), callback removal
(0x451862), and the event-list count/lookup/remove bodies
(0x450158/0x450190/0x4501d2). The list removal sets the descriptor invalid bit
and requests deferred compaction, matching the native child order. Actual
compiled ARM C versus stock ARM checks pass nine wrapper, seven callback, and
six event-list cases. The coherent target link is
`peripherals-event-list-access-round`: 2783 definitions, 740 mixed unresolved
imports, zero duplicate strong providers, SHA-256
`318b9ecb6d2ea7836f5832d189810b9eef78cd8a50250f386796f2df1a0df76d`.
Its relocation census has 79 direct branch imports and 661 address-only
imports. These counts are interfaces, not missing-body or source coverage counts.

The next selected source adds the complete audio-stop selector at 0x45faa8 and
brightness open/close wrappers at 0x46f68a/0x46f6a2. Audio-stop's 40 actual
compiled ARM C versus stock cases cover null state, byte-truncated modes,
missing IDs, child lookup failures and successful child routing. Brightness
uses the already attributed live byte `audio_uart_font_flash_mode` at
RAM0x20074fb8. Its stage, prepare and commit children remain genuine typed
callable imports. The coherent target link `peripherals-display-stop-brightness-round`
has 2786 definitions, 745 mixed unresolved imports, zero duplicates, SHA-256
`d140a6e4253fee5154fac0c6f96cd87b6e83c261f8b326332f458446de338e70`.
Audio-stop exposes four genuine child bodies. The image remains source-incomplete;
live RAM initialization, target placement and hardware execution remain open.

The four direct audio-stop children are now source-defined: all-stop event
0x45f6da, two-list ID lookup 0x45f840, and ID-specific event posts
0x45f6c0/0x45f6ec. They use the previously selected native LV object-event
provider 0x451670, including the synchronous stack-local ID payload.
Twelve actual compiled ARM C versus stock ARM lookup/event cases pass.
`peripherals-display-stop-children-round` links 2790 definitions, 741 mixed
unresolved imports, zero duplicates, SHA-256
`e46192b1658b9be6d6d7ac02377dca4bf155569ad14c34d89c3fde06cc8520fe`.
The connected stop path is source-closed at its direct children, while the
larger display service, product object state and live layout remain open.

Brightness flash-power preparation 0x46f50c/0x46f52c is now source-defined
against the previously selected `audio_uart_font_flash_power` provider and
authenticated device/sleep cells. Six actual compiled ARM C versus stock ARM
cases cover prior sleep values 0, 1 and 2 for both directions. Existing
`display_font_flash_lock.c` already contained the full native mutex and
diagnostic bodies of 0x46f5a6/0x46f604 as private helpers; these now export
their authenticated identities and remain shared by the older flash-lock
callers. The fresh post-change coherent Main receipt
`peripherals-brightness-connected-round` links 2794 definitions, 737 mixed
unresolved imports, zero duplicates, SHA-256
`ea4a07892e4db30ce32a980773cb22bec7063a9ae44c89044f7938e8ff767035`.
The two new preparation branches have actual C/native comparison; the reused
mutex diagnostic branches have source/native static correspondence and still
need broader runtime/hardware qualification. Product mutex/device cell
initialization and final placement remain separate contracts.

### Display service and BLE receive transport round (2026-10-12)

The native display service entry 0x44227e and framebuffer-base getter
0x46ca6e are now source-defined. Two actual compiled ARM C versus stock ARM
checks cover the ordered EFS/logger calls and the authenticated 0x20080000
framebuffer literal. The connected EFS request 0x458c48 initializes its
one-byte stack payload to zero and passes ID0x400/length1; the actual
compiled/native call comparison passes. The logger BLE cancellation parent
0x458e48, flag getter0x458e32, setter0x458df0 and descriptor writer0x448cb8
are source-defined against authenticated RAM cells at0x20074fe2,
0x200746b0 and direct descriptor object0x20073b90. Six actual compiled/native
cases pass across inactive, no-log, extended-log and compressed-log branches.
The callback pointer is an authenticated Thumb reference to 0x5bf972 and
remains a genuine source/ROM contract. The post-change coherent Main receipt
`peripherals-display-service-connected-round` links 2801 definitions, 740
mixed unresolved imports and zero duplicates, SHA-256
`640727ad547f226151354252a88779a2f23c3bbf6de95721696d56a15d428fa9`.

`display_thread_msg_rx_ble.c` adds the complete native receive transport
0x48f12c: validation, heap allocation, payload zero/copy, queue counts,
submission, wake and failure cleanup. It reuses the existing typed RX manager
contract `audio_ble_rx_thread_state` at RAM0x20003ffc. Five actual compiled
ARM C versus stock ARM cases cover null input, missing queue, allocation
failure, success and queue failure. The zero-fill oracle normalizes stock
helper0x43c0e4's `(destination,length,value)` ABI against C `memset` while
comparing resulting bytes and all other call effects. The fresh corrected
Main receipt `peripherals-ble-rx-transport-corrected-round` links 2802
definitions, 739 mixed unresolved imports, zero duplicates, SHA-256
`265e2857a63793f216089a56e6f9ae1e068f54c21976fd80581977a79ba0153b`.
Its relocation census is 74 direct branch imports and 665 address-only
imports. These are interface counts, not missing-body counts. Heap product
cells, BLE RX queue/thread initialization, callback source and final
placement/hardware remain open.

The shared connection-state callback 0x46f32c is now one source-defined
provider for both display and BLE slave-sync call sites. It reads the
profile context at offset0x54 and invokes the already selected security-state
provider0x4b82e8 with a normalized Boolean. Four actual compiled ARM C versus
stock ARM cases pass for byte values 0, 1, 2 and 255. The context pointer
cell0x2007432c has an authenticated source producer in the selected
`audio_ble_app_slave_handler_init` (native0x46ed94); allocation and live
initialization of its pointed-to state remain separate. The coherent Main
receipt `peripherals-display-connected-round` links 2803 definitions, 737
mixed unresolved imports and zero duplicates, SHA-256
`cd2f27420ee8358f045e568528d24f57e519185d90628013efc308bacd8133cc`.
Current relocation census: 72 direct branch imports and 665 address-only
imports. No full source, layout or hardware completion is inferred.

### LV startup descendant round (2026-10-12)

`display_lv_init.c` reduces the full native lv_init parent0x473548 with its
ordered initialization, idempotent warning, authenticated three-byte version
check, endian assertion and final root flag. It reuses the selected LV root
RAM0x2006f548 and file context RAM0x20071ac8 symbols. Actual compiled ARM C
versus stock ARM passes the first-run and initialized branches with child calls
symmetrically cut. `display_lv_global_init.c` reduces native0x4734cc:
the 0x1ec-byte clear, two array headers, fixed constants and fixed-root
assignment. Its actual compiled/native 0x200-byte state comparison passes.
The coherent receipt `peripherals-lv-global-init-round` links 2805 definitions,
753 mixed unresolved imports and zero duplicates, SHA-256
`e8e7cda9ffc1a78e12a828d73bd30f1b776696027b08c474363565cd3d5680d8`.

`display_lv_init_children.c` adds eight genuine native LV startup children:
memory0x48aa60, async0x49acb0, display0x464330, indev0x4c6d8c,
style0x44d32c, animation0x48438c, cache0x44b90c and font0x488f4c.
The array-header primitive0x482b00 is source-defined once and shared with
the global initializer. Eight actual compiled ARM C versus stock ARM cases
pass for child call sequence, arguments and changed root bytes. The coherent
receipt `peripherals-lv-init-children-round` links 2814 definitions, 751
mixed unresolved imports, zero duplicates, SHA-256
`f3bc77149d3b6a5cfaf2bfb3e158888c73ea0a40d74a474573989fe18ee5a75e`.
Current relocation census: 86 direct-branch imports and 665 address-only
imports. The direct count rose because full native parent/children exposed
genuine allocator, timer, filesystem and callback-table descendants. The
selected C graph remains incomplete; LV root placement and startup RAM
ownership still require product evidence.
