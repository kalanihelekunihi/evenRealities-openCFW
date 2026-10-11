# Apollo Bootloader and Main C completion pass

## Bootloader filesystem ABI split

The selected filesystem source used one `opencfw_boot_fs_error` variadic import for two distinct locked-image targets. The NOR-backed littlefs read, program and erase failure paths call the plain formatter at `0x415fae`; boot mount diagnostics call EasyLogger at `0x4176ce`. The latter needs level, tag, file, function, line and format metadata that the current `boot_mount.c` callsites do not reconstruct.

`filesystem.c` now calls `opencfw_boot_fs_printf` on its three NOR errors. The new `source_candidate_20261010/fs_printf_alias.c` is a naked Thumb tail branch to the already selected, source-owned `opencfw_provider_415fae`. Its object has one `R_ARM_THM_JUMP24` relocation to that provider, with no retained stock executable target literal. The ABI preserves argument registers and caller stack. The mount calls still use `opencfw_boot_fs_error` and remain unresolved until metadata and variadic arguments can be proved; no generic one-step alias is admitted.

The source-only M55 builder selected **312 objects** (one more than the previous 311), **861 global/weak providers**, zero compiler failures, 19 excluded duplicate variants and two excluded fixture tests. `arm-none-eabi-ld -r --whole-archive` passed with its prior GNU-stack warning. The exact ten unresolved names remain `__aeabi_d2f`, `opencfw_bl_generic_log`, `opencfw_bl_post_configure`, `opencfw_boot_fs_error`, `opencfw_boot_rom48`, `opencfw_boot_rom_delay_cycles`, `opencfw_boot_rom_mram_program`, `opencfw_boot_startup_power_initialize`, `printf`, and `resume_scheduler`. The existing littlefs host test and boot-mount host test both pass after their two logging stubs were separated. This pass has no fresh original-byte execution oracle; the target distinction follows the previous round-95 callsite audit and the new relocation proves only source composition.

**Bootloader component complete: no.** Beyond the ten named imports, startup-root data/callback placement and a whole-path variant oracle, EasyLogger/formatter behavior, ROM and scheduler contracts, final link/layout and hardware execution remain open. A bounded remaining estimate is ten import decisions plus startup/layout/whole-image qualification phases; elapsed time is not grounded by the current evidence.

## Main source boundary

The selected Main archive remains **56 objects**, relocatable PASS and **nine** imports: `audio_log_simple` (provided by Audio source with lower-state caveats), `g2_fal_flash_device_count`, `g2_fal_flash_device_table`, `g2_fal_partition_rows`, `g2_flashdb_candidate_log`, `g2_flashdb_db_rows`, `g2_flashdb_print_buffer`, `g2_flashdb_print_sink`, and `g2_flashdb_vformat`. Its direct SMP body coverage remains **10/11**. Main and Audio are subgraphs of the Apollo Main image, but the Audio source provider cannot close its own output/lock/formatter state merely by linking the two archives. The FAL/NOR product tables and FlashDB rows have stock validation bytes but no attributable product source initializer; zero-filled substitutes would alter behavior. The print formatter has an isolated ABI-compatible Audio alias and 88 selected formatter cases, but no complete composed grammar/capacity proof or source-owned buffer/sink installation. The direct extended logger lacks a complete fatal and FP64/general-varargs path.

**Main component complete: no.** The exact remaining source areas are G2 FAL/NOR product configuration, FlashDB 256-row initializer, diagnostic formatter plus output state, direct extended logger, Audio output/lock state, and absolute reset/link layout; physical flash and output need hardware validation. The current source corpus supports no safe inferred product bytes or whole-image completion percentage.

## Isolated outer-body C reductions

The second pass adds two complete *syntactic outer control-flow* reductions in C and keeps both outside the selected archives. `build_outer_candidates.py` compiles them independently with freestanding Cortex-M55 flags and `-Wall -Wextra -Werror`. Both compile with zero diagnostics; the ignored build receipt is `g2/build/c-source-completion-20261011/apollo/receipt.json`.

* Bootloader `startup_power_root_candidate.c` covers frozen decompile `0x41c4b4..0x41c7de` (**810 stock bytes**) as a C root with the observed query/INFO-read branch, revision/variant field extraction, mode and MMIO updates, critical section and packed return. The product pointer-cell map is a required external data contract, not copied stock data. Its object defines `opencfw_boot_startup_power_initialize` and exposes **19** imports: one product state object and 18 child/runtime names. **Caller ABI mismatch:** selected `startup_alternatives.c` declares `extern void opencfw_boot_startup_power_initialize(void)`, while this isolated candidate exposes `uint64_t (uint32_t,uint32_t,uint32_t,uint32_t)` following Ghidra's uncertain signature. Raw R0–R3 input use and R0/R1 output observation must be resolved at the actual callsite before composition. The original decompile's condition where both INFO reads are skipped leaves a low return register inference; this candidate takes `prepare_io`'s return as that register value. That and the many `DAT` field mappings require original-byte/state oracle review before selection. The selected Bootloader archive still has **312** objects, **861** providers and **10** unresolved names from the preceding section.
* Main `extended_log_root_candidate_20261011/extended_log.c` covers frozen decompile `0x43d574..0x43d976` (**1,026 stock bytes**) as an outer C logger. It carries exception rejection, fatal callback/idle flow, level/module filtering, prefix assembly, source fields, variadic format, token filter, suffix/output and guard release. It defines `g2_flashdb_candidate_log` with **21** imports: product configuration/state, fatal continuation, formatting/output/guard helpers and compiler memset. These are typed contracts; none is a fabricated initializer, inert fatal path or output stub. In particular arbitrary format grammar, FP64 conversions, runtime format pointers, output state and the installed fatal callback remain unowned. The Main selected archive remains **56** objects and **nine** unresolved names.

