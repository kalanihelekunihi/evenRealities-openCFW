# CASE whole-image source ownership audit

## Current startup-inclusive checkpoint (2026-10-11)

The first startup-inclusive header-lead audit included 181 startup-candidate C units alongside
the 29 selected and 108 command-candidate units. Of the 426 fixed pseudocode
entries, 255 have a source-header address lead and 171 do not. These are
triage counts only: a lead is not a whole-body proof, and an address absent
from a header can still be implemented under another source name. The older
122/304 figures below are the historical command-only checkpoint.

At that checkpoint, the distinct command-plus-startup relocatable graph compiled with
21 undefined symbols. Thirteen are source-body obligations: console open/apply,
five transport callbacks (0x6e1c, 0x7f2c, 0x9684, 0xb7ec, 0xbb90), two
transport registration providers (0xaa48, 0xa93c), and four application/OTA
operations (box file open, OTA transmit, probe send, service maintenance).
Six are source-data obligations: sensor divisor/rate tables, transport action
packet seed, transport registration storage, OTA probe seed and reset GPIO
configuration. The remaining two are the box selector's ambient ABI and CRT
initial data. Final linker ownership, entry-to-source mappings, complete
behavioral qualification and physical behavior remain separate.

The subsequent heap/registration pass adds 0xb3e8/0xae0c heap source,
0xaa48 registration selector, 0xccc0/0xccf2 storage wrappers, 0xaf30 task
initializer and 0x8558/0xb4a4 callback trampoline/context lookup. The
0x8559 literal is an executable Thumb address, correcting the earlier
task-name interpretation. Its refreshed graph compiles with 20 imports:
12 source bodies, six source-data contracts, one ambient ABI and one CRT
initial data contract. The startup-inclusive lead audit is now 260/166 over
426 entries and 185 startup C units. All counts remain triage, not admission.

New bounded stock/C oracles cover the 0x9a9c reset guard (192), 0x6968
transport registration sequence (11 calls), 0x9d70/0xbb4c callbacks (256),
0x82ec one-iteration worker behavior (192), 0x1c1c transport action (256),
0xa836 event classifier (192), 0xc48c/0xc4aa event storage (256) and the
0xb3e8 first-allocation heap paths (14), 0xaa48 registration (384) and
0xaf30 task initialization (192). Their cuts do not establish whole
task, reset waveform, repeated heap operation, or hardware equivalence.

The next worker pass sources the 0xa93c descriptor selector and its 0xc9a8
dynamic / 0xca06 static task creation children. Bounded stock/C checks pass
384 selector cases, 192 dynamic allocation cases, and the existing 96 static
task-create cases. The latest command-plus-startup graph compiles with 19
imports: 11 source bodies, six data contracts, one ambient ABI and one CRT
initial-data contract. The refreshed header-lead index is 262/164 across the
same 426 entries and 187 startup C units. Final linker placement and complete
runtime/physical qualification remain open.

The fixed `g2-box-ghidra-decomp.c` contains 426 distinct function-entry
comments. The candidate graph contains 108 C translation units and links with
zero undefined symbols, but archive linkage only covers functions reached by
those units. `case-body-crosswalk.json` records header-address leads for 122
entries and no header lead for 304. These counts are a triage index, not
evidence that 304 functions lack C or that 122 have equivalent bodies.

## High-impact entry triage

| Stock entry | Pseudocode observation | Current source ownership |
| --- | --- | --- |
| `0x08000928` | Legacy command switch | `full_command_candidate.c` composes C route candidates; full linked semantics still lack a whole-entry oracle. |
| `0x08000e1c` | Binary command switch | `full_command_candidate.c` composes C routes; arbitrary accepted-frame effects are not proved. |
| `0x08009210` | Variadic formatter | `vformat_candidate.c` supplies C and 180 bounded original/source cases; whole domain remains open. |
| `0x08006e18` | Empty `return` decomp | Startup candidate now emits the same `bx lr` bytes; its large distance to the next entry is not function-body size. |
| `0x08007214` | Long application policy loop with event flags, stop mode and frame activity; decomp uses unrecovered incoming registers/stack | No attributable whole-entry C body found in selected or command-candidate sources. Requires register/stack ABI recovery before faithful reduction. |
| `0x08002fc8` | Board/application initialization and version/status work | Separate startup graph now has a full control-flow C candidate with typed physical/log contracts. Initial state setup passes eight stock/source cases; self-check retry loop passes ten at sensor/delay cuts; one successful PMIC path matches through boost-set. PMIC failure, secondary/final paths, format data and full-entry effects remain unqualified. |
| `0x08001e94` | `Z`, `0xa5`, `0xff` record scan and decode | Source-owned scan/CRC prefix now passes 15 no-header and `0x5a` bad-CRC early-return stock cases. Valid-frame command dispatch, diagnostics and payload effects remain unowned. |
| `0x08005528` | Peripheral register/transfer state machine | `transfer_control_candidate.c` now supplies the C body; `verify_case_transfer_control.py` covers bounded register/poll paths with clock-plan and tick lowers. Hardware timing and unexercised paths remain open. |

