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