Both root bodies are therefore **C-compilable candidates**, not original-byte or ABI-approved providers. Their combined nominal decompile extent is **1,836 bytes**, but compiler success is not evidence that all those original bytes or branches execute equivalently. No bootloader or Main whole-image completion flag is set.

### Still absent or external in these two root graphs

The Bootloader root's 19 imports are exact in the compile receipt. Some child semantics already exist under differently named selected providers, but the candidate does not alias them without argument/return and state-effect proof. Product pointer-cell initialization, privileged IRQ restoration, ROM behavior and full root reset sequence remain external. The older selected Bootloader archive separately retains generic floating log, post-configure, boot-mount EasyLogger, three ROM, compiler conversion, `printf` and scheduler-resume seams.

The Main root's 21 imports are exact in the compile receipt. Several correspond to selected bounded helpers, but general formatter behavior, fatal continuation and product logger data are not selected providers. Main's FAL table/count/rows, 256 FlashDB rows, print buffer/sink/formatter and Audio logger state also remain absent or external. Thus the two previously whole-outer undefined names now have compiled C candidates, while their child/import graphs and production admission are unfinished. This is a bounded census for these two roots, not a claim that every pseudocode body in either official image has been reconstructed.

## Experimental Main logger composition with selected source

`selected_helper_adapters.c` bridges the root candidate to **12** selected Main helper contracts: bounded append, module length, token search for input and output, category-mask checks, optional source-field checks, fixed five-byte line rendering, stack fill, lock-state guard enter/exit, module policy and output wrapper. It passes the selected guard and output implementations real typed lower callbacks (`g2_log_lock_enter/exit` and `g2_log_transport_submit/signal`) instead of inert fixtures. The category mask reads the product-supplied logger state at byte 216 plus four bytes per level. This is experimental composition; the selected helper bodies still contain some stock RAM address assumptions and have their own bounded test domains.

The isolated builder links the current **56-object selected Main relocatable object**, the logger root object and the adapter object with `arm-none-eabi-ld -r`: **PASS**, zero duplicate definitions. The composed object has **21** unresolved names: existing Main/Audio/product imports `audio_log_simple`, three FAL product symbols, `g2_flashdb_db_rows`, and three diagnostic-print lowers; logger product imports `g2_extended_log_fatal_callback` and `g2_extended_log_product`; runtime/hardware `g2_log_exception_number`, `g2_log_is_privileged`, `g2_log_fatal_idle`, two lock callbacks, three time/process/thread strings, two output callbacks, and `g2_log_vformat`. This replaces the selected Main whole-body `g2_flashdb_candidate_log` gap with explicit lower contracts. Of the logger root's original 21 standalone imports, **12** now bind to composed source or locally compiled selected-helper adapters; the remaining nine are product/runtime/formatter seams. The total 21 includes previously independent Main imports and the four newly explicit lock/output transport callbacks.

Audio source owns `audio_log_simple` in the Apollo Main image graph; its lower state/output closure is a separate cross-archive task. The composition uses the Main archive only and neither assumes Bootloader/Audio are one image nor claims runtime/byte equality. Fatal callback installation, arbitrary variadic formatting including FP64, runtime format strings, product data placement and hardware output remain the exact admission blockers.

## Bootloader startup-root ABI composition

The original root's Ghidra four-word signature was a poor production ABI: its caller at `0x41fa50` declares/invokes no arguments and ignores return, while the root consumes ambient **R5/R7** and mutates saved R1–R3. The selected source `platform_control/runtime_query.c` clears its output byte before descriptor lookup and then writes 0/1, so incoming R1 low byte does not drive the power-query result. Incoming R1 high 24 bits still survive in returned R1. The retained `root-r1-negative-control.failure.json` rejects clearing all R1 bits (stock R1 `0x10203000` versus zero), and `root-r5-negative-control.failure.json` shows ambient R5 changes clock MMIO (required temporary value `0x2002706a` versus mutant `0xa5b6c7da` in the controlled fixture). A plain C `void(void)` function that invents register values would be wrong.