The listed gaps are first-pass source attribution findings, not claims that
these functions are all reachable from the current command handler.

## Startup, data and layout

The pinned image payload has 55,752 bytes after its 32-byte package header.
The first vector words are stack `0x20002c88`, reset Thumb entry
`0x08000145`, and two further handler entries `0x08006d71` and `0x08006779`.
The separate `startup_candidate_20261011/startup_vector_candidate.c` now
declares all 46 vector slots with typed handler symbols, supplies the
decoded reset and initial stack setup, and preserves the native default
handler loop. Its C CRT decoder and zeroing routines cover the two retained
startup descriptors: 420 initialized RAM bytes at `0x20000000` and 10,980
zeroed bytes at `0x200001a4`. The 104 compressed initializer bytes remain a
typed external product-data contract. Its isolated source link passes a
46-slot vector check (including 21 default-handler slots); the complete
startup entry matches two stock boundary calls and all 11,400 initialized
RAM bytes in the bounded original/source oracle. The SVC entry at
`0x08006e18` is source-owned with identical two-byte `bx lr`. The distinct
startup source also owns the native NMI/hard-fault loops and four vector
forwarders; the latter pass four original/source call-boundary cases. The
relocatable startup object has 56 unresolved command/product/handler symbols in
`case_startup_candidate.o.receipt.json`. It is not selected into the command
archive. `build_case_command_startup_experiment.py --output PATH` composes
the two distinct C graphs into one relocatable object without duplicate
definitions; its 51 unresolved symbols retain the real product data and
handler/application obligations. Handler bodies and final memory map remain
open. We have not
assigned arbitrary values to initialized RAM, vector slots or external flash
identity data. A full source image needs per-byte data ownership, startup
behavior, linker placement and relocation proof in addition to C bodies.

## Next finite evidence work

1. Bind every recognized function entry to a selected/candidate C body or a
   documented absent-source item. Treat header mentions as leads only.
2. Recover incoming-register and stack ABI for the `0x08007214` policy loop,
   then split it into bounded branch families with original/source checks.
3. Reduce `0x08002fc8` initialization and `0x08001e94` record parser from
   retained pseudocode with explicit product lower/data contracts.
4. Audit vector entries, reset and copy/zero startup, initialized RAM/flash
   values, and final linker layout. Keep external identity bytes as runtime
   input until product source identifies them.

There is no defensible calendar estimate from the current evidence. The
finite audit scope is 426 function entries plus startup/data/layout; the
first three substantial no-body leads above are concrete next C targets.

## Current experimental checkpoint (2026-10-11 aging exchange pass)

The separate CASE command/startup C graph builds at SHA-256
`384bf960171b0dd869ceca183282659cdc6430aca227da1f06817f7dcc2b9851`
with 18 unresolved symbols. Ten name source bodies (console apply/open,
four transport callbacks, box file open, OTA transmit, service maintenance,
send probe); six name product data (two sensor tables, action packet seed,
registration storage, OTA packet seed, reset GPIO configuration), one is
ambient box-selector ABI, and one is the CRT initial-data payload. This
classification concerns linked reachability, not all fixed-image bodies.

The startup-inclusive address-lead census now finds 266 header leads and
160 rows without a header lead among 426 retained pseudocode entries. One
no-header row, 0x08009210, already has a candidate C formatter body named
`case_vformat`; therefore a no-header row cannot be counted as missing code
without alias inspection. The other 159 require the same attribution audit.
No claim of entire image source coverage follows from the 18-import graph.