The component now selects the existing source ABI solution: `startup_power_root_integrated.c` is copied from the previously reviewed `reconstructed_initialize_clock_coupled_abi.c`, with **only** 11 preprocessor bindings from historical accepted startup linker names to currently selected semantic providers and removal of one unused declaration. `startup_root_entry.S` is byte-identical source text to the prior validated adapter; it captures R5/R7 plus saved R1–R3 and restores mutated R1–R3. `startup_power_void_adapter.c` exposes the selected caller's `void(void)` symbol as a single Thumb branch to that ABI entry; the branch has one `R_ARM_THM_JUMP24` relocation and preserves raw registers. The speculative four-argument `startup_power_root_candidate.c` stays explicitly builder-excluded.

The prior independent `root-abi-native4-comparison.json` reports **1,376 PASS** original/source fixtures, visits **810/810** root bytes and **922/922** clock bytes, compares R0–R11, SP, PRIMASK, ordered writes and RAM, and exercises original/source query, critical-save, trim and dispatcher subgraphs. It explicitly controls seven root and ten clock children, plus INFO and some callback effects, so it is not whole-product proof. This prior receipt applies to the copied core algorithm and unchanged ABI adapter; the new selected archive's named child bindings were **not** rerun through that original-byte oracle in this pass.

Fresh source-only Bootloader builder: **315 selected objects**, **864 providers**, 19 excluded duplicate alternatives, two fixture exclusions, one isolated speculative root exclusion, zero compile failures and **nine unresolved** names. Whole-archive `arm-none-eabi-ld -r` passes with the prior GNU-stack warning and no duplicate strong definition. The nine names are `__aeabi_d2f`, `opencfw_bl_generic_log`, `opencfw_bl_post_configure`, `opencfw_boot_fs_error`, three resident ROM entries, `printf` and `resume_scheduler`. This retires the root *symbol* from the selected archive but does not establish startup product data/layout, real ROM/scheduler behavior, all-variant execution, image equality or hardware qualification. **Bootloader complete: no.**

## Fresh selected-root execution and numerical runtime

The retained root harness was adapted to the **current selected archive** and now resolves the actual selected child symbols. A temporary test ELF links all archive members with external test addresses. Unicorn cannot execute the selected Cortex-M55 MVE instructions in `startup_clockmux.c` and `runtime_query.c`, so those **two** unchanged source files were recompiled for Cortex-M33 in the test ELF; the M55 selected archive remains independently compiled and relocatably linked. The test entry is the new `void(void)` adapter. `verify_current_root.py` passes **1,376/1,376** stock/source cases, visiting **810/810** original root bytes. The selected query at `0x41c2d8` and critical-save at `0x41b8ec` execute actual stock/source bodies; nine other root children and ten clock lower calls use identical controlled callbacks on both sides. R0–R11, SP, PRIMASK, ordered MMIO writes and local RAM agree. The ignored receipt is `g2/build/c-source-completion-20261011/apollo/current-root-m33-native-query-critical.json`. This fresh result proves bounded root composition under the stated cuts; it does not establish native M55 runtime, ROM timing, product layout or hardware behavior.

The missing compiler conversion `__aeabi_d2f` is now source-owned by pinned LLVM compiler-rt **llvmorg-20.1.8** `truncdfsf2.c`, `fp_trunc_impl.inc` and `fp_trunc.h`, with exact URLs and SHA-256 hashes in `compiler_rt_20_1_8/provenance.json`. The ARM object defines `__truncdfsf2` and EABI alias `__aeabi_d2f`, with no executable blob. `verify_d2f.py` compares the pinned source against a host hardware double-to-float cast for **100,127/100,127** exact output-bit cases: signed zeros, infinities, quiet/signaling NaNs, subnormal/normal/overflow thresholds and seeded random encodings. The ignored receipt is `g2/build/c-source-completion-20261011/apollo/d2f-receipt.json`. This is host round-to-nearest numerical evidence; it does not prove all rounding modes, target FP exception flags, original IAR code identity or stock byte equality.

Two more named imports gained source-backed branches. `post_configure_alias.c` forwards the post-bringup `(object,operation,enable)` ABI to selected `opencfw_boot_control_power_apply`, whose guard and accepted UART configuration path are already selected; the historical startup linker binds both to stock `0x422ba8`. `scheduler_resume_entry.c` forwards the idle-loop void call to selected `opencfw_bl_scheduler_resume`, whose return that caller ignores; the historical startup linker repeatedly binds that name. These are target-name/ABI compositions, not new whole-entry execution or device proofs.

The current deterministic Bootloader builder selects **318** members and **868** global/weak providers with zero compile failures, 19 duplicate alternatives excluded, two fixtures excluded and two isolated leads excluded. Whole-archive relocatable linking passes. It has **six exact unresolved imports**, down from nine before this pass:

| Import | Concrete remaining contract |
|---|---|
| `opencfw_bl_generic_log` | Seven direct platform-bringup calls target stock formatter `0x415fae`; two use binary64 `%f`. `generic_log_float_candidate.c` compiles as an isolated register-preserving branch to selected formatter source, but a composed FP64/FPSCR/output and product-format-pointer oracle is needed for selected admission. |
| `opencfw_boot_fs_error` | Boot-mount callsites use EasyLogger `0x4176ce`, yet current source passes only a format pointer and arguments. Reconstruct level/tag/file/function/line and vararg placement for those exact callsites before forwarding. The littlefs NOR callbacks are already split to the plain formatter. |
| `opencfw_boot_rom48` | Resident INFO ROM read via source thunk; target ROM implementation or a declared platform import and hardware qualification remain external. |
| `opencfw_boot_rom_delay_cycles` | Resident delay primitive from authored timing wrapper; target ROM/timing behavior remains external. |
| `opencfw_boot_rom_mram_program` | Resident MRAM program primitive from source bridge; ROM ABI and real flash programming remain external. |
| `printf` | Pinned upstream TLSF diagnostic/default-walker paths call C `printf`. Historical links use a synthetic fixture address, with no authenticated bootloader `printf` implementation binding. Requires a sourced freestanding libc implementation or explicit runtime import; aliasing it to a formatter solely to remove the name would not establish its `%p/%s/%x/%u` contract. |

**Bootloader completion flag: false.** The source archive compiles, but two logger contracts and TLSF `printf` still lack admitted source providers, three ROM interfaces remain external, and initialized product data/layout, all-variant execution, whole-image link/equality and physical qualification are unresolved. The bounded remaining count is six named import decisions plus those independent integration/validation phases. A calendar estimate is not grounded by this evidence.
### TLSF diagnostic `printf` C candidate

`source_candidate_20261010/tlsf_printf_candidate.c` is a complete C varargs
candidate for the TLSF scalar diagnostic callsites. It uses the selected
0x415fae wrapper's buffer (`0x20024cd0`), callback slot (`0x200270cc`), and
source-owned `opencfw_boot_plain_vsprintf` parser. It compiled with Clang for
ARM Cortex-M55 (`-Wall -Wextra -Werror`). The builder excludes it because the
TLSF `printf` import's original call target and output-domain equivalence have
not been authenticated; the current selected archive remains 318 members,
868 providers, six imports. This is C source coverage, not production or
original-byte admission.
### Boot-mount EasyLogger argument recovery

The pinned `f89a4c46` stock image (`g2-2.2.6.10`) at base `0x410000` and
decompilations `004210c8.c`, `004211b0.c`, and `00421210.c` identify the ten
boot-mount log callsites. Their fixed ABI is `(level, tag, file, function,
line, format, ...)`, with levels 2/4, tag `file_system`, one source-file
string, three function names, and exact source lines 0x51/0x53/0x55/0x5a/
0x5c/0x6b/0x6f/0x7f/0x86/0x9a. The literal pool 0x421374..0x4213c4 and
pointed-to strings supply the metadata and formats; no new product values
were inferred. `filesystem/boot_mount_log.h` provides a typed C metadata
adapter to selected `opencfw_boot_elog_output`, and `boot_mount.c` now supplies
the original metadata at each callsite. Host boot-mount test passes (ten log
events). Current selected archive builds: 318 members, 868 providers, **five**
imports (`opencfw_bl_generic_log`, three ROM contracts, and TLSF `printf`).
This is C source/build closure for the EasyLogger ABI, not a fresh original-
byte comparison of the modified boot-mount callers.
### Resident ROM boundary

`platform_control/resident_rom_contracts.h` records the three remaining
resident Thumb entries: info read `0x00000049`, cycle delay `0x00000041`, and
MRAM program `0x0200ff21`. The MRAM bridge has a recovered five-argument C
call shape; the delay wrapper passes a cycle count in R0 and ignores the
return. The info-read thunk forwards ambient registers, so no C prototype is
asserted for that entry. These addresses occur in existing checked linker
maps and the MRAM API table; actual ROM implementation bytes are absent from
the OTA image. They remain unresolved imports by design.
### Whole Bootloader body crosswalk audit

`audit_boot_body_crosswalk.py` writes a finite, per-function
`boot-body-crosswalk.json` against the pinned `f89a4c46` catalogue and the
current selected archive inventory. The catalogue recognizes **903** function
envelopes; **849** have a raw pseudocode file and **54** do not. Among all
903, **73** have an exact-address authored provider name in the selected
archive; **260** have a selected source header mentioning the address;
**30** have a selected source function-name lead; **540** have no mechanical
address/name crosswalk. The JSON enumerates all 903, including the 54 raw-
pseudocode absences and 540 attribution gaps. Header/name leads are not
semantic proof; absence of a machine crosswalk is not proof that a source
body is missing. For example the no-crosswalk qsort body `0x423a48` is
implemented in selected `init_table/qsort.c` and independently tested, while
the raw-absent thread creator `0x417c7c` is represented in selected
`thread_creation/kernel_static.c`. This audit therefore establishes a
**finite unresolved attribution set of 540**, not a truthful claim that
540 implementations must be written. It also exposes the 54 missing raw
pseudocode artifacts as a separate input gap. The catalogue itself is not a
validated whole-image code/data partition, and no production image layout
has been established.
### Receipt-backed crosswalk refinement