The following aging callback pass replaces the 0xb7ec import with real
0x23f4 and 0x24c0 control-child imports. Its graph has 19 unresolved symbols:
11 source bodies, six product data, one ambient ABI and one CRT initializer.
Native 0xb7ec has no marker in the 426-entry fixed pseudocode catalogue,
which confirms that the catalogue is not the full native function inventory.

Both aging-control child bodies are now source and bounded-oracle qualified;
the current strict graph has 17 unresolved symbols: nine code bodies, six
product data, one ambient ABI and one CRT initialized-data obligation. The
fixed pseudocode address-lead audit is 268/158 of 426. The non-catalogue
0xb7ec example and formatter alias still make this an incomplete whole-body
census.

Alias audit of the three largest no-header rows gives candidate source
mappings, not whole-body equivalence: native 0x08009210 is the formatter
implemented as `case_vformat`; native 0x08000928 is the legacy command
entry assembled by `case_legacy_command_candidate`; native 0x08000e1c is
the binary command entry assembled by `case_binary_command_candidate`.
The command candidates route numerous bounded, tested branches, but their
full native envelopes and all lower effects have not been proven. They
must stay qualified as candidate aliases rather than erased from the
whole-body audit.

The current 0xbb90 and typed transport-data pass reduces the combined graph
to 13 imports: eight code bodies, three product data (sensor divisor/rate
tables and reset GPIO configuration), one ambient ABI, and one CRT payload.
The 276-byte registration block at 0xd26c and 20 protocol seed bytes at
0x1d04/0x1e4c are now source-owned with exact field/label/byte checks.
Native 0xbb90 is another real function absent from the fixed pseudocode
catalogue; its C source is qualified separately by a 768-case bounded oracle.

The reset GPIO configuration at 0xd36c aliases the typed transport event
descriptor tail at 0xd26c+0x100. The two 8-entry sensor lookup tables at
0xd398/0xd3a0 are also source-owned with native-byte checks. The current
strict reachable graph has 10 unresolved symbols: eight code bodies,
ambient selector ABI and CRT initial data. This is not all CASE data:
unreached native initializers, vectors, strings and final linker placement
remain to be audited beyond this import graph.

The 0x258c probe path and exposed 0x6cf8/0x6c80/0x3bb0/0x66ac sensor
transfer chain are now C source. Bounded native comparisons pass 384, 256,
128, and 192 cases for the respective oracle cuts, including 0x66ac MMIO
writes and ready-child arguments. The strict graph has nine reachable
undefined symbols: seven code bodies, one ambient selector ABI, and CRT
initial data. The 426-entry pseudocode lead audit is 271/155. This does
not close native bodies absent from the catalogue, initialized data beyond
the reachable graph, final vector/layout placement, or hardware behavior.

Native 0x2744 OTA transmit now has distinct C source with a 384-case bounded
original/source comparison. The strict reachable graph is at eight imports:
six code bodies (two console, two transport callbacks, box file open and
service maintenance), one ambient selector ABI, and CRT initial data. The
fixed pseudocode header-lead census is 272/154 of 426. The native whole-body
inventory, initialized-data extent and final linker/vector layout are still
open outside the reachable graph.

The full outer 0x1574 box file state machine is C source with a 160-case
bounded native comparison. Five concrete bank/file child bodies are now
visible as genuine contracts (0x2f46, 0x2d48, 0x2b4c, 0x2e04, 0x2cc0).
The combined graph has 12 imports; this import increase reflects deeper
source exposure rather than lost progress. Remaining original code bodies
are console open/apply, two transport callbacks, and service maintenance.

Box children 0x2f46, 0x2d48 and 0x2cc0 now have bounded source comparisons.
The 0x497c erase executor remains a true hardware body; 0x2b4c serial copy
and 0x2e04 chunk write are still unimplemented source bodies. Current strict
combined graph has ten imports and 274/152 fixed-pseudocode header leads.
These measures do not establish full CASE initialized data, body inventory
or link layout.