The crosswalk now consumes selected-path, same-image
`function-provenance.json` and `mapped-functions.json` receipts. It adds
**20** address leads that were absent from the initial lexical audit.
`manual_body_bindings.json` adds two inspected selected-source leads:
introsort core `0x423a48` to `opencfw_boot_init_sort`, and PCM state
transition `0x42b294` to `native_spot_state_transition`. Both are leads,
not new semantic admission. The remaining no-machine-crosswalk count is
**518** of 903 catalogue envelopes. No sampled high-byte candidate was
proven to lack C: `0x423a48`, `0x42b294`, and raw-absent `0x417c7c` all have
existing source routes. The finite list of 518 is in the JSON and is the
current manual attribution queue. An exact count of truly unwritten bodies
cannot be inferred until each is resolved against selected upstream static
functions, renamed providers, or missing source. A safe current bound for
catalogued bodies is 0..518 unresolved attribution, rather than treating the
archive's five imports as a body coverage result.

Whole-image obligations remain outside that function count: a reviewed
code/data partition, stock vector and initialized-data placement, product
string and configuration address layout, a final linker script and relocation
policy, and external resident ROM entry contracts. The compiled archive is
still a relocatable component candidate; no complete boot image has been
linked or compared with the stock payload.
### Normalized attribution and newly implemented division body

The crosswalk now recognizes selected C comment address leads and normalized
`name_42xxxx_native` spellings, reducing the unattributed queue from 518 to
474. These are labelled leads because comments can describe callees rather
than the containing body. The largest 20 no-crosswalk entries were inspected
against selected sources: early `0x411xxx..0x414xxx` littlefs bodies have
selected upstream C but lack per-address bindings; `0x41ce52` has selected
startup SPOT dispatch; `0x42b6b8` has `native_spot_state_decode`;
`0x42b06c` has `native_spot_power_transition_trims`; `0x42c6f8` has selected
IOM event service; `0x42308e` has selected post-validation. These require
further individual equivalence receipts before exact attribution.

The review found a genuine source gap: general unsigned 64/64 quotient
helper `0x42287c`. Prior UART evidence explicitly covered only a specialized
64/32 call. `source_candidate_20261010/u64_division_42287c.c` now supplies a
complete C body with the recovered four-word ARM argument and two-word return
ABI, including stock pseudocode's divisor-zero return. It uses bitwise long
division and introduces no compiler division import. Cortex-M55 archive build
passes at **320 selected members, 870 providers, five imports**. Host
arithmetic check passes **100,121** edge/random cases; this is not a stock
instruction oracle or image admission. `0x42a550`, a separate SPOT state
decoder from `0x42b6b8`, also now has a C body with its distinct product
configuration word and auxiliary-bit condition; it is compile-only pending
an original-byte oracle. The current per-function crosswalk has **75** exact
provider names, **261** header leads, **20** receipt leads, **30** function
name leads, **7** normalized-name leads, **34** comment leads, **2** reviewed
manual leads, and **474** without a machine crosswalk. After four additional
manually inspected source bindings (with the IOM mapping already counted by
its source header), the regenerated JSON has **6** manual leads and **470**
without a machine crosswalk. Bootloader completion
remains false; further work is finite but not reducible to the import count.
### Fresh stock/source instruction oracles for new bodies

`verify_new_boot_bodies.py` executes locked `f89a4c46` stock instructions
and Cortex-M33 recompilations of the unchanged new C sources under Unicorn.
The receipt `new-body-oracle-receipt.json` passes **421** unsigned 64/64
division cases (including zero denominator, high-word divisors, and seeded
random values), comparing both return words and visiting **514/562** stock
body bytes. The distinct `0x42a550` decoder passes **360** combinations of
snapshot words, state, auxiliary byte, mode, configuration, and hardware
state, comparing status and both output words and visiting **610/782** stock
body bytes. Inputs and MMIO are simulated; the two uncovered branch slices
and selected Cortex-M55 code generation are outside these receipts. This
qualifies bounded semantics, not production image equality.

The crosswalk's glued source-header form (`locked428068`, etc.) now detects
eight further selected source leads. Its latest no-machine-crosswalk queue
is **464** before two reviewed manual bindings and **462** in the latest
generated JSON. The next largest entries were sampled: DFU payload program
`0x42dae8` is represented by selected `opencfw_boot_program` in
`update_core/update_core.c`; `0x415bf6` is the selected Ambiq plain formatter
parser; `0x427e84` is within the PCM transition family and needs a specific
function receipt. Early 0x411xxx..0x414xxx large bodies are littlefs code
but lack a complete per-function source binding. No additional high-
confidence unwritten body was established from this sample.
### Thirty largest remaining attribution reviews

`largest30-review.json` records the next thirty largest no-crosswalk
functions at the start of this round. **Six** have inspected selected-source
bindings: SPOT transition selector `0x42a2b4`, ADC enumeration `0x42ee70`,
IOM event apply `0x42c0b2`, startup information cache `0x41c320`, DFU CRC
check `0x42d890`, and TON trim apply `0x42f4b2`. The ADC binding has an
existing 388/388 original-byte scoped receipt; the others retain the stated
source/equivalence limits. **Eighteen** lie in the locked littlefs cluster
with selected pinned `filesystem/upstream/lfs.c` but no trustworthy per-static-
function mapping. Two are PCM transition family, three clock/runtime family,
and one parser-adjacent body remains unattributed. Those 24 are finite review
items, not newly asserted missing implementations. The generated crosswalk
now has **456** no-machine-attribution entries out of 903.

The pinned nine-byte TON configuration table at `0x433f20` already has a
source-owned definition `opencfw_ton_trim_rows` in selected
`startup_ton_hooks.c`; its consumer still uses the stock address. A final
linker/data-placement contract or a separately tested symbolic-reference
change is needed before that table is self-contained in a new image. No
stock address was silently assigned in this round. Component completion is
still false; the next measurable work is the 456 per-function attributions,
then a code/data partition and data-placement/link receipt. A calendar ETA
would depend on how many of those resolve to existing upstream/static C.

### LittleFS static functions and next non-LittleFS bodies

`littlefs_static_bindings.json` records eighteen individual bindings from
locked function entries to selected pinned `lfs.c` algorithms. Fourteen
static functions have local text symbols in the selected object. Four
(`lfs_dir_splittingcompact`, `lfs_mkdir_`, `lfs_ctz_extend`, `lfs_mount_`)
have definitions in the selected source but were inlined or optimized away
as separate symbols. These are source attribution leads, not whole-body
equivalence receipts. Two further selected static bindings are recorded in
`selected_static_bindings.json`: stock `0x4210c8` to the emitted
`ensure_directories`, with its five recovered EasyLogger lines, and stock
`0x42740c` to `pll_configure`, whose register masks and config guards match
but whose local symbol was optimized away. The regenerated crosswalk has
**436** no-machine-attribution entries out of 903 catalogue functions; this
count does not equal 436 missing C bodies.

Stock `0x426536` (`am_hal_mspi_interrupt_service`, 234 catalogue body bytes)
is a genuine gap in the selected C archive. The pinned Ambiq HAL 5.1.0
source has a strong family attribution, but the target uses private command
queue, DMA, and clock lowers. A full C control-flow candidate now exists at
`source_candidate_20261010/mspi_interrupt_service_candidate.c`. It compiles
for Cortex-M55 with `-Wall -Wextra -Werror` and retains six typed external
lowers: command queue status, queue disable, queue error resume, queue enable,
DMA programming, and clock release. The source builder explicitly excludes
it pending lower binding and a bounded original/source oracle. The stock
state prefix, callback layout, HP/CQ branches, and MMIO paths are represented;
this compile result is not an equality claim. Bootloader component completion
remains false. Its selected archive count is unchanged by this isolated file;
the next concrete work is binding the MSPI lowers and testing bounded branch
fixtures, followed by the remaining 436 attributions and data placement.

The first fresh stock/source MSPI oracle found and fixed two concrete errors
in that isolated candidate: the valid handle prefix includes the initialized
bit (`0x01bebebe`), and transaction status accumulation occurs only inside
active HP/CQ branches. `verify_mspi_service_candidate.py` now passes nine
Cortex-M33 original/source cases with **534 distinct stock instruction bytes**
visited within the 712-byte function range. The cases cover invalid handles,
idle CQ, HP pending/completion, HP clock release, CQ status lookup, and CQ
error handling. Real child calls are cut to declared success and the status
output is explicitly populated; callback-present, active CQ sequence and
real hardware progress remain outside the receipt. The selected Cortex-M55
archive is still a separate build qualification.

The next bounded reduction binds the MSPI service's six lower imports to
source bodies. Selected `nor_mspi_queue.c` now defines the locked `0x427a56`
CMDQ status extraction and `0x427b38` error-resume traversal with 16-byte
status layout and target register masks. It also exposes a typed CQ-enable
result for the caller's consumed residual R0; the earlier void helper remains
available. Selected `mspi_pause_dma.c` exports its existing `0x42403e` DMA
programming body under the service's typed name. CQ disable and clock release
were already selected. The Bootloader archive build passes with **320 selected
objects, 874 providers, five unresolved imports**; the MSPI service itself
remains an isolated candidate, so this provider count is not image closure.
The extended service oracle passes **10** controlled stock/source cases with
**598/712** stock instruction bytes visited, including one active CQ callback
and explicit child output. This still excludes nonzero lower statuses, callback
side effects/restart, descriptor callback, changing MMIO during busy-wait,
and physical hardware operation. These are concrete remaining oracle contracts,
not fabricated implementations.

The MSPI service oracle has since expanded to **14** stock/source cases and
**610/712** visited stock instruction bytes. It compares HP descriptor
callback invocation, a command queue callback, and nonzero results from
CMDQ status, CQ disable and clock release, with controlled child cuts. It
does not prove child implementations or callback side effects. The next
unattributed review established that stock `0x424af0` MSPI configure already
has selected `nor_mspi_init/hal_leaves.c::opencfw_hal_mspi_configure`; its
handle guard, module registers and state offsets match. This is recorded as
one additional manual source lead, not a new body or whole-image proof.