The exposed box read, serial copy, chunk write and erase chain is now C
source with bounded native comparisons. The strict reachable graph returned
to seven imports: five original code bodies, ambient selector ABI and CRT
initial data. 0x1574 -> 0x2e04 passes native offset, data pointer and byte
count. Flash/option register comparisons are synthetic MMIO checks and do
not establish physical persistence. Fixed pseudocode leads: 276/150 of
426; full native body/data/layout census remains open.

Native 0x18e4 periodic maintenance is C source with 256 bounded stock/C
state and child-call cases. Four reachable code bodies remain (console
open/apply and transport callbacks 6e1c/7f2c), plus ambient selector ABI
and CRT initial data. A diagnostic format string in native 0x18e4 lacks an
explicit R1 argument; the bounded comparison only checks its text and does
not assign semantic meaning to the incidental register value.

Console open/apply 0x4480/0x4100 and their exposed 0x46a4/0x67b0 lowers
are C source with bounded native comparisons. Only callbacks 6e1c and
7f2c remain as reachable code imports, plus ambient selector ABI and CRT
initial data. This still excludes full native body/data census, final
linker placement and physical console operation.

Transport callbacks 0x6e1c/0x7f2c now have complete candidate C loops,
with bounded one-iteration comparisons of 192/224 cases. Their exposed
nine native children remain genuine source obligations, and the reachable
graph has 11 imports including ambient selector ABI and CRT initial data.
The callbacks were missing from the fixed pseudocode catalogue; its 280/146
header-lead count therefore cannot measure complete native body recovery.
Quiet diagnostics and physical device effects remain unqualified.

The subsequent original-byte CASE code pass adds 0x085c frame dispatch and
0x9b94 hex conversion, 0xa836 event choose/create, 0x9ebc/0x9f18/0x9ff0/
0xa01e power sample conversions, 0x1334 aging reset, and 0x2a68 periodic
power debounce. Strict combined C graph SHA
`daee2b5826d908c16479cd063c0ba455de3a3de1616d0db0d70f8c4f2251869e`
links with exactly two unresolved data/ambient contracts:
`case_crt_initial_data` and `case_policy_box_selector_ambient`.
`verify_case_power_samples.py` passes 384 native/source cases at PMIC/timer
cuts; `verify_case_periodic_power.py` passes 192 cases at pin/PMIC/boost/log
cuts. Physical PMIC/pin behavior, diagnostic text, and the aging reset lower
signals are outside these two new oracles. The prior fixed pseudocode audit
now reports 285 header leads and 141 no-header leads of 426; this is not a
whole native body inventory, and 0x6e1c/0x7f2c were absent from that fixed
catalogue.

Native reset reads a 104-byte compressed CRT source range at 0x0800d95c..d9c3.
The decoded output is exactly 0x1a4 bytes at 0x20000000..0x200001a3;
18 run records consume exactly 104 bytes under the recovered decoder. The decoded range 0x20000032..0x20000068 contains a dense sequence of nonzero
material requiring field attribution; it must not be replaced by zeros or a
copied opaque stock blob. `case-crt-data-audit.json` records the exact
compressed/decoded hashes and sparse nonzero runs without emitting source bytes. Final source-owned initializer, semantic field
ownership, vector placement and standalone image link remain open despite
zero reachable code imports.

Follow-up bounded checks pass native/source for 0xa836 choose/create (160
thread-mode descriptor fixtures) and 0x1334 aging reset (128 RAM/call fixtures).
The native 0x38e0 box-begin stack frame leaves selector `words[1]`
uninitialized before 0x4a00 reads it to choose an option register. The
`case_policy_box_selector_ambient` contract therefore remains real. Assigning
any default selector would erase the native caller ABI ambiguity. The CRT
initializer audit records compressed and decoded digests and record extents
without claiming a source-owned product payload.

A fresh 0x085c received-frame oracle now passes 256 stock/source fixtures,
covering raw 0xde legacy, ASCII-hex legacy, 0x7f/0xcf binary, bad lengths,
random prefixes and retry-byte state. It cuts only public command entries,
so command effects are qualified by their own separate graph rather than
claimed here.