Two further reviewed continuations are now bound: `0x41c86c` to selected
startup power configure, and Ghidra's ambient-register split at `0x42033e`
to the selected `0x420254` NOR MSPI initializer body. The regenerated
crosswalk has **431** no-machine-attribution entries of 903 recognized
functions (849 with raw pseudocode). This number changed partly because
other selected-source comments acquired address matches during concurrent
work; it remains an attribution queue. None of these bindings supplies
initialized data placement or a whole-image code/data partition.

### Source-owned TON consumer and fresh body/data audit

The selected TON apply routine previously consumed stock address `0x433f20`
even though selected source declared the nine-byte `opencfw_ton_trim_rows`
table. Its consumer now indexes that C table. The locked image slice and the
fresh selected Cortex-M55 object's symbol data both equal
`010102010102010202` (`ton-symbolic-data-receipt.json`). A fresh archive
build passes at **320 selected objects, 874 providers, five unresolved
imports**. The compiler may inline the bytes into the consumer; this is
semantic source ownership, not final address/layout qualification.

Stock `0x42da1e` chunked source compare is now manually bound to selected
`update_core.c::opencfw_boot_compare`: the 4 KiB storage-read/memcmp loop and
EasyLogger success/error lines match. The crosswalk has **430** remaining
no-machine-attribution entries. The canonical catalogue has 903 recognized
functions, 849 with raw pseudocode, and its range claims do not establish a
whole-image code/data partition. This pass found a real data-consumer gap
and fixed it; the inspected compare body was already source-owned.

The DFU update core had the same absolute-data issue for its diagnostics:
selected `update_core.c` still passed fixed stock flash addresses for 15
source-owned log strings and the OTA path. It now passes the C string symbols,
and `log_literals.c` owns the path string. The fresh selected archive builds
at **320 objects, 875 providers, five unresolved imports**. The authenticated
`update-symbolic-data-receipt.json` compares all **16** strings/path objects,
**452 bytes** including terminators, against their stock addresses with exact
matches. This closes source semantic ownership for these literals; final
placement and firmware image equality remain separate obligations.

### Selected reset, exceptions, scatter records and vector words

The Bootloader builder previously omitted six existing startup/exception
assembly sources (`reset.S`, `fpu.S`, `itcm_helpers.S`, `init_records.S`,
`record_adapters.S`, `exception_entry.S`). It now selects all six. The source
ABI graph gained the actual reset/stack/FPU, ITCM helper, scatter-record and
SVC/PendSV providers without new unresolved imports. New
`startup/vector_handlers.S` supplies the three genuine stock infinite-loop
handlers and a source SysTick entry that saves/restores BASEPRI and calls the
selected tick increment. New `startup/vectors.S` owns the first sixteen
vector words, including initial MSP `0x2007fb00` and symbol relocations for
all nonzero handlers. The fresh archive builds at **328 selected objects,
895 providers and five unresolved imports**.

`vector-table-receipt.json` compares a fixed-address link fixture against
the pinned first 64 image bytes: **64/64 exact**. The fixture assigns source
handler symbols their locked addresses; it does not prove a final source
link at those addresses. The selected vector object has 11 symbol relocations,
so executable handler addresses are not embedded as stock pointer constants.
`verify_vector_tick.py` passes six bounded stock/source SysTick cases across
three initial BASEPRI values and both tick results, visiting **26** entry
bytes. Unicorn rejects the M-profile mask instructions, so both stock mask
helpers and the equivalent source MRS/MSR operations are controlled cuts;
this is an outer-entry comparison, not a full exception/hardware proof.
The regenerated crosswalk has **421** unattributed entries of 903. Final
vector placement, external IRQ span, reset image layout, scatter payload
identity, and full code/data partition remain unresolved.

The remaining non-fixture assembly audit found three more authored units that
the builder had omitted: NOR storage callback veneers, source-owned startup
callback/context tables, and the clockmux ABI adapter. They now select; the
two omitted `opencfw_test_*` assembly units remain fixtures. The selected
archive builds at **331 objects, 901 providers and five unresolved imports**.
The context configuration table's **64 bytes** match pinned stock address
`0x433d58`; a fixed-address fixture for the four callback pointers and
priorities matches **32/32 bytes** at `0x433440`
(`callback-context-data-receipt.json`). These are source-owned data records,
but fixed-address pointer identity is still a fixture rather than final
linker placement. The crosswalk remains **421** attribution entries.

The scatter record table is now selected but still refers to compressed
payload offsets `0x434461`, `0x4341c0` and `0x434431`. Its C decompressor
and record structure are source-owned; those compressed payloads have not
been reconstructed from semantic source initializers. Copying their opaque
bytes would not meet the source-completeness requirement. This is a concrete
initialized-data blocker alongside final linker/vector placement and the
unreviewed code/data partition.

### Source-owned scatter initializer reduction

The authenticated 22-, 625-, and 48-byte stock streams decode to 24 bytes at
`0x40`, 1,371 bytes at `0x20000000`, and 4,096 bytes at `0x20080000`.
`scatter-semantic-data-receipt.json` records each input/output SHA-256 and
length. The last output is exactly 4,096 zero bytes. The first output is
exactly the 24-byte `.text.itcm_helpers` section assembled from source
(SHA-256 `06761544...`). The middle output is the existing structured C
`recovered_data` object (SHA-256 `e3bea7cc...` after normalizing native
callback relocations in the prior bounded receipt).

The selected scatter adapter now calls `opencfw_boot_expand_locked_data_record`.
That function installs the ITCM helper source bytes, the C-initialized SRAM
object, and the zero SSRAM region when the three authenticated output
records are encountered. Their source record offsets are zero because no
encoded payload is consulted. For any other descriptor, the adapter preserves
the generic decoder path. This changes 331 selected objects to 903 providers
and five unresolved imports; the source-only archive builds successfully.
This is a compiled source reduction, not a fresh execution oracle for the
modified adapter or a final linked image.

The middle object has source-owned VDDC/VddF rank arrays at offsets `0x0a4`
and `0x0f4`, five initialized state fields at `0x144..0x157`, and 27 SPOT
callback relocation slots at `0x158..0x1c3`. The 216-byte profile table at
`0x244` has an earlier consumer-backed extraction. The rest of the object
contains numeric address-valued metadata, including 12 words at
`0x31c..0x348` pointing into the stock data region and context pointers
around `0x39c..0x4b8`. Their typed field ownership and relocation targets
still require final source linker composition. The two task deinit callback
slots at `0x4d0` and `0x4f8` already use C symbol relocations. Numeric task
entry pointers at `0x4cc` and `0x4f4`, plus later original-address callback
values at `0x518..0x544`, remain contracts rather than source relocations.

The source linker must prove a loadable ROM image for `.text.itcm_helpers`
before the adapter copies 24 bytes to `0x40`, and must resolve the remaining
numeric data pointers and placement of all source-owned tables. The 421
crosswalk reviews are attribution work, not 421 established missing bodies.

A fresh direct-callback native oracle now covers the modified source adapter
(`verify_scatter_semantic_runtime.py`, receipt
`scatter-semantic-runtime-receipt.json`). It executes the three stock record
callbacks and source callbacks in separate Unicorn machines. All return
pointers agree. ITCM 24 bytes and SSRAM 4,096 bytes are exact. Of the SRAM
1,371 bytes, 1,247 compare exactly; the remaining 124 bytes are the 31
function relocation words deliberately unresolved in the bounded linker
fixture. A prior linked selector receipt validates the selector and deinit
relocations; two task entry targets are selected C providers.
This oracle uses Cortex-M4 C output because Unicorn cannot execute the
Cortex-M55 low-overhead-loop instruction produced by the selected compiler;
Cortex-M55 archive compilation passed separately.

Seven additional pointer words in the middle object now use source symbols:
four context config row pointers at offsets `0x39c`, `0x3bc`, `0x3cc`,
`0x3ec`, and three platform config row pointers at `0x478`, `0x494`,
`0x4b0`. The bounded linker places the two source tables at their original
addresses, and the native oracle compares those seven words without
normalization. This first config pointer pass increased the ARM object's
`.rodata` relocations to 36. The subsequent EasyLogger and task entry pass
below raises the total to 50 source relocations. Remaining numeric address
fields need the final source relocation and layout audit.

The next 12 pointer slots are EasyLogger metadata. Stock `0x434178..0x43418f`
contains six 4-byte level labels (`A/`, `E/`, `W/`, `I/`, `D/`, `V/`), while
`0x43403c..0x43406b` contains six 8-byte ANSI color suffix rows. New
`initializer_callbacks/elog_metadata.c` source-defines both tables and the
scatter SRAM slots `0x31c..0x348` now relocate to those symbols. The bounded
source linker places both tables at their authenticated addresses; fresh
oracle checks exact table bytes and all 12 pointer words without
normalization. Two additional task entry slots (`0x4cc`, `0x4f4`) now
relocate to selected C providers for DFU thread initialization and the
manager callback. Their runtime addresses are normalized in this bounded
oracle because those provider bodies are outside its link fixture. The
Cortex-M55 archive includes the real providers. The 1,371-byte comparison
therefore normalizes 31 function relocation words (124 bytes) while all
semantic scalar, text table, and table-pointer bytes match.

Three storage callback pointer slots at initialized SRAM offsets `0x200`,
`0x204`, and `0x208` now relocate to the selected source-owned read,
program, and erase-validation veneers. The veneers preserve the stock
published callback ABI and branch to C bodies. The bounded scatter fixture
does not link those bodies, so its normalized function pointer area grows
to 34 words (136 bytes); all remaining 1,235 initialized bytes compare
exactly, including all text and config data pointers. This relocation closes
three more raw executable addresses in source data without claiming their
full runtime behavior from this scatter oracle.