A separate direct-call target triage (`audit_case_native_call_targets.py`) finds
406 distinct Thumb BL destinations below the registered data boundary
0x0800d26c. Six are outside the fixed 426-function pseudocode catalogue;
39 have no exact address mention in current CASE C. This is a lead list, not a
missing-function count: it includes 0x080000c0 reset veneer, 0x08009190
jump-table machinery, source-covered aliases without address comments, and
possibly disassembly through inline data. The JSON records all caller sites
and limits. Indirect calls, vector-only entries and uncalled bodies still
require separate inventory. This expands the audit beyond the reachable
import graph but does not prove whole-image code closure.

CRT field attribution improved: RAM 0x2000002a..0x20000079 is the 80-byte
PMIC expected register table consumed by native 0x9f80 compare and 0x9e0c
repair, mapping table index `i` to PMIC register `16+i`. It has 59 nonzero
bytes and decoded SHA256
`923bf3796afa2e45777f41208c1d9d7ec6f7ac4e3aa9af0984787b9ab05f23ae`.
This gives the table's meaning and exact extent, but the independent
product value source is not recovered; the table remains a data contract.
The initialized word at RAM 0x20000124 is 16,000,000 Hz used by SysTick,
console timing and clock planning. The initialized 0xaaaaaaaa word at
0x2000019c is scheduler state later cleared by native 0xc57c. The CRT
field audit records these proven consumers without synthesizing any unknown
configuration bytes.

Native call-target triage next reduced ten otherwise unnamed GPIO wrappers
at 0xba44..0xbb2c to C, with 320 bounded stock/source cases at genuine
0x4d30/0x4e9e lower cuts. The 0x01e6 zero-fill wrapper and 0xa794/a7a2
short-delay leaves also have C bodies and 192 bounded RAM/completion cases.
These import-neutral bodies expand catalogue coverage without changing the
two unresolved CRT/ambient contracts. Strict combined source link SHA is
`4892bf870137acfa72da50f3ba6e7aee367a493d26d6846717419076c15178f4`.
The direct-BL triage now has 30 address-unmentioned targets (address mention
is only a lead); the fixed pseudocode crosswalk remains a separate bound.

The direct-call leaf pass also adds 0x6782 ADC enable alias, 0x67a2 ADC
bitfield writer, and 0xa39c/0xa3ac GPIO pin-read wrappers. Their bounded
comparisons pass 320 ADC fixtures and 384 GPIO wrapper fixtures total. The
strict combined graph still has exactly CRT initializer and ambient selector
imports, SHA
`00cd074b3c7a0c186a77e786c70517e54c1cf2376b33ea01dec50c049f4e06f3`.
The refreshed direct-BL triage is 406 targets, 26 without an exact C address
mention; the fixed pseudocode header lead count is 290/136 of 426. Neither
number proves missing or complete full native bodies.

Two additional native direct-call bodies, 0x4edc tick accumulation and
0x543c RCC/flash clock snapshot, are now C with 320 bounded stock/source
RAM/MMIO fixtures. Combined source link SHA
`4ffc4e7d9ef83c48111f148374e08f0c2f378d8da1e36aa3f629006f561c1632`
keeps only the CRT initializer and ambient selector imports. Direct-BL
address-unmentioned leads are now 24; fixed pseudocode header leads are
292/134. These are audit leads, not a total body completion score.

Direct-call audit also exposed 0x5bc0, the 0x40010000 port register
0x600-mask writer. Its source passes 192 bounded MMIO fixtures. Combined
relocatable SHA is
`302b59cc174b4551ac9493d939b6da7972374cec2c3c8da91bec5110d6cb7a81`.
Twenty-three BL destinations currently lack an exact source address mention;
several are already semantically covered aliases, including 0xa13a PMIC
write-register (`case_init_pmic_write_register`) and 0x9e0c PMIC repair
(`case_init_pmic_repair`). The address-only audit does not distinguish such
aliases without a body crosswalk. The fixed pseudocode lead count is 293/133.

Native 0xca6c scheduler counter accessor is now C with 128 bounded
original/source return cases. The strict combined build SHA
`511da65dae00293034b11762ef585dbbcc5ce8f8e4d20d915daa49101a346550`
retains exactly the CRT initializer and ambient selector imports. The latest
direct BL address-unmentioned lead count is 22; fixed pseudocode header leads
are 294/132. These counts remain scope triage only.

The 80-byte table at RAM `0x2000002a..0x20000079` is specifically a
**Cellwise CW221X fuel-gauge battery profile**, rather than a generic PMIC
register-default table. Independent [Rockchip CW221X driver source](https://github.com/rockchip-linux/kernel/blob/develop-6.1/drivers/power/supply/cw221x_battery.c)
defines chip ID `0xa0` at register `0`, profile register base `0x10` and
length `80`, mode register `8` with `0x30`/`0xf0`/`0x00` transitions, update
flag bit 7 in register `0x0b`, and ready bits `0x0c` in register `0xa7`.
These independently match CASE native `0x9f80`/`0x9e0c` and its reader's
I2C bytes `0xc8`/`0xc9` (7-bit address `0x64`). CASE's separate `0x70`/`0x71`
reader addresses a different 7-bit device `0x38`. The independently published
example profile differs from the CASE table; it establishes the field's
purpose and shape, **not** the battery-specific CASE values. Those exact
values still require an attributable product battery characterization or
board configuration for independent product provenance. The authorized CASE
candidate now carries them as a named 80-byte CW221X battery-profile product
configuration extracted from the authenticated stock CRT (source address and
SHA recorded in `case_battery_profile_config.c`); the startup copy function
reconstructs only RAM `0x2000002a..0x20000079`, without embedding the opaque
compressed CRT stream. The pinned Rockchip driver and GPL-2.0 license are
stored under `third-party/cw221x-rockchip-77168c8d/` for read-only evidence
and are not linked into firmware. The exact stock-to-C table and RAM copy pass
80-byte verification. Native 0x01fc is also C as a little-endian word reader,
with 256 bounded original/source cases. The strict combined source build SHA
is `bef1e01da98460110d9627d55454aeed730f1ddc0d491b327a05ee60670b1287`;
the unresolved imported CRT initializer still owns other initialized RAM
fields, and the ambient selector remains unresolved.

The next native helper pass source-reduced 0x0294/0x02b4 64-bit shifts without
introducing compiler runtime imports, with 512 original/source cases across
shift counts 0..71. Three authentic single-`bx lr` hooks at 0x5c26, 0x5e6c,
0x5efc are preserved as identity/no-side-effect C functions and pass 384
original/source register fixtures. Combined graph SHA
`512483f76b06dea819bceb2a3b0a98c6ce8afd1c80a0c5d8cbd2a9c11242748d`
still has the same two imports. Direct BL triage is 406 targets with 16
without an exact source-address mention; most of these 16 are known source
aliases or formatter/runtime mechanisms, requiring body-envelope checks
before using the count as a coverage metric.

The 16 address-unmentioned direct BL destinations split as follows after
checking callers and native entries. `0x00c0` is the continuation within
startup's `0x00b8` veneer, and `0x0270` is the CRT decoder entry already
expressed by `case_crt_init_0270`. `0x0210` is the formatter's 64-bit
quotient/remainder helper, whose radix use is semantically represented by
`vformat_candidate.c`'s source-owned `divide_radix`, although an exact
native four-register ABI wrapper is not yet reconstructed. `0x9190` is a
return-address jump-table dispatcher; `0x9210`, `0x9638`, and `0x9658` are
formatter internals under the full formatter candidate, not separate source
imports. `0x9e0c`, `0xa0ea`, `0xa13a`, and `0xa1ac`/`0xa1ca`/`0xa1e8`/`0xa206`
are named PMIC or bus routines in the compiled startup graph under different
C symbol names. `0xbf54` and `0xbf6c` are scheduler leaf cases absorbed by
their C caller bodies. Address-only absence therefore does not imply 16
missing functions, but the formatter ABI and jump-table mechanics still need
whole-body/placement qualification for a byte-identical final image.

CRT attribution then narrowed the 420-byte initialized RAM range to one
unattributed nonzero field. Two five-word GPIO descriptors at RAM offsets
`0x14` and `0xa0` have typed C defaults (pin masks 4/8, output settings 1,
pull 0, speed 3, alternate 0), confirmed against native GPIO-config
consumers and 40 exact stock bytes. Clock, clock-plan and scheduler initial
fields reproduce 13 stock bytes; policy/IRQ flags reproduce three more.
`case_crt_init_known_defaults` clears only the 420-byte stock-zero region,
then installs those named fields and the CW221X profile. RAM byte offset
`0xfb` remains `case_crt_unattributed_field_fb`; its role is not proven.
With that single byte supplied as a test fixture, Unicorn execution produces
all 420 exact stock-decoded bytes, SHA
`d91efcf9f5409364aa0e3791d1084418682e76414c5a7b588c3c484daa0dd89a`.
The source startup uses this semantic initializer; the separately sourced
native decoder remains available for full layout work. The strict combined
graph SHA `3766ef815ca9c65102c6040ee6d9629f2acab9957eb59c4b1195c76d2ba6c88b`
has two genuine imports: the one byte and the ambient selector. This is
source-state equivalence at the RAM boundary, not byte-identical startup
code or complete image equality. Native `0x01ea` is also implemented as a
preserving memset wrapper using its actual `R1=value, R2=count` ABI, with
256 stock/source return-and-RAM cases.

The last byte at `0x200000fb` is now attributed as transport `device[7]`
mode relative to `0x200000f4`: native callback `0x9684` dispatches values
1/2/4, while the stock initial value 3 reaches its idle return path;
native aging begin `0x1334` later selects mode 4. The typed initializer
sets that one byte to 3. With no test fixture, Unicorn execution of the
semantic CRT initializer reproduces all 420 decoded stock bytes and SHA
`d91efcf9f5409364aa0e3791d1084418682e76414c5a7b588c3c484daa0dd89a`.
The strict CASE combined C graph SHA is
`acae0223a614473b84332022f91b005bd562c2d6709f1f3f184946a821112b39`
with exactly one unresolved linker import,
`case_policy_box_selector_ambient`. This closes initialized RAM values in
the candidate but not exact native CRT code, full image layout, complete
non-reachable body coverage, or physical hardware behavior.

The ambient selector import is now modeled by the actual entry-frame read in
an instruction-backed wrapper for native `0x38e0`: push `{r4,r5,r6,lr}`,
reserve 32 bytes, read word `SP+4` (caller SP−44), and pass it with the same
local-frame pointer to the C option-bit body. The C body writes the captured
value to `words[1]` before the native option-reader equivalent inspects it.
An original/source cut at the first reader call passes 128 randomized
incoming stack fixtures with equal pointer and selector. This removes the
last linker import; strict combined C graph SHA
`5523210b9b4ac9d7b0a45b71af927a9cd4454d003b5b5a2def0a0fbf3a03c03f`
has zero undefined symbols. Matching that ambient value in a final image
depends on actual caller stack reuse and layout, which the entry cut does not
establish. Zero linker imports therefore does not close whole-image native
body coverage, placement, physical effects, or byte-identical rebuilding.
### 2026-10-11 combined graph and callable census refresh

The source-only CASE command/startup graph links as an experimental absolute
ELF with zero undefined symbols using `build_case_absolute_experiment.py` and
`case_clean_experimental_layout.ld`. This is an independent source placement:
its text exceeds the official payload, and no stock-address or physical-device
equivalence follows from the link. Typed CRT initializers reproduce all 420
decoded initialized RAM bytes; this closes that source-data subcomponent only.

Fresh `case_absolute_current_round.elf` and `case-absolute-layout-audit.json`
measure one 65,196-byte load segment against the 55,752-byte official CASE
payload, a **9,444-byte overflow**. Its entry `0x0800a493` differs from the
native reset Thumb entry `0x08000145`. The `case_vformat` stock/source corpus
has also been extended from 815 to **1,068 passing cases**, including signed
and unsigned 64-bit extrema, j/z/t/L/h/hh modifiers, width and precision,
and `%n` widths. These checks improve the bounded formatter evidence without
establishing all invalid-pointer, callback, overflow or caller domains.

Later CASE source-only layout work is recorded in `CASE_LAYOUT_SIZE_ROUND.md`.
It places the reset entry at `0x08000145`, retains all 39 aligned native
pointer leads, and moves 203 authenticated semantic strings into named C
objects with relocatable references. Sixteen logger callsite bindings were
corrected from native ADR/literal loads. The latest isolated optimized and
garbage-collected C ELF has one `0x0f970` = 63,856-byte load segment, 8,104
bytes beyond the official payload, with zero unresolved imports. This is a
newer diagnostic candidate than the 65,196-byte graph above; its reachability,
final product capacity, scatter and physical effects remain unqualified.

The conservative fixed-pseudocode crosswalk currently recognizes 426 entries,
of which 303 have an address lead in a source header and 123 do not. A header
lead is not a whole-body proof, and a no-lead entry can have an implementation
under another name. Direct native BL triage recognizes 406 distinct targets;
14 lack any source address mention after sourcing the 0x08009638/0x08009658
formatter padding leaves. The remaining 14 include formatter, arithmetic,
list/heap, CW221X write, bus waveform/adapters, RAM region descriptors, and
startup veneer/runtime targets. Indirect calls, vectors, uncalled functions,
the native memory layout, firmware packaging, and hardware behavior remain
outside those counts.

The next direct-call pass resolved all 14 remaining address mentions: 0x0270
was corrected from a decompiler list-unlink artifact to the native two-record
CRT dispatcher; the CW221X writer/adapter bodies were already sourced under
semantic names; two RAM-region descriptors were newly sourced and passed 128
native/C calls; 0x0210 64-bit quotient/remainder and 0x9190 compact jump-table
helper were newly sourced and passed 263 and 256 native/C cases respectively.
The source startup veneer 0x00c0 and native formatter candidate 0x9210 are now
explicitly identified. The refreshed crosswalk has 315 of 426 header leads,
111 without, and zero direct BL targets without any address mention among 406.
These are address/ABI leads and bounded comparisons, not a proof that every
body or indirect call is covered. In particular, formatter whole-body behavior
and stock placement remain open.

The independent semantic-lead review then split the 426 fixed catalogue
entries into 318 full-address header leads, 88 abbreviated-address leads and
20 with neither. `CASE_NO_HEADER_REVIEW.md` maps those 20 to specific existing
C operations, retaining each as a source lead until relevant body/state
comparison. It also found an actual missing indirect callback at 0x080086e0;
that callback is now sourced and passes 128 randomized native/C state checks.
This catalogue still cannot establish coverage of all stock executable bytes.

The 0x08005f44 status-word OR was then lifted from the inlined probe candidate
to a standalone source body, connected to the probe path, and passed 256
native/C register cases. The latest lead triage is 319 full-address, 88
abbreviated and 19 no-header entries; this remains an address inventory rather
than whole-image equivalence.

The historical isolated `verify_case_startup_layout.py` used a linker script
that assigned stock addresses to selected unresolved child symbols. It no
longer links after typed CRT source integration. Its default entry now runs
`verify_case_startup_integrated.py`, which checks the clean source ELF's
46-entry vector and 14 typed entries plus the independent 420-byte CRT state
oracle. `--legacy` retains the old stock-address experiment, with its expected
link failure. The new gate does not claim stock-address equality.

Formatter comparison now includes 116 distinct printable constant native
logger-caller literals recovered by address from the retained decompiler,
plus 28 C-source formats and synthetic grammar cases: 293 bounded native/C
cases pass. Dynamic caller strings and arbitrary formatting inputs are not
exhausted. A clean-ELF vector forwarding oracle passes four native/source
child-call cuts; existing SysTick, PendSV and three IRQ-vector suites also
pass their bounded cuts. This qualifies source behavior at those interfaces,
not timing or real-device interrupt behavior.

The native 0x080002d6 CRT decoder and clean-ELF C decoder now produce the
same 420 initialized bytes from the authenticated 104-byte compressed source
in an independent Unicorn comparison (`verify_case_crt_decode.py`). This
qualifies the decoder's actual stock input, in addition to the typed
initializer-state comparison; it does not establish every possible malformed
compressed stream or stock instruction layout.

A deterministic 512-case format-grammar extension found stock/C differences
for character precision zero, unsigned sign flags, alternate pointer prefix,
and zero padding of character/string fields. The formatter source now models
those observed behaviors, and the native/C corpus passes 805 total cases.
This remains sampled grammar and retained caller literal coverage, not a
universal formatter proof.

Ten zero-pointer/precision edge cases further established an eight-digit
minimum for `%p`, including explicit precision zero. Native null `%s` faults
when a byte is requested; precision zero emits nothing without reading the
pointer. The source now follows those observed behaviors. The expanded
native/C formatter corpus passes 815 cases, including matched null-string
fault outcomes. The clean absolute source ELF still links with zero imports;
its text and placement remain different from stock.
