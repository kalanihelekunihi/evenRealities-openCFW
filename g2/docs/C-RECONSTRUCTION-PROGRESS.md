STATUS: IN-PROGRESS

# G2 compilable-C reconstruction ledger

## CASE interfunction frontier classified — 2026-11-11

The locked CASE interfunction gap frontier now has 349 classified rows
covering 2,184 bytes, with no unsupported rows. All row hashes match the
locked `firmware_box.raw.bin` and the rows do not overlap. The classifications
are 1,608 PC-relative literal bytes, 260 zero/alignment bytes, 28 bytes of
source-semantic data, and 288 bytes attributed to source-backed executable
functions. This is closure of the existing *interfunction frontier*, not a
proof that all CASE instructions and data have been inventoried.

The audit decoded Thumb PC-relative literal loads against the locked bytes
and checked function ownership in the Ghidra corpus. It resolved complete,
partial, and unaligned literal spans, then reviewed residual scheduler and
callback code, terminal tails, short strings, and zero alignment halfwords.
The six remaining instruction entries were written as separate C functions
in `startup_vector_candidate.c`. Five compile to self-branches and one to
`BX LR`; a retained linker section keeps their exact 12 instruction bytes
in the source-linked CASE image. Their linked addresses differ from stock,
and reachability of the isolated `BX LR` remains unproved. The CASE CRT now
calls separate C word-copy and zero helpers matching the stock loop contracts.

The focused CASE build compiles 359 C units with no duplicate strong symbols
and passes its strict link. Its image is 60,184 bytes, SHA-256
`8b764c6315d429cf06051f87fa9c010ca3adba4e25c5350ec8904d95fe01846d`.
The all-payload build and source bundle for this final change are pending.
Evidence: `g2/evidence/case-pc-literal-coverage-{complete,partial,unaligned}-20261111.json`,
`case-residual-executable-coverage-20261111.json`,
`case-scheduler-residual-coverage-20261111.json`,
`case-zero-alignment-coverage-20261111.json`,
`case-tail-string-coverage-20261111.json`, and
`case-retained-entry-c-coverage-20261111.json`.

## CASE ADC startup branch correction — 2026-11-11

The locked CASE routine at `0x080007A8` returns zero when the controller
is already enabled. Its source-linked C provider omitted this guard, so it
could write configuration during an active controller state. The guard is
now present. The three adjacent ADC startup providers also reload the
controller pointer at the stock post-helper, wait and timeout access sites.
Five focused hosted scenarios passed, covering pointer changes, the early
return and both timeout paths. The harness adapts only address-based memory
access for a host array; it does not run the stock image or validate hardware.
`sources-check`, all 4,878 enabled C compilations and seven strict payload
links passed, with no compile failures or duplicate strong symbols. The
source-linked CASE image is 60,180 bytes, SHA-256
`e88ec496541b037de81faa2807cef9dced0df2ea929edcddd772f325ad48b2c9`.
The source-only OTA is 4,638,056 bytes, SHA-256
`1828ea5e6b9267b4132a7e8cf3eca0a9db6a77fcc43d72bb053fdf5f2698166c`;
it differs from the locked target. Evidence:
[`case-adc-startup-branches-20261111.json`](../evidence/case-adc-startup-branches-20261111.json).

## Case PC-relative literal coverage batch — 2026-11-11

Eight more full case frontier spans, totaling 40 bytes, are now classified
as PC-relative literal data. Each word is loaded by a Thumb instruction
inside an inventoried function: the literals include RAM state pointers,
one peripheral address, and the constant `0x7FFFFFE8`. All frontier row
hashes match the locked case image and the rows remain nonoverlapping.
Unsupported case frontier rows fall from 194 to 186; 64 bytes are now
explicitly classified as literals across this and the startup review.
Other candidate literals still need review, and source completeness remains
open. Evidence:
[`case-pc-literal-coverage-batch-20261111.json`](../evidence/case-pc-literal-coverage-batch-20261111.json).

## Case startup literal-pool coverage — 2026-11-11

Four spans in the locked case startup image that the coverage frontier had
left as unknown code or data are now resolved. PC-relative literal loads
at `0x080000C4..CC` and `0x08000158..60` fetch the Thumb application entry,
early hook, startup entry, and MSP top. The literals at `0x080000F0..F4`
and `0x08000140..44` both hold the scheduler context pointer `0x20000128`.
The halfword at `0x080000EE..F0` is zero alignment before a literal.
All new row hashes match the authenticated case image. The frontier now
classifies 24 more literal bytes and two alignment bytes, reducing
unsupported rows from 198 to 194. This closes only those spans; remaining
case gaps and overall firmware source completeness are still open. Evidence:
[`case-startup-literal-coverage-20261111.json`](../evidence/case-startup-literal-coverage-20261111.json).

## Apollo font-chain success count — 2026-11-11

The locked font manager's node-add helper at `0x46d158` writes the new list
head but never increments the list count. Its constructor at `0x46cae0`
compares the head before and after each addition, counts successes locally,
and writes that count to list offset `+8` only when returning a valid chain.
The C helper previously incremented the list count on each addition. It now
leaves that field alone; the constructor checks head changes and publishes
the final count after linking the fonts. Linked Apollo instructions have
only the zero initialization and final count store at offset `+8`.
`sources-check`, all 4,878 enabled C compilations, and all seven strict
source links passed without failures or duplicate strong symbols. Only
Apollo-main changed versus the preceding source bundle. The source-only OTA
is 4,638,060 bytes, SHA-256
`37c3f73290aea91d7f84d1a5c08d1e7eb37d51c38d0d38145af0562cadfb507c`.
Physical font behavior and whole-firmware source completeness remain
unverified. Evidence:
[`apollo-font-chain-count-20261111.json`](../evidence/apollo-font-chain-count-20261111.json).

## Apollo tracepoint CRC ownership and EFS state span — 2026-11-11

The locked TPS1 state writer and reader both call `0x47ddfe`, which computes
the CRC of the first 12 bytes through the table routine at `0x4d34c4`.
Their C copies instead called the TPF1 packet CRC helper. Both now call the
existing state wrapper. The two C CRC implementations agreed on 4,096
generated TPS1 records, and the final linked writer and reader both call
the state wrapper.

The EFS transfer-state C array was 0x76 bytes even though its typed object
and seven stock reset sites use 0x78 bytes. In the preceding linked image,
the next one-byte state cell began exactly at the end of the 0x76-byte EFS
symbol, so a reset could clear that cell. The array is now 0x78 bytes; the
new linked EFS symbol ends exactly where the next symbol begins.
`sources-check`, all 4,878 enabled C compilations, and seven strict source
links pass without failures or duplicate strong symbols. The source-only
OTA is 4,638,060 bytes, SHA-256
`11b10a0af91729cc51e7be43ffa6e82488374d6bd42c8f55dddf0bb1b908cb52`.
Only the Apollo-main payload changed versus the preceding source bundle.
Physical behavior and overall source completeness remain unverified. Evidence:
[`apollo-tracepoint-crc-efs-state-20261111.json`](../evidence/apollo-tracepoint-crc-efs-state-20261111.json).

## EM9305 timer probe zero-count argument — 2026-11-11

The locked EM9305 timer probes at `0x31398c` and `0x3139cc` load an unsigned
halfword count. When it is zero they skip the ARC LP delay and pass zero in
`r0` to ROM probes `0x104ca4` and `0x104cb4`. The C helper previously
substituted `UINT32_MAX` for zero. It now passes the measured count for both
ROM paths, including zero. The ARCv2 `EXTH` instruction in the stock
nonzero path is unsigned, so `EXTH(count - 1) + 1` equals the original
halfword across its full range. In the linked-source object the prior
`mov.eq r0,0xffffffff` is gone; `exth.f`, the zero branch, the LP loop and
both ROM probe relocations remain. An exhaustive 65,536-count arithmetic
check passed. `sources-check`, all 4,878 enabled C compilations, and seven
strict links passed without compile failures or duplicate strong symbols.
Only the EM9305 payload binary changed versus the preceding source build.
The source-only OTA is 4,638,060 bytes, SHA-256
`30e5bc9aca683ad3707e63d5ae976fae3304dc176e388d76a2b74f034c364c4a`.
Physical timer calibration and overall source completeness remain unverified.
Evidence: [`em9305-timer-probe-zero-20261111.json`](../evidence/em9305-timer-probe-zero-20261111.json).

## Apollo-main ITCM overlay startup copy — 2026-11-11

The locked Apollo region table has an LZ77 record at `0x75d3e0` targeting
ITCM `0x40`. The GNU-linked source previously initialized no bytes there;
Renode preloaded the overlay and hid that startup gap. The Apollo source now
emits the 24-byte countdown/word-copy overlay from a naked C function and
copies it to `0x40..0x58` as the first startup record. The linked source
overlay at `0x61003c` matches the recovered locked 24 bytes exactly, and the
linker asserts its size. The record at `0x7a6c28` resolves to copy handler
`0x507471`, source `0x61003c`, destination `0x40`, end `0x58`.
`sources-check`, all 4,878 enabled C compilations, and seven strict links
passed with no compile failures or duplicate strong symbols. The source-only
OTA is 4,638,068 bytes, SHA-256
`9dfdf5c39116e35b3ad6be66306063102e5e74c73c7427a0855a48c6cb9904ed`.
In an isolated Renode run without its usual ITCM preload, address `0x40`
started at zero and all six words matched the locked overlay after startup.
The same no-preload image ran for two virtual seconds, emitted 56 HCI host
packets including advertising enable, and reported no simulator errors or
unhandled exceptions. No physical boot was attempted; source completeness
and hardware behavior remain unproven. Evidence:
[`apollo-itcm-overlay-startup-20261111.json`](../evidence/apollo-itcm-overlay-startup-20261111.json).

## Codec A BINH stage-1 clock trim success — 2026-11-11

The locked BINH A clock initializer calls a distinct wrapper at `0x10000f34`.
It enables the 32 kHz oscillator only when trim at `0x10000860` succeeds. The
C initializer previously called trim directly and discarded its result, so
this hardware clock transition was absent. It now calls an explicit C wrapper
placed at the stock address. Its 18 instruction bytes match stock at 14
positions; the four differences are relocated call offsets. The linker pins
the wrapper in the 20-byte interval before read-only data and asserts its
18-byte instruction size. The 79 internal direct-call sites in the locked
stage-1 block reach 31 targets; this wrapper and the three pinned SDK clock
helpers account for the formerly unnamed targets. The focused 367-unit codec
A build and strict link passed. The full source gate compiled 4,878 enabled
C units without failures or duplicate strong symbols, and all seven strict
links passed. The stage-1 load remains 4,756 bytes within the 12,260-byte
limit. All seven primary payload binaries are unchanged; only the packaged
codec component changed. The 4,638,028-byte source-only OTA SHA-256 is
`82a71f7ca865789b59e2f746ce87ac31329131b21617dc4ec71d875040ab6db7`.
Physical oscillator startup and overall source completeness remain unverified.
Evidence: [`codec-a-stage1-clock-trim-20261111.json`](../evidence/codec-a-stage1-clock-trim-20261111.json).

## Codec B BINH stage-1 direct-call ownership — 2026-11-11

The locked BINH B stage-1 block has 61 direct `bsr` sites to 22 distinct
targets. Twenty-one targets now have address-named C providers; the remaining
`0x10000138` is the pinned NationalChip `__module_get_info` C helper, also
present as a local symbol in the linked source ELF. The stock
`0x10001310` trim-success wrapper was previously folded into the C clock
initializer. It now has its own C function and a live call from that
initializer. Its 20-byte linked body follows the stock trim-call, failure
return, and 32 kHz enable sequence. The two indirect loader calls resolve
statically to the stage-2 and stage-1 reset entries already named in C.
A focused 332-unit codec B build and strict link passed. The full source
gate compiled 4,878 enabled C units with no failures or duplicate strong
symbols, and all seven strict links passed. Only the codec B payload and
codec component changed; the source-only OTA is 4,638,028 bytes, SHA-256
`ecddb449ef72ce49927a078fb88f886acf0ca124333f952e947c3509e39c74d1`.
Direct-call ownership does not prove instruction coverage, physical boot,
or full source completeness. Evidence:
[`codec-b-stage1-direct-call-closure-20261111.json`](../evidence/codec-b-stage1-direct-call-closure-20261111.json).

## Codec B BINH stage-1 JEDEC quad policy — 2026-11-11

The BINH B NOR initializer's C candidate grouped ESMT `0x1c3812/13` with
PUYA parts and attempted a combined status write. The locked initializer
branches around all QE status transactions for those ESMT IDs, as does the
pinned NationalChip SPL. The C initializer now returns after caching either
ESMT ID; PUYA `0x854012` and `0x856013/14` retain the two-byte write, and
other IDs retain the status-2-only path. Linked C-SKY disassembly confirms
the three dispatch routes. A focused codec B build compiled 332/332 units and
linked strictly. The stage-1 load remains 6,764 bytes within the locked
12,288-byte block. The full `make sources` gate compiled 4,878/4,878 enabled
C units without failures or duplicate strong symbols, and all seven strict
links passed. Six payload binaries are unchanged; the codec B image and
codec package changed. The 4,638,028-byte source-only OTA now has SHA-256
`063cb1a33bb2e439a6031ae12607fe53016210d6e3e170c49fd6e5ff3bf9226d`.
Full initializer behavior and physical flash transactions remain unverified;
source completeness is unproven. Evidence:
[`codec-b-stage1-jedec-quad-policy-20261111.json`](../evidence/codec-b-stage1-jedec-quad-policy-20261111.json).

## Codec A BINH stage-1 JEDEC quad policy — 2026-11-11

The BINH A NOR reader's C candidate wrongly grouped ESMT `0x1c3812` and
`0x1c3813` with PUYA parts and attempted a combined status write. The locked
reader and pinned NationalChip SPL both leave those two ESMT IDs alone. The C
branch now skips their status writes and proceeds to XIP setup; PUYA IDs
`0x854012`, `0x856013`, `0x856014` retain the combined write path and other
IDs retain the status-2-only path. A focused codec A build compiled 367/367
units, and the strict link passed. The BINH A stage-1 source load remains
4,756 bytes within the locked 12,260-byte limit; its image changed as
expected, while the separate UART codec A image stayed unchanged. The full
`make sources` gate compiled 4,878/4,878 enabled C units without failures or
duplicate strong symbols, and all seven strict links passed. Only the codec
component changed in the source-only OTA; its new 4,638,028-byte SHA-256 is
`02668eeebe7e3ea87bec6f72c88c9e62ee2de729248cd486a869ebccbceb57cb`.
Full reader behavior and hardware flash transactions remain unverified. Evidence:
[`codec-a-stage1-jedec-quad-policy-20261111.json`](../evidence/codec-a-stage1-jedec-quad-policy-20261111.json).

## Codec A BINH stage-1 clock switch table — 2026-11-11

The locked and C-linked 224-byte clock-frequency switch tables agree at 203
same-offset bytes. The other 19 words are branch targets into moved blocks;
disassembly shows the same zero-result, common-lookup and module 16/22/10/19
selection actions at each mapped target. Normalizing those addresses makes
all 224 bytes identical. The codec A stage-1 linker now checks the normalized
table hash and 19 mapped words on each source link. The focused codec A link
passed with both the UART and BINH A stage-1 images unchanged. This checks the
table and branch destinations, not the full clock-frequency function or
hardware startup. Evidence: [`codec-a-stage1-clock-switch-table-20261111.json`](../evidence/codec-a-stage1-clock-switch-table-20261111.json).

## Live CASE command routing — 2026-11-11

The linked legacy command entry at stock `0x08000928` matched 708/708
no-action opcode cases and 72/72 `0xAF`, `0xD1`, `0xDD` and `0xDF` state
cases under controlled logging. The linked nonlocal binary forwarding route
matched 288/288 cases across both framing modes, including event masks and
copied bytes. Four local binary commands (`0x50`, `0x5C`, `0x5D`, `0x68`)
matched 240/240 cases at their send, ACK and GPIO boundaries. The `0x3E`
aging-state route matched 144/144 event and state cases; `0x14` matched
523/523 sensor-reply cases, including signed scaling with edge inputs.
The `0x3D` aging-exit forwarding route matched 192/192 cases and `0x56`
OTA-state changes matched 144/144 cases at their lower-call boundaries. A narrower
offline forwarder duplicated the nonlocal stock route but
was discarded by the strict linker; its C, README and manifest unit were
removed. The manifest now has 4,883 units; 359/359 CASE units compile and
the strict CASE link is unchanged at 60,184 bytes, SHA-256
`f7135f3a8254111949f55deb2bd092ff9b7ec2e61fada299c0fe2f0916676a84`.
All 4,878 enabled G2 C units compiled and all seven payloads linked strictly;
all seven binary hashes are unchanged. The source-only OTA remains 4,638,028
bytes, SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
Other active commands, physical effects and overall source completeness
remain unverified. Evidence: [`case-command-routing-live-20261111.json`](../evidence/case-command-routing-live-20261111.json).

## Live CASE frame dispatcher — 2026-11-11

The worker's linked frame dispatcher at stock `0x0800085C` matched the locked
firmware in 12 directed and 1,024 seeded controlled-child cases. These cover
raw legacy frames, ASCII hex decoding, both binary formats, malformed frames
and retry-state updates. The old offline dispatcher was a duplicate whose
sections the strict linker discarded; its C, private header, README and
manifest unit were removed. The CASE image and all seven payload binaries
are unchanged. The manifest now has 4,884 units; 4,879 enabled C units
compiled, and all seven payloads linked strictly without duplicate strong
symbols. The source-only OTA remains 4,638,028 bytes with SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
The controlled comparison does not establish command-side or physical UART
effects. Evidence: [`case-frame-dispatch-live-20261111.json`](../evidence/case-frame-dispatch-live-20261111.json).

## CASE UART frame capacity guard — 2026-11-11

The linked CASE callback at stock `0x08006544` now checks the 16-bit `0xCF`
payload length before passing it to blocking receive. The frame buffer is
1,200 bytes at `0x20000974` and the UART handle begins immediately afterward
at `0x20000E24`. A five-byte header and trailing byte leave at most 1,194
payload bytes. The new C path rejects 1,195 and 65,535 before receiving;
stock forwards those lengths, so this is an intentional safety difference.
Controlled stock/source emulation matched 452 bounded valid callback cases,
seven blocking receive cases and ten UART wait cases against the final linked
CASE image. All 4,880 enabled G2 C units compiled and all seven payloads
linked strictly, without duplicate strong symbols. The source-only OTA is
4,638,028 bytes with SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
Physical UART behavior and source completeness remain unverified. Evidence:
[`case-uart-frame-capacity-20261111.json`](../evidence/case-uart-frame-capacity-20261111.json).

## Live CASE UART receive graph — 2026-11-11

The CASE link map exposed five compiled UART receive/frame units that the
strict linker discarded. Their stock-address functions already have live
startup providers. The superseded C, its private headers and offline READMEs
were removed from `g2/src/sources.json` and the source tree, leaving one
implementation per stock receive, bind, ISR and frame-parser function. Vector
slot 43 still points to the linked UART IRQ wrapper; the live map contains
the bind core, RX callbacks, frame parser and blocking receive helper. The
CASE image and all seven payload binaries are byte-for-byte unchanged. The
manifest now has 4,885 units, 4,880 enabled C units compiled, and seven
strict links with no duplicate strong symbols. The source-only OTA remains
4,638,024 bytes with SHA-256
`c1187eee3fa765619ad3f99a10bf2011300fc43ecb9d49a1d1399f74ee971f54`.
Physical UART behavior and overall source completeness remain unverified.
Evidence: [`case-uart-live-source-consolidation-20261111.json`](../evidence/case-uart-live-source-consolidation-20261111.json).

## CASE output setter return contract — 2026-11-11

The linked CASE output setter at stock `0x080099E8` now returns the cache
byte on a hit, zero after a failed lower write, and the possibly mutated
stack byte after a successful write and cache update. Previously its C
provider was `void` while the `0x3f` enable wrapper returned its result.
The alias and caller declarations now agree. A three-branch register-backed
host harness and the linked ARM disassembly checked the return paths. The
CASE tree compiled 366/366 units; all 4,885 enabled G2 C units compiled and
all seven payloads linked strictly, without duplicate strong symbols. The
source-only OTA is 4,638,024 bytes with SHA-256
`c1187eee3fa765619ad3f99a10bf2011300fc43ecb9d49a1d1399f74ee971f54`.
Physical output-bus behavior and source completeness remain unverified.
Evidence: [`case-sensor-setter-return-20261111.json`](../evidence/case-sensor-setter-return-20261111.json).

## CASE RAM-to-flash interrupt restoration — 2026-11-11

The linked CASE copy helper at stock `0x08003F38` now saves `PRIMASK` before
disabling interrupts and restores that exact value after its 64-word copy and
flash-busy wait. The previous C read `CONTROL` and could conditionally enable
interrupts, losing the caller's state. Stock and freshly linked source
disassembly show the same `mrs PRIMASK` / `cpsid i` / `msr PRIMASK` ordering.
The CASE tree compiled 366/366 units; all 4,885 enabled G2 C units compiled,
and all seven payloads linked strictly, without duplicate strong symbols.
The source-only OTA is 4,638,016 bytes with SHA-256
`26fe401230373641c1e280bc77a22ab37ab7551b7d652ff1f68ccd4432e361a9`.
Physical flash behavior and overall source completeness remain unverified.
Evidence: [`case-flash-primask-source-20261111.json`](../evidence/case-flash-primask-source-20261111.json).

## CASE flash controller status returns — 2026-11-11

The linked CASE C helpers for flash unlock and lock now return the status
observed in the locked firmware. Unlock checks the controller lock bit after
writing its keys; the lock helpers read back their control bits. The legacy
serial-number write at stock `0x08003664` returns the final lock status, so
its source path no longer relies on a `uint32_t` alias of a `void` provider.
Caller declarations now agree with the provider. The CASE tree compiled
366/366 units and linked strictly; all 4,885 enabled G2 C units compiled and
all seven payloads linked strictly, without duplicate strong symbols. A
register-backed host harness passed the available return and write cases.
The source-only OTA is 4,638,044 bytes with SHA-256
`edea0f8ddad60b7864ae368cbe98ca3b5fa7b2bfb2a216bd23194ce31c8013b0`;
source completeness and physical flash behavior remain unverified. Evidence:
[`case-flash-status-source-20261111.json`](../evidence/case-flash-status-source-20261111.json).

## One touch SysLib delay body — 2026-11-11

The source touch image had two implementations of stock
`Cy_SysLib_DelayCycles`: a PDL-facing loop over the unscaled requested count
and an application-facing loop with repeated stack accesses. PDL and
application callers now use one C body. Its linked loop follows stock's
`(cycles + 2) >> 2` count and add/subtract branch sequence, with one extra
post-loop instruction; physical cycle timing remains unmeasured. The duplicate
symbol is absent from the linked ELF. The focused touch build, all 4,885
enabled C units, all seven strict payload links, authenticated hybrid build,
manifest check, and 16 verifier tests passed. The source-only OTA is
4,638,012 bytes with SHA-256
`0b0c80e436802a68d1e64a7472b5d526e320f2727ba9ff8b6c92bb2baf3ddad0`.
Evidence: [`touch-syslib-delay-unified-20261111.json`](../evidence/touch-syslib-delay-unified-20261111.json).

## Seven more CAPSENSE units with Arm GNU 14.2 — 2026-11-11

Seven additional linked touch CAPSENSE units now compile with the pinned Arm
GNU 14.2 toolchain. Fresh qualification found 16 new, nonoverlapping
stock-exact C functions totaling 844 bytes; each symbol appears in the
focused source-linked touch map. The source plan now selects 87 touch regions
(5,522 bytes) and 105 G2 regions (5,640 bytes). The focused touch build and
link, all 4,885 enabled C units, seven strict payload links, authenticated
hybrid build, and 16 verifier tests passed. The source-only OTA is 4,638,064
bytes with SHA-256
`1076b59448131b3f5940221a3cc779201028a62f4d66beda82cecddb40dba6dc`.
Other code in those units and physical touch behavior remain unverified.
Evidence: [`touch-capsense-seven-gcc14-units-20261111.json`](../evidence/touch-capsense-seven-gcc14-units-20261111.json).

## Exact C CAPSENSE functions with Arm GNU 14.2 — 2026-11-11

The linked touch CAPSENSE sensing unit now uses the pinned Arm GNU 14.2
compiler. Its `Cy_CapSense_ConfigureMsclpTimer` body matches all 70 stock bytes
after its call relocation is bound to the inventoried timer helper. Fresh
qualification of that unit found 16 new, nonoverlapping exact CAPSENSE
functions totaling 1,012 bytes. The source plan now selects 71 touch regions
(4,678 bytes) and 89 G2 regions (4,796 bytes). The focused touch build,
4,885-unit full manifest build, all seven strict source links, authenticated
hybrid build, and 16 verifier tests passed. The source-only OTA is 4,638,116
bytes with SHA-256
`0d3e1caf0b298ea70950a8284d30acb809f4163b0798c856db5e49e44f8d562f`;
source completeness and hardware behavior remain unverified. Evidence:
[`touch-capsense-gcc14-exact-source-20261111.json`](../evidence/touch-capsense-gcc14-exact-source-20261111.json).

## Current source image versus stock in Renode — 2026-11-11

The freshly linked Apollo-main C image and the authenticated stock image
sent the same 56 HCI host packets in matched two-second Renode runs, ending
with advertising enable. In matched paired hub runs, Secure Connections
pairing completed, all 18 phone steps produced the same per-step notification
counts, and five touch checks matched. Both produced 16 notifications and had
zero CFSR/HFSR. Three settings notifications carried battery field 12 as 38
in the source image versus 31 in stock. At two seconds, the source and stock
telemetry both read 3.798 V, 0 mA and 25.00 °C, while their SOC words were
38 and 31. The source-only Nordic fuel-gauge provider remains an uncalibrated
estimate; the battery path is a concrete divergence to investigate. The emulator
models the other chips and does not
establish their firmware behavior or physical boot. Evidence:
[`g2-source-current-paired-simulator-20261111.json`](../evidence/g2-source-current-paired-simulator-20261111.json).

## Additional exact touch C bodies — 2026-11-11

A fresh sweep compiled all 81 enabled touch Clang source units and found seven
previously unselected, nonoverlapping stock-exact bodies: four configuration
leaf/fault functions, `_exit_halt`, and both critical-section helpers. All
seven were already linked in the source image. The source plan now covers 55
touch regions/3,666 bytes and 73 G2 regions/3,784 bytes. The authenticated
hybrid build passes with 3,666 touch bytes from C; the source-only OTA remains
nonidentical. Evidence:
[`touch-clang-exact-sweep-20261111.json`](../evidence/touch-clang-exact-sweep-20261111.json).

## Exact C touch CRT hooks — 2026-11-11

The touch image now links the GCC 14.2 CRT clone-table registration and
constructor/destructor paths from C instead of two empty hooks. The compiled
and stock-linked 32-, 40-, 44-, and 36-byte bodies match the locked touch
image exactly. The empty TM table and 25 bytes of CRT state occupy their
stock RAM addresses. The source plan covers 48 touch regions/3,640 bytes and
66 G2 regions/3,758 bytes. The full manifest compiled 4,885/4,885 enabled
C units with no failures or duplicate strong symbols; all seven strict links,
the authenticated hybrid build, and 16 verifier tests passed. The source-only
OTA is 4,638,336 bytes with SHA-256
`b7f00ac20ebf27524e55819d5124b5f6dc6eb85c396d5e493e9ede0fb627fd86`,
so it is still not the 4,301,227-byte locked artifact. Evidence:
[`touch-crt-exact-source-20261111.json`](../evidence/touch-crt-exact-source-20261111.json).

## Exact C touch lite exit — 2026-11-11

The linked touch exit path now compiles from C with the weak cleanup hook left
undefined, as in stock. The exact-source matcher records that linker state
separately from an absolute zero binding. Fresh qualification matched the
complete 40-byte exit function at stock `0xA9AC..0xA9D4`; the older symbol
inventory's 54-byte extent overlaps the following `memset`. The source plan
now covers 44 touch regions/3,488 bytes and 62 G2 regions/3,606 bytes. The
full manifest compiled 4,884/4,884 enabled C units with no failures or
duplicate strong symbols; all seven strict links and the hybrid build passed.
The source-only OTA remains nonidentical. Evidence:
[`touch-libc-exit-exact-source-20261111.json`](../evidence/touch-libc-exit-exact-source-20261111.json).

## Exact C touch init-array runtime — 2026-11-11

The touch C runtime now builds `__libc_init_array` from the pinned newlib
init-array loop. The linker binds its empty preinit range and single init
entry to the reconstructed stock RAM layout. Fresh qualification matched the
complete 72-byte code-and-literal section at the stock entry. The source plan
now covers 43 touch regions/3,448 bytes and 61 G2 regions/3,566 bytes. The
full manifest compiled 4,883/4,883 enabled C units without failures or
duplicate strong symbols; all seven strict links and the hybrid build passed.
The source-only OTA remains nonidentical. Evidence:
[`touch-libc-init-array-exact-source-20261111.json`](../evidence/touch-libc-init-array-exact-source-20261111.json).

## Exact C touch byte-loop runtime — 2026-11-11

The linked touch `memset` and `memcpy` implementations now compile from C
with the fingerprinted Arm GNU 14.2 compiler at `-Os`. Their complete 16-
and 18-byte bodies match the authenticated stock runtime exactly. The source
plan now covers 42 touch regions/3,376 bytes and 60 G2 regions/3,494 bytes.
The full manifest compiled 4,882/4,882 enabled C units without failures or
duplicate strong symbols; all seven strict links and the authenticated hybrid
build passed. The all-source bundle remains nonidentical. Evidence:
[`touch-nano-runtime-exact-source-20261111.json`](../evidence/touch-nano-runtime-exact-source-20261111.json).

## Exact touch plan points to linked C — 2026-11-11

Fresh qualification of the nine PDL units used by the source build found 38
stock-exact function bodies. Together with the two flash-address C helpers,
all 40 selected touch regions (3,342 bytes) now point to enabled, linked
source units. The old `cy_flash.c` and `cy_scb_ezi2c.c` selections were
replaced without changing any selected stock range or hash. The authenticated
hybrid bundle still passes, with 31,090 touch bytes supplied by binary
pull-through; the source-only bundle remains nonidentical. Evidence:
[`touch-linked-exact-source-provenance-20261111.json`](../evidence/touch-linked-exact-source-provenance-20261111.json).

## Source-owned exact touch flash address helpers — 2026-11-11

The row-write C path now calls separate flash address-validation and row-number
helpers. Compiled with the pinned Arm GNU 14.2 toolchain, their complete 52-
and 28-byte bodies match stock byte for byte at the independently inventoried
entries. The exact-source plan now selects these **linked C** helpers instead
of the equivalent upstream probe, without increasing its 58 G2 exact regions.
The full G2 manifest compiled 4,881/4,881 enabled C units with no failures or
duplicate strong symbols; all seven strict links and the authenticated hybrid
build passed. The all-source bundle still differs from stock. Evidence:
[`touch-flash-address-source-20261111.json`](../evidence/touch-flash-address-source-20261111.json).

## Nine touch PDL units built with the qualified compiler — 2026-11-11

The source manifest now builds GPIO, SCB common, system interrupt, system PM,
and SysTick PDL units with the fingerprinted Arm GNU 14.2 compiler, alongside
the four PDL units switched earlier. GCC's PM callback static state is pinned
to the same stock RAM cell. The full manifest compiled 4,880/4,880 enabled C
units with no failures or duplicate strong symbols, and all seven payloads
strictly linked. Only touch changed in the assembled OTA: its component gained
104 bytes and 112 more same-offset bytes match stock, but it is still 5,172
bytes shorter and the bundle is not byte-identical. Evidence:
[`touch-gcc14-nine-pdl-source-build-20261111.json`](../evidence/touch-gcc14-nine-pdl-source-build-20261111.json).

## Touch reset-copy source ownership — 2026-11-11

The source-linked `.touchdata` covers the stock 964-byte reset-copy extent.
Against the authenticated stock load image, 946 bytes match at the same data
offset. The other 18 bytes are in nine 32-bit pointers to functions or
configuration objects whose source-linked flash addresses differ. This closes
the earlier missing-generated-config *data ownership* question for that span;
it does not prove the code layout, hardware behavior, or the whole touch image.
Evidence: [`touch-reset-copy-source-ownership-20261111.json`](../evidence/touch-reset-copy-source-ownership-20261111.json).

## Arm GNU 14.2 touch PDL in the all-C source build — 2026-11-11

Four touch PDL translation units now use the fingerprinted Arm GNU 14.2.Rel1
compiler and pinned PDL input cache in the source manifest. The touch RAM
linker script places GCC's `compRunStat.0` section at the authenticated ILO
state cell. The full G2 manifest compiled 4,880/4,880 enabled C units with no
failures or duplicate strong symbols; all seven strict payload links passed.
The six-component source candidate is 4,638,140 bytes and differs from the
locked OTA. Its touch component is 5,276 bytes shorter than stock. These gates
establish a source build, not source completeness, hardware behavior, or byte
identity. Evidence: [`touch-gcc14-source-build-20261111.json`](../evidence/touch-gcc14-source-build-20261111.json).

## Exact touch PDL bodies with Arm GNU 14.2 — 2026-11-11

The locally fingerprinted Arm GNU 14.2 compiler and pinned PDL inputs match
four more complete stock touch functions: `Cy_MSCLP_Configure` (424 bytes),
`Cy_SCB_I2C_Init` (484), `Cy_SysClk_ClkHfGetFrequency` (56), and
`Cy_SysLib_SetWaitStates` (56). All 36 prior exact touch selections remain
matched. The source plan now verifies 40 touch functions and 3,342 touch
bytes, or 58 G2 functions and 3,460 bytes overall. The authenticated hybrid
build passes and matches the locked OTA by pulling through all remaining
bytes. The separate source-only candidate is still different. Evidence:
[`g2-touch-gcc14-exact-source-plan-20261111.json`](../evidence/g2-touch-gcc14-exact-source-plan-20261111.json).

## Fresh exact G2 source-plan qualification — 2026-11-11

The fingerprinted ARM GNU touch PDL run retained all 23 previously selected
exact touch functions and found 13 more, adding 534 verified stock bytes.
An audit of the checked-in G2 source plan found six stale selections: two no
longer compile to their recorded bodies and four referenced deleted source
files. The moved case critical-entry function was requalified from its current
C source, restoring 24 exact bytes. The revised plan now selects 54 current
G2 regions covering 2,440 bytes. Its default authenticated hybrid build
passes and is byte-identical to the locked OTA **using binary pull-through for
the remaining bytes**. The separate source-only candidate is still not
identical, and source completeness is unproven. Evidence:
[`g2-exact-source-plan-refresh-20261111.json`](../evidence/g2-exact-source-plan-refresh-20261111.json).

## C-compiled bootloader ROM Thumb aliases — 2026-11-11

The bootloader's remaining first-party `.S` link helper is now a C translation
unit containing three typed declarations for external resident-ROM entry
points. The ARM C compiler emits absolute Thumb function symbols and no text,
data, or BSS. The focused bootloader link and the full six-component OTA
candidate are byte-identical to their preceding source candidates. The full
G2 manifest compiled 4,880/4,880 enabled units without failures or duplicate
strong symbols, and all seven strict payload links passed. The resident ROM
bodies are outside the OTA and are not reconstructed here. Evidence:
[`bootloader-rom-thumb-aliases-c-20261111.json`](../evidence/bootloader-rom-thumb-aliases-c-20261111.json).

## Single EM9305 PML_Init source body — 2026-11-11

The older controller candidate carried a second implementation of the stock
`PML_Init` routine at `0x30f4b0`. It had no source references but occupied
252 bytes in the linked EM9305 image. That duplicate and its unused helpers
were removed; the separately recovered C body remains linked as
`opencfw_em9305_stock_30f4b0`. The focused EM9305 build compiled 775/775
units and linked. The full G2 build compiled 4,880/4,880 enabled units with
no failures or duplicate strong symbols, and all seven strict links passed.
Only the EM9305 package changed in the new source bundle. The OTA candidate
still differs from the locked artifact. Evidence:
[`em9305-single-pml-init-20261111.json`](../evidence/em9305-single-pml-init-20261111.json).

## Authenticated codec KWS weights in a source bundle — 2026-11-11

The codec A model-weight input is now a declared 120,800-byte data asset
extracted from the authenticated locked codec component, with its source
offsets and SHA-256 recorded. `make -C g2 source-bundle` links all seven C
payload candidates and assembles the six-component OTA using this asset.
The candidate codec FWPK's full 129,964-byte KWS command-and-weight region
matches the locked component byte for byte. The trained-weight candidate has
158,191 equal same-offset codec bytes, versus 40,124 with the zero-weight
fixture. The outer 4,638,044-byte candidate still differs from the locked
4,301,227-byte artifact, and model behavior has not been tested. Evidence:
[`codec-a-trained-kws-source-bundle-20261111.json`](../evidence/codec-a-trained-kws-source-bundle-20261111.json).

## Touch reset-copy zero padding from linker source — 2026-11-11

The final `STOCK-BYTES` touch reset-copy unit held only seven zero padding
bytes. The linker now fills those three gaps with zero, and the superseded C
unit was removed. The focused touch build compiled 99/99 units and linked a
28,804-byte image byte-identical to the previous source candidate. The full
G2 manifest compiled 4,880/4,880 enabled units without failures or duplicate
strong symbols, and all seven strict links passed. Touch code completeness
and hardware behavior remain unverified. Evidence:
[`touch-source-zero-padding-20261111.json`](../evidence/touch-source-zero-padding-20261111.json).

## Apollo main shared state and initialized nonce — 2026-11-11

Five address-named Apollo state groups that previously had split C storage now
share their source-defined arrays: HCI radio result, HCI error, Nema frame
buffer context, three adjacent case reconnect/force-out flags, and the four
case nonce bytes. The nonce alias uses the existing initialized word
`0x0202ffff`, which emits the required `ff ff 02 02` startup bytes. The
separate reconnect and nonce units were removed. A focused Apollo-main build
compiled 2,717/2,717 units and linked; the full G2 manifest compiled
4,881/4,881 enabled units without failures or duplicate strong symbols, and
all seven strict payload links passed. This closes the bounded duplicate
allocations found in the address-named ELF symbols; broader RAM-layout and
hardware behavior remain unverified. Evidence:
[`apollo-shared-state-aliases-20261111.json`](../evidence/apollo-shared-state-aliases-20261111.json).

## Apollo main shared EasyLogger state — 2026-11-11

The EasyLogger event-flags handle and the transport free-list head now share
the same source-defined eight-byte state cell. Previously, the named handle
linked at `0x200a25dc` while the transport state linked at `0x200b4f50`;
the handle now aliases the latter, with the free-list head at offset four.
An Apollo-main build compiled 2,719/2,719 units and linked successfully. The
full G2 manifest compiled 4,883/4,883 enabled units with no failures or
duplicate strong symbols, and all seven strict payload links passed. This
corrects one split allocation; the other Apollo RAM-address inconsistencies
and hardware behavior still need review. Evidence:
[`apollo-logger-shared-state-20261111.json`](../evidence/apollo-logger-shared-state-20261111.json).

## Touch PDL ILO measurement and clock callback — 2026-11-11

The touch ILO compensation wrapper now calls the pinned PDL C measurement
functions used by the stock wrapper. Its reset-copied PM descriptor points to
the PDL clock deep-sleep callback. The separate hand-reconstructed ILO helpers
and callback were removed, and the four PDL state cells link at the stock RAM
addresses `0x20000f1c` through `0x20000f20`. A focused touch build compiled
100/100 units and linked its 28,804-byte candidate without duplicate strong
symbols. The full G2 manifest compiled 4,883/4,883 enabled units with no
failures or duplicate strong symbols, and all seven strict payload links
passed. Source completeness, stock equivalence, and hardware behavior remain
unverified. Evidence:
[`touch-pdl-ilo-callback-source-20261111.json`](../evidence/touch-pdl-ilo-callback-source-20261111.json).

## Touch deep sleep through pinned PDL C — 2026-11-11

The touch application now calls `Cy_SysPm_CpuEnterDeepSleep` from the pinned
Infineon PDL C source, matching the stock main call target. The separate
hand-reconstructed callback executor and deep-sleep routine were removed;
the local callback unit now checks only the reset-copy ABI. A focused touch
build compiled 101/101 units and linked without duplicate strong symbols.
The linked PDL function retains the callback root at `0x20000f34` and the
`wfi` path. The full G2 manifest compiled 4,884/4,884 enabled units with no
failures or duplicate strong symbols, and all seven strict source links
passed. Clang inlines its helper functions here, and the resulting
300-byte deep-sleep function does not match the stock 104-byte function.
Hardware behavior and whole-image byte identity remain unverified. Evidence:
[`touch-pdl-deepsleep-source-20261111.json`](../evidence/touch-pdl-deepsleep-source-20261111.json).

## Touch shared power-management callback RAM — 2026-11-11

The registered clock callback previously landed in the upstream PDL root
array at `0x20000f5c`, while the C deep-sleep path read the stock root at
`0x20000f34`. The linker now places the PDL root, failed-callback array, and
last-callback cell at their stock zeroed RAM addresses (`0x20000f34`,
`0x20000f28`, and `0x20000f24`). Both the BSP clock descriptor and the
application descriptor register through that single PDL function. The unused
duplicate C registrar was removed. A focused touch build compiled 101/101
units without failures or duplicate strong symbols, and its strict link
passed. The full G2 manifest compiled 4,884/4,884 enabled units without
failures or duplicate strong symbols, and all seven strict source links
passed. Deep-sleep behavior still needs hardware validation. Evidence:
[`touch-pm-shared-root-20261111.json`](../evidence/touch-pm-shared-root-20261111.json).

## Touch BSP deep-sleep callback registration — 2026-11-11

The touch BSP now passes its reset-copied callback descriptor at
`0x20000850` to the upstream `Cy_SysPm_RegisterCallback` implementation.
The C function returns zero on success and the stock `0x06020000` error on
failure. `cybsp_init` now calls generated initialization followed by that
registration, as the locked `0x4650` call chain does. The prior source only
returned success and made two reset-reason calls absent from the stock BSP
entry. A focused 101-unit touch build and strict link passed; the registration
function and PDL provider are both retained in the 29,000-byte image. The
full G2 manifest compiled 4,884/4,884 enabled units without failures or
duplicate strong symbols, and all seven strict source links passed. The whole
touch image and hardware behavior remain unverified. Evidence:
[`touch-bsp-pm-registration-20261111.json`](../evidence/touch-bsp-pm-registration-20261111.json).

## Touch EEPROM reset-copy source ownership — 2026-11-11

The touch image now links the typed, mutable 12-byte EEPROM configuration at
`0x200004c0` from `reset_owned_data.c` instead of copying a stock-byte array.
Its fields compile to the exact 12 bytes in the authenticated reset image.
Removing the duplicate `SystemCoreClock` from that unit allowed it into the
touch source composition without a duplicate strong symbol. A focused touch
build compiled 101/101 units and linked; the resulting 28,844-byte image is
byte-for-byte unchanged from the previous C candidate. The full G2 manifest
compiled 4,884/4,884 enabled units without failures or duplicate strong
symbols, and all seven strict source links passed. Overall touch image
identity and hardware behavior remain unverified. Evidence:
[`touch-eeprom-reset-copy-source-20261111.json`](../evidence/touch-eeprom-reset-copy-source-20261111.json).

## Touch CRT reset-copy hooks and exit path — 2026-11-11

The touch reset copy now carries C-linked init and fini function pointers at
`0x2000087c` and `0x20000880` instead of eight placeholder zero bytes. The
reset-entry C visits the one init entry after data and BSS initialization,
matching the locked image's empty preinit array and one-entry init array.
If the application returns, the C exit wrapper visits the optional cleanup
callback at `0x20000f54` and enters the terminal loop. The source hook bodies
have no work because this image has no TM clones.
The focused touch build compiled 101/101 units without failures or duplicate
strong symbols, and its strict link passed. The full G2 manifest compiled all
4,884 enabled units without failures or duplicate strong symbols, and all
seven strict payload links passed. The linked pointers resolve to
Thumb addresses in the new image; the 28,844-byte touch payload is 5,588
bytes shorter than the locked application and has not been tested on hardware.
Evidence: [`touch-crt-hook-source-20261111.json`](../evidence/touch-crt-hook-source-20261111.json).

## Codec A BINH stage-1 module lookup — 2026-11-11

The C module lookup at `0x10000160` now matches all 164 locked bytes. A
stage-1 copy of the pinned MIT-licensed SDK clock header changes only the
ordering of its direct-table candidate comparison and `info->param` clear;
the strict linker pins that header's digest and checks the function bytes.
A focused codec A build compiled 367/367 units and linked successfully. The
full G2 manifest compiled 4,884/4,884 units without failures or duplicate
strong symbols, and all seven strict payload links passed. The
exact clock-source and clock-gate functions remain unchanged; same-offset
agreement in the non-padding stage-1 load rose from 2,212 to 2,228 bytes.
Evidence: [`codec-a-stage1-module-lookup-20261111.json`](../evidence/codec-a-stage1-module-lookup-20261111.json).

## Codec A BINH stage-1 clock placement — 2026-11-11

The C clock-source leaf now links at `0x1000014c` and matches all 20 stock
bytes. Moving the module lookup to its observed `0x10000160` address, placing
the clock-gate and clock-frequency sections at `0x100005a4` and `0x100006a4`,
and pinning the switch tables at `0x10000f48` makes the 256-byte C clock-gate
function byte-identical to stock. The source linker checks both new exact
ranges. The 4,756-byte stage-1 load still has exact vectors and initialized
data; the remaining 7,504 bytes of the locked boot block are all zero and
the source wrapper pads that tail. Same-offset agreement in the non-padding
load rose from 1,476 to 2,212 bytes. The
module lookup matches 148/164 bytes, clock frequency 288/448, and switch
tables 203/224; their remaining differences need separate work. The fresh
full manifest build compiled 4,884/4,884 enabled G2 units with no failures
or duplicate strong symbols, and all seven strict source links passed. A
synthetic zero-weight OTA candidate authenticated against the locked bundle
remains different in all six components; the codec component's same-offset
agreement rose from 39,052 to 40,108 bytes.
Evidence:
[`codec-a-stage1-clock-placement-20261111.json`](../evidence/codec-a-stage1-clock-placement-20261111.json).

## Codec A BINH stage-1 XIP divider call — 2026-11-11

The locked flash-reader path calls unsigned division with arguments 24 and 4,
shifts the result by four, and ORs it with `0x08c09406` before programming
XIP control. The source now expresses that call through the existing C helper
instead of hard-coding the folded `0x08c09466` value. A focused codec A build
compiled 367/367 units and its strict link passed. The stage-1 load still fits
at 4,756 bytes, with the 254-byte stock-matched SPI function range preserved.
The C reader now occupies 536 bytes including its literal pool, the same span
as the locked reader, but its bytes and location still differ.
The divider helper has not been placed at its stock address, so the complete
reader remains a source candidate. Evidence:
[`codec-a-stage1-xip-divider-20261111.json`](../evidence/codec-a-stage1-xip-divider-20261111.json).
A separate ignored linker probe placed the 536-byte reader at its stock address
but matched only 41 bytes there; the production layout was not changed for
that probe. See
[`codec-a-stage1-reader-placement-probe-20261111.json`](../evidence/codec-a-stage1-reader-placement-probe-20261111.json).

## Codec A BINH stage-1 SPI helper placement — 2026-11-11

Five existing C-compiled functions now occupy their locked addresses from
`0x10000b40` through `0x10000c3e`: clock status, SPI idle wait, flash write,
flash transaction, and flash ready wait. All 254 function bytes match the
authenticated codec component at those addresses. The source linker checks
that range and the two previously placed SDK helper ranges on each BINH A
stage-1 link. A focused codec A build compiled 367/367 units without failures,
duplicate strong symbols, or unresolved symbols; its strict link passed.
The source load remains 4,756 bytes with exact vectors and initialized data.
The full G2 manifest then compiled 4,884/4,884 enabled units without failures
or duplicate strong symbols, and all seven strict source links passed.
The other stage-1 code and complete codec payload remain unverified. Evidence:
[`codec-a-stage1-spi-placement-20261111.json`](../evidence/codec-a-stage1-spi-placement-20261111.json).

## Codec A BINH stage-1 C helper placement — 2026-11-11

The C-compiled SDK helpers `__reg_set_val` (18 bytes) and
`__module_get_div.isra.1` (28 bytes) now link at their locked BINH A stage-1
addresses, `0x10000138` and `0x10000204`, with exact stock function bytes.
The intervening source module lookup is placed to fit the bounded boot
block but does not match stock. The 4,756-byte source load still has exact
vectors and initialized data. A fresh manifest build compiled 4,884 enabled
units with zero failures or duplicate strong symbols. All seven strict source
links and the synthetic six-component candidate build passed; the complete
codec and outer OTA remain different from stock. Evidence:
[`codec-a-stage1-helper-placement-20261111.json`](../evidence/codec-a-stage1-helper-placement-20261111.json).

## Authenticated six-component candidate comparison — 2026-11-11

The repeatable comparison tool authenticates the locked manifest and each
official component against `g2/workflow/target.json`, validates the source
candidate's EVENOTA structure and link receipt, and reports per-component
size and same-offset byte differences. None of the six candidate components
is byte-identical. The codec's 9,164-byte KWS command window is exact; its
weight input is still synthetic. The source candidate is 295,664 bytes larger
for Apollo main, 36,748 larger for EM9305, 5,633 larger for the bootloader,
4,416 larger for case, and 5,644 smaller for touch. These are placement and
compiler diagnostics, not a classification of missing executable code.
Evidence: [`g2-source-candidate-comparison-20261111.json`](../evidence/g2-source-candidate-comparison-20261111.json).

## Six-component source OTA candidate — 2026-11-11

The strict source linker now assembles all seven linked G2 payload candidates
into a six-component EVENOTA candidate, combining codec A and B into one FWPK.
It uses recovered container metadata and recomputes sizes and CRCs; it reads
no official component bytes during assembly. A synthetic, all-zero codec
weight fixture exercised the complete path. Structural validation passed for
the 4,638,044-byte candidate, but it differs from the locked 4,301,227-byte
artifact and has no functional trained model. It is not a release or evidence
of source completeness. The source-linked Apollo main, EM9305 and case images
also differ in size from stock. Evidence:
[`g2-source-candidate-bundle-20261111.json`](../evidence/g2-source-candidate-bundle-20261111.json).

## Codec A candidate packaging from source regions — 2026-11-10

The strict G2 source linker can now assemble its separately linked BINH A
stage-1, XIP, and SRAM loads with the C-generated KWS command stream into a
BINH A candidate when given a 120,800-byte weight asset and matching JSON
SHA-256 provenance. If codec B is selected in the same run, it also packages
the UART and BINH images into a codec FWPK candidate. A synthetic all-zero
weight fixture in ignored `build/` exercised both wrappers; the output's NPU
command and weight windows matched their declared inputs, and an incorrect
weight digest was rejected before linking. This establishes the packaging
path only. The repository still lacks a sourced trained model, and the
resulting synthetic image is not a functional firmware release. Evidence:
[`codec-a-source-candidate-packaging-20261110.json`](../evidence/codec-a-source-candidate-packaging-20261110.json).

## Codec A KWS command corpus — 2026-11-10

Field-level C descriptors and encoders under `g2/src/codec/npu/` now cover
all 212 commands in the locked 9,164-byte GXNPU KWS stream. The host C oracle
compares every emitted record and the assembled stream with the authenticated
codec firmware. `make -C g2 kws-command-stream` writes this stream from the C
sources under `build/` without reading the official firmware. The seven-payload
strict source link also emits it as a separate codec A source region. These source
units remain compile-only while the 120,800-byte
trained weight block lacks a declared source. Some command control-bit and
geometry-axis meanings remain unresolved. This command-stream match does not
qualify the codec executable, BINH A, FWPK bundle, or hardware behavior.
Evidence: [`codec-a-kws-command-corpus-20261110.json`](../evidence/codec-a-kws-command-corpus-20261110.json).

## Codec BINH A stage-1 source link — 2026-11-10

The BINH A stage-1 tree now includes C candidates for clock initialization,
clock trim and frequency policies, timer configuration, unsigned division,
oscillator control, and initialized boot state. Its nine source units compose
and link into a separate boot image at `0x10000000`, without an undefined
symbol. The 4,756-byte source load fits the locked 12,260-byte stage-1 limit.
Its 256 vector bytes and 620 initialized-data bytes at
`0x20001028..0x20001294` match stock exactly. The code does not match stock;
the candidate is not hardware-qualified. BINH A XIP and SRAM still exceed
their locked spans, and source NPU weights are missing, so a
complete source BINH A or FWPK cannot yet be built. Evidence:
[`codec-a-stage1-source-link-20261110.json`](../evidence/codec-a-stage1-source-link-20261110.json).
The stable full manifest build compiled 4,877/4,877 enabled G2 units with no
failures or duplicate strong symbols. All seven strict source links passed
without an external binary archive; the existing codec A UART image remained
unchanged while its separate BINH A stage-1 candidate was added.

## Codec BINH A stage-1 reset and boot dispatch — 2026-11-10

Added C-compilable source for the BINH A stage-1 vector table, naked reset
entry, default handler, boot setup, audio gate, boot-mode read, clock status
and setup, and timer-start wrapper. The 64 stock vector words point to reset
at `0x10000100` and the default loop at `0x10000130`. The default handler,
return-only leaf, and clock-status leaf compile to the exact stock bytes.
The other six measured function bodies have the stock lengths and match
outside call or address relocations. A relocatable composition of the seven
stage-1 C units leaves clock initialization, timer configuration, and the
image-A SRAM reset symbol external; the SRAM reset already has C source in
the codec A tree. The stage-1 block is still excluded from the final codec A
link. Evidence: [`codec-a-stage1-startup-boot-c-review-20261110.json`](../evidence/codec-a-stage1-startup-boot-c-review-20261110.json).
The stable full manifest build compiled 4,875/4,875 enabled G2 units with
zero failures or duplicate strong symbols. All seven strict source links
passed without an external binary archive, and the linked codec A binary is
unchanged.

## Codec BINH A stage-1 clock gate — 2026-11-10

Reconstructed the stage-1 `0x100005a4` clock-gate dispatcher from the pinned
GRUS clock policy. Its 256-byte C-SKY function body has the stock length and
matches stock outside two literal-address relocations and two calls to the
module descriptor lookup helper. The helper compiles to the stock 164-byte
length but has a different instruction schedule near its entry. Composing
the clock gate with the C loader, NOR reader, and SPI transactions leaves no
undefined symbols. This proves closure only for those candidate units; the
complete BINH A stage-1 boot block remains unlinked and unverified.
The stable full manifest build compiled 4,872/4,872 enabled G2 units with
zero failures or duplicate strong symbols; all seven strict source links
passed without an external binary archive. The codec A linked binary is
unchanged because these stage-1 candidates remain `link:false`.
Evidence: [`codec-a-stage1-clock-gate-c-review-20261110.json`](../evidence/codec-a-stage1-clock-gate-c-review-20261110.json).

## Codec BINH A stage-1 SPI transactions — 2026-11-10

Added C candidates for the locked BINH A stage-1 SPI write at `0x10000b5c`
and read at `0x10000bbc`. Each compiles to 96 bytes, the stock function
length. Comparing their object sections with the locked stage-1 load leaves
only the two call relocations to the bus-busy poll in each function; all
other bytes match. Composing these functions with the loader and NOR reader
resolves both SPI references. The separately reconstructed clock-gate
dispatcher closes this candidate call graph. These units are
still excluded from the final codec A link, and BINH A stage 1, its NPU
payload, and the complete FWPK are not source-built or hardware-qualified.
Evidence: [`codec-a-stage1-spi-transactions-c-review-20261110.json`](../evidence/codec-a-stage1-spi-transactions-c-review-20261110.json).

## Codec stage-1 flash readers — 2026-11-10

Added a C BINH A NOR reader candidate at `0x10000c40`, including JEDEC
handling, XIP setup and a 64 KiB SPI chunk loop. Its bus-busy poll compiles
to the exact 16 stock bytes. Its 34-byte status-ready poll matches stock
except for the unresolved call relocation. Together with the preceding C
loader, the new reader resolves the loader's flash-read reference; clock
gating and the two SPI transaction functions remain separate missing source
dependencies. The BINH A units remain `link:false` and have not been checked
on hardware. Evidence:
[`codec-a-stage1-reader-c-review-20261110.json`](../evidence/codec-a-stage1-reader-c-review-20261110.json).

The locked BINH B reader initializes SPI when its cached JEDEC word equals
`0x00ffffff`. Its linked C candidate had the condition reversed even though
the initial cached word is that sentinel. Correcting the branch changed one
byte in the 6,764-byte stage-1 load. A host check covers both sentinel and
non-sentinel paths. The 94,352-byte source BINH B package now has SHA-256
`8cd3cb7ce492b974c2fa1e86903b367fbc6f94f1c9c8efd29b0cb678669e676e`;
it still differs from stock and is not hardware-qualified. Evidence:
[`codec-b-jedec-branch-correction-20261110.json`](../evidence/codec-b-jedec-branch-correction-20261110.json).

The full manifest build compiled 4,870/4,870 enabled units with zero
failures or duplicate strong symbols, and all seven strict source links
passed without an external binary archive.

## Codec BINH A stage-1 loader C — 2026-11-10

Added a C candidate for the locked BINH A NOR scatter loader at
`0x10000a2c`. The normal branch reads the XIP length at `package+0x3000`,
copies 14,716 bytes to `0x10023400`, and enters `0x10023500`. The alternate
`0xaabbccdd` marker branch reads at `package+0x323b0`, then copies 82,060
bytes from `0x323b4+xip_length` to `0x20003000` and enters `0x10003100`.
Those addresses and branch shapes come from the locked stage-1 disassembly.
The host branch-plan check and direct C-SKY compilation pass; the focused
codec A manifest build compiled 352/352 units, and its final linked binary
is unchanged. The new unit remains `link:false` while its flash reader and
the rest of BINH A stage 1 are reconstructed. The full G2 manifest build
compiled 4,869/4,869 enabled units with zero failures and duplicate strong
symbols; all seven strict source links passed without an external binary
archive. See
[`codec-a-stage1-loader-c-review-20261110.json`](../evidence/codec-a-stage1-loader-c-review-20261110.json).

## Codec image-A reset entry moved to C — 2026-11-10

Replaced the standalone image-A SRAM reset assembler unit with a naked C
translation unit. Its CPU control and stack instructions remain inline C-SKY
assembly, because they run before a C stack exists. The C unit emits the same
44 bytes as the superseded assembler section, including the exception bridge.
The focused 351-unit codec A build and final link passed; its flat binary,
UART stages, image-A regions and UART candidate package are byte-for-byte
unchanged. The full 4,868-unit G2 build and seven strict source links also
passed, with zero failures, duplicate strong symbols or external binary
archive. Apollo main differed between full build directories because six
generated LVGL objects embed their build path; its source hashes did not
change. This reproducibility gap is separate from the codec reset conversion.
See
[`codec-a-reset-c-conversion-20261110.json`](../evidence/codec-a-reset-c-conversion-20261110.json).

## Codec BINH A source boundary — 2026-11-10

The codec A source ELF already contains image-A XIP and SRAM code. The strict
link now extracts both load regions and reports their stock capacity checks.
XIP is 46,764 bytes against 36,484 stock bytes; SRAM is 14,940 against
14,716. The source SRAM vector table resets at the stock `0x10023500`, but its
exception and IRQ entries point to `0x1002351e` and `0x1002575c` instead of
the stock `0x10023640` and `0x10025574`. A garbage-collection probe reduced
XIP to 31,376 bytes while discarding 54 named stock XIP functions, so it was
not adopted.

The new BINH A and codec FWPK builders reproduce the locked bytes from stock
inputs. They reject an over-limit source image; there is still no C BINH A
stage-1 block or source NPU command/weight payload. All seven strict source
links continue to pass. Evidence:
[`codec-a-binh-source-boundary-review-20261110.json`](../evidence/codec-a-binh-source-boundary-review-20261110.json).

## Codec BINH B stage-1 source link — 2026-11-10

The eleven existing BINH B stage-1 C units were compilable but excluded from
the codec B composed object. Their profile emits shared `.text`/`.data`
sections, so merging them with image B stage 2 placed boot code in the later
image and exceeded its stock SRAM bound. The final-link path now verifies
those eleven object hashes, composes a separate stage-1 object, and maps it
into the `0x10000000` boot block. The stage-1 vector table matches stock
byte-for-byte, with reset at `0x10000100` and default handler at
`0x10000130`. Stage-1 initialized data loads at `0x10001720` with a D-bus
view at `0x20001720`. Image B stage 2 still starts at `0x10003000` and ends
at `0x10016ec0`, below the locked `0x1001708c` bound.

The source link now wraps the 6,764-byte stage-1 load and 81,600-byte stage-2
load into a 94,352-byte BINH B candidate, computing its stage-1 CRC-32/MPEG-2.
The wrapper reproduces the locked BINH B bytes exactly when given the locked
stage inputs. The source candidate is different and remains unverified on
hardware. The full manifest build compiled 4,868/4,868 enabled units with
zero failures and duplicate strong symbols; all seven strict source links
passed without an external binary archive. See
[`codec-b-stage1-source-package-review-20261110.json`](../evidence/codec-b-stage1-source-package-review-20261110.json).

## Codec UART stage-2 vectors and source segment — 2026-11-10

The codec A source image now has a 64-word UART stage-2 vector table at
`0x10002800`, reset at `0x10002900`, exception-frame entry at `0x10002950`,
exception bridge at `0x10002994`, and common IRQ entry at `0x10003124`.
The table's 256 bytes and the bridge instruction match the locked UART stage
byte-for-byte. The naked C exception entry follows the stock frame sequence;
66 of its first 68 bytes match stock, with differences in a literal load and
the C report call. The C ISR uses the same VIC active-vector field and
`0x2000984c` callback table, but its floating-point save sequence differs.
The source trap report emits the register groups through the source UART sink;
its output and interrupt behavior have not been compared on hardware.

The source linker now extracts both UART stages and builds the type-1 GX8002
boot segment with its fixed-length padding and computed additive checksum.
The stock stages reproduce the stock 38,236-byte segment exactly through the
same builder. The linked source stages are 9,408 and 24,158 bytes; they are
shorter than the stock 10,240 and 27,964 bytes, and the source candidate is
not stock-identical. The codec BINH images and NPU command/weight payload
still lack a source-built FWPK package. See
[`codec-uart-source-segment-review-20261110.json`](../evidence/codec-uart-source-segment-review-20261110.json).
The subsequent full manifest build compiled every selected G2 unit with no
failures or duplicate strong symbols, and all seven final source links passed
without an external binary archive; that receipt does not establish a
complete codec FWPK or hardware boot.

At the earlier audit, BINH B stage-1 source was outside the final link: its
11 C units were registered with `link:false`, and the codec B ELF contained neither their
`.spl.vectors` section nor their reset symbol. A source link must place those
units in the separate `0x10000000` stage-1 boot block before BINH B can be
packaged. The later section above records that source link and package. See
[`codec-b-stage1-link-gap-20261110.json`](../evidence/codec-b-stage1-link-gap-20261110.json).

## Codec UART stage-1 boot vectors — 2026-11-10

The source-linked codec A ELF had code at IRAM `0x10000000`, where the locked
FWPK UART stage 1 has a 64-word vector table. Its reset function was at
`0x10000eb4` instead of the vector's `0x10000100`. A C vector-table unit now
owns the first 256 bytes, and the linker pins reset, exception and IRQ trap
entries at `0x10000100`, `0x10000130` and `0x10000134`. All 256 vector bytes
and the two trap entries match stock; the source reset body does not. The
focused codec A build compiled 348/348 units, linked with zero undefined
symbols, and its stage-1 load image is 9,408 bytes versus 10,240 stock bytes.
See [`codec-uart-stage1-vector-review-20261110.json`](../evidence/codec-uart-stage1-vector-review-20261110.json).

The existing stage-2 reset function was also collected into stage 1 because
its symbol is named `gx8002_uart_stage1_second_entry`. It now has a dedicated
section and links at the stock stage-2 reset address `0x10002900`, with a
linker assertion. At this intermediate checkpoint the source stage-2 load
still started there, rather than at the stock vector base `0x10002800`.
The later stage-2 vector and handler work is recorded above. See
[`codec-uart-stage2-reset-review-20261110.json`](../evidence/codec-uart-stage2-reset-review-20261110.json).
Neither UART stage nor the codec BINH/NPU payload is qualified as a complete
source-produced FWPK image.

## Source package boundary audit — 2026-11-10

The touch image is linked at flash `0x3300`, but the FWPK wrapper previously
validated its reset vector against an address-zero image. That rejected the
source reset vector `0x9929` even though it is within the linked image. Both
the wrapper and validator now use the actual application flash base. The
source package path adds the touch controller's reflected CRC-32C footer to
the linked flash bytes, then the FWPK record and its independent CRC. The
stock touch payload still round-trips, and a regression test rejects an
out-of-range vector.

The seven-payload source link now emits wrapped source candidates for Apollo
main, case and touch in addition to the EM9305 record package. The touch
candidate is 28,820 bytes versus the 34,464-byte locked payload, so this is
format closure, not source completeness or byte identity. At that checkpoint,
codec A/B remained separate linked images and no source-built codec BINH or
NPU command and weight payload had been established. The later BINH B source
candidate is recorded above. See
[`touch-source-package-review-20261110.json`](../evidence/touch-source-package-review-20261110.json)
and `build/g2-all-packaging-link-20261110/link-report.json`.

## EM9305 record coverage audit — 2026-11-10

The current final-link check proves a source-linked **application** at
`0x00302400`, not a complete EM9305 firmware package. The authenticated stock
package also has 224 bytes at `0x00300000`, 656 bytes at `0x00300400`, and a
56-byte `FHDR` record at `0x00302000`. At the time of that audit, none of those
three records had a source-linked producer. The EM9305 datasheet places NVM bootloader stages
before the optional EM-Core and application, so the first two records cannot
be treated as disposable packaging. The `FHDR` contains an address field
`0x00302028`. The local SDK's public header layout and stock CRCs now establish
that this is the NVM entry address. The stock
record wrapper round-trips byte-for-byte with the existing parser, but this
does not create the record sources. Record hashes, addresses, the linked-app
scope, and qualifications are in
[`em9305-record-coverage-20261110.json`](../evidence/em9305-record-coverage-20261110.json).

The subsequent source record 2 and NVM bootloader candidate work is described
below. A zero-undefined application ELF alone does not close EM9305 firmware
coverage.

## EM9305 source record 2 — 2026-11-10

The local SDK's public `firmwareHeaderV0_t` defines the stock record 2 as a
40-byte `FHDR` followed by a 10-byte ARC NVM entry and six erased bytes.
The entry loads the stock stack top `0x80f978` and branches to the C boot loop.
The source header and entry now live in
`g2/src/em9305/boot-header/nvm_header_entry.c`, with a linker section fixed at
`0x302000`. `tools/build/em9305_record2.py` fills the firmware size and two
CRC-32 fields after linking; the CRC algorithm and span reproduce the locked
stock record exactly when given the stock entry and application. A probe link
generated a 56-byte record 2 from source without changing the 247,364-byte
source-linked application. The full seven-payload manifest build compiled
4,863/4,863 units with no duplicate strong symbols, and all seven strict
source links passed with no external binary archive. Receipts:
`build/g2-all-record2-20261110/report.json` (SHA-256
`7d7915b19ea63cacf21d9c3d469ca5ad551e3bb628b18aff555fbefea0b3cde2`)
and `build/g2-all-record2-link-20261110/link-report.json` (SHA-256
`c60478e78261beffffe868daa5e52a7982e10b0d905d80f5e0a7fbecec35d3c1`).

## EM9305 NVM bootloader source candidate — 2026-11-10

The authenticated records at `0x300000` and `0x300400` contain the NVM
bootloader entry, firmware-header accessors, CRC checking, header enumeration,
and execution selection. The local vendor SDK v4.6 symbolized ELF and public
headers identify these functions at the same addresses as the stock
disassembly. `g2/src/em9305/bootloader/nvm_bootloader.c` now implements that
path in C, linked at `0x300000` ahead of the source FHDR and application.
The source package builder emits one contiguous C bootloader record rather
than copying the two stock records, followed by the FHDR and application.

A host check loaded the four authenticated stock records into a simulated NVM
array. The C header search found `0x302000`, the firmware CRC passed, and
single-byte mutations to the payload and header were rejected. This checks
those routines against the stock image; it does not establish equivalence of
the boot-selection and reset paths, byte identity, or successful hardware boot.
The new source package is a candidate and must not be treated as a release.
The final focused EM9305 build compiled 775/775 units with no duplicate strong
symbols and linked with no undefined symbols. The source bootloader is 736
bytes at `0x300000`; record 2 remains 56 bytes, and the 247,364-byte
application is unchanged from the preceding source link. The three-record
source candidate package is 248,272 bytes. The same host check passed on that
package. Receipts are
`build/g2-em9305-bootloader-final-20261110/report.json` (SHA-256
`5f7c09ae56eba699de79a2e7ba99e113e93eed259be309b55be52c2c0f461d6c`)
and `build/g2-em9305-bootloader-final-link-20261110/link-report.json`
(SHA-256 `42c278804226cd8db662a682a3b707404b160beb239c9e1042e73fa3c0f4dcec`).
The final all-payload manifest run compiled 4,864/4,864 units with zero
failures and duplicate strong symbols. Seven final ELFs linked with zero
undefined symbols and no external binary archive. Receipts:
`build/g2-all-bootloader-final-20261110/report.json` (SHA-256
`dd7f883fa38b248f65a7002e98628e1ded88069aff15d9b7ffcc1ab6601c7f87`)
and `build/g2-all-bootloader-final-link-20261110/link-report.json`
(SHA-256 `1aa13e07395e87848dee3854ad1afd800fb40823f3deca9c88bc01ad29ec7904`).

## EM9305 boot-selection fidelity revision — 2026-11-10

The preceding 736-byte candidate selected a section by fixed priority and
left the PML boot-mode bits unchanged before entering the application. The
authenticated ARC disassembly instead gates CRC checks on reset flags, chooses
among updater, EM-Core, customer application and customer bootloader according
to PML mode bits, and updates those bits on fallback or application entry.
`bootloader/nvm_bootloader.c` now follows that observed sequence. It also
implements the stock `getNextPageIfHeaderAddress` rule, and its
`jumpToFunction` compiles to a direct ARC register jump.

The host check mapped both the authenticated four-record package and the
source candidate into an NVM array. It verified the header and firmware CRCs,
rejected separate header and payload mutations, and exercised application,
updater, EM-Core and bootloader selection across the observed PML modes and
CRC gate states. At this checkpoint the expected outcomes were transcribed
from the stock disassembly; the stock-code differential follows below.
The revised focused build compiled 775/775 units, linked with zero undefined
symbols, and produced a 1,160-byte C bootloader and a 248,696-byte three-record
candidate package. Its application and record 2 hashes remain unchanged.
Receipts: `build/g2-em9305-selection-final-20261110/report.json` (SHA-256
`7b915068e6e014b52ca14cce7f4469ca352c7a67a35984cd3361f2904db0507e`)
and `build/g2-em9305-selection-final-link-20261110/link-report.json` (SHA-256
`6a9a25d639c38aaec62abf39bb74fdce7382d06b97be1af067db77e443a4ead7`).
Physical boot and byte identity remain unverified.

### CRC-option correction and stock-code differential

The expanded QEMU ARC run reached the authenticated stock `checkCRCHeader`
with the normal option-0 G2 header. It called payload verification, exposing
an inverted condition in the C candidate: firmware option bit 8 **skips**
payload CRC verification. The C condition was corrected, so the ordinary
source image now checks the payload before boot. A host check verified the
source CRC against both stock and source packages and rejected a changed
payload; setting bit 8 skipped the check as the stock branch does.

The one-off QEMU ARC harness then called the authenticated stock record code
and the C code with identical NVM entries and PML state. Their outputs matched
across 155 cases covering section combinations, boot modes, reset-flag/CRC
gates, next-page handling and header-entry storage. The stock CRC instruction
is unsupported by this QEMU build, so the QEMU differential uses bit 8 to
skip that instruction; the payload CRC result is supported by the separate
host check. A second QEMU run loaded the complete source FHDR/application
span, retained the valid header entry after CRC verification, then rejected
that entry after one application byte was changed. Matching these functions
does not prove the whole bootloader or physical boot. The exact result is in
`g2/evidence/em9305-boot-selection-review-20261110.json`.
The current all-payload build compiled 4,864/4,864 units with zero failures
and duplicate strong symbols, then linked seven final ELFs with zero undefined
symbols and no external binary archive. The revised bootloader is 1,160 bytes;
the three-record source candidate package is 248,696 bytes. Receipts:
`build/g2-all-selection-final-20261110/report.json` (SHA-256
`40d1c2b71cf380829abf49e484b31b7f9fb74262e286a4222df97ae328225b80`)
and `build/g2-all-selection-final-link-20261110/link-report.json` (SHA-256
`450ef4664598f050ec83ab8ea9e26d26f161e710df7a3c288793ccef67dd1711`).

## Source-only fuel-gauge candidate — 2026-11-10

Apollo main now has a C provider for the five Nordic fuel-gauge API calls it
uses. The address-named shim forwards to this provider, and the final-link
tool no longer loads the Nordic binary archive. Its state of charge estimate
uses measured voltage and current with the stock firmware's 80 mAh design
capacity; the voltage curve is an **uncalibrated development estimate**. The
proprietary Nordic algorithm and undocumented EVENBAT model parameters were
not reconstructed. This is a source-only compilation milestone, not a
stock-equivalent battery implementation or permission to flash hardware.

The full G2 source build compiled 4,862/4,862 enabled units with zero compile
failures or duplicate strong symbols. All seven final ELFs linked with zero
undefined symbols and without an external binary archive. The exact aggregate
build and link receipts are in `build/g2-all-source-20261110/` and
`build/g2-all-source-link-20261110/`. A host-side contract check covered
initialization, charge and discharge direction, invalid input, and finite
time estimates. The exact final Apollo-main binary reached BLE advertising in
the lenient Renode model: 56 HCI host packets, byte-for-byte the same sequence
as the earlier archive-linked baseline. The durable hashes and qualifications
are in [`g2-source-only-link-20261110.json`](../evidence/g2-source-only-link-20261110.json).

Goal: complete compilable C with open toolchains; byte identity is not required
for this user-authorized campaign. Historical workflow gates/evidence remain unchanged.
EvenHub SDK is excluded. Compilation and relocatable composition do not prove
complete firmware, final linkage, or hardware operation.

## Payload inventory

| Payload | Registered units | Assembly syntax | Opaque markers | Candidate/unverified triage | Unresolved (report scope) |
| --- | ---: | ---: | ---: | ---: | ---: |
| apollo-main | 2835 | 172 | 17 | 2775 | 131 |
| apollo-bootloader | 381 | 205 | 4 | 381 | 3 |
| case | 408 | 106 | 3 | 407 | 0 |
| touch | 78 | 8 | 0 | 76 | 30 |
| codec-a | 344 | 35 | 4 | 322 | 5 |
| codec-b | 332 | 29 | 3 | 319 | 3 |
| em9305 | 618 | 489 | 0 | 618 | 37 |

Full per-payload unit lists, assembly/opaque unit paths, candidate/unverified paths,
and unresolved symbol lists are in
[`c-reconstruction-inventory.json`](../evidence/c-reconstruction-inventory.json).
Counts are per manifest unit, including shared units compiled into both codecs.
Assembly and opaque counts are conservative lexical triage, not an exhaustive
classification of executable bytes. Candidate/unverified is a review backlog,
not a count of proven incorrect bodies. Exact inferred-body count is unknown.
Composed ARM unresolved lists come from nm; object-only lists are definition-subtracted.

Baseline: `g2/evidence/source-build-goal-validation.json` and its referenced
full-tree/flash reports; fresh wave report supersedes payloads when available.
Codec A/B and EM9305 have object-scope unresolved counts (no composition).
Case zero unresolved does not establish source completeness.

## Coverage evidence and gaps

- Function ownership/frontiers: `g2/symbols/*.tsv`,
  `g2/tools/manifests/g2-case-final-function-frontier.tsv`,
  `g2/tools/manifests/g2-case-final-gap-frontier.tsv`.
- Existing pseudocode: `g2/research/corpus/*/ghidra/`; exports are not a
  reviewed, frozen, complete corpus.
- Historical audits: `g2/build/audits/2026-10-06-current-assessment-refresh/`
  and `g2/build/pseudocode-first/20260930T190500Z/`. They retain unknown regions,
  nested codec images, compressed initialization, and code/data ambiguity.
- Source unit counts do not cover all firmware functions. No whole-artifact
  C completeness percentage is established.

## Wave 01 — 2026-10-26

- Created this ledger and machine-readable per-payload backlog.
- Recovered missing RTC weekday helper at `0x004d3cf8` with REA/Ghidra 12.1.4;
  body hash matches authenticated pseudocode corpus. Recovered both month tables.
- Added one freestanding C unit, preserving invalid-input handling, wrapping
  arithmetic, signed remainder, and stock's unusual century/leap condition.
- 12,240 ARM-emulated stock/C comparisons passed, zero mismatches.
  Receipt: `g2/evidence/rtc-weekday-review.json`; harness/output under
  `build/g2-c-wave-01/`. This is bounded behavioral evidence, not hardware proof.
- Added G2-only `sources` and `sources-check` targets to `g2/Makefile`.
  `./g2/make.sh sources-check`: 4,996 units, 4,708 files, zero not built.
- Build: `./g2/make.sh sources SOURCES_OUT=build/g2-c-wave-01/sources`.
  Result pending; see `build/g2-c-wave-01/build.log`.
- Upstream shortcut triage: existing manifest already integrates LVGL, FreeType,
  FreeRTOS and vendor providers. No new dependency version is asserted or vendored
  without a fresh match. This wave closes a missing first-party helper instead.

## Unresolved

- [ ] Complete full G2 source build and record fresh counts.
- [ ] Close Apollo-main unresolved functions, data, runtime and linker symbols.
- [ ] Close bootloader's three remaining dependencies with provenance.
- [ ] Classify/close touch's 30 dependencies (including ROM/external boundaries).
- [ ] Compose codec A/B and EM9305 with open-toolchain startup/link layouts;
      close respective object-scope unresolved lists (5/3/37 baseline).
- [ ] Convert assembly/opaque executable providers to C where technically possible;
      explicitly account for unavoidable architecture entry/interrupt intrinsics.
- [ ] Review/replace inferred bodies; candidate backlog is not resolved by compiling.
- [ ] Account for every executable region/nested image and all required resources.
- [ ] Produce final linked payload images/bundle from complete C and validate behavior.

## g2c session (2026-10-26) — Apollo-main closure and first GNU link

All uncommitted. Tooling: `.waves/bm.sh` (rebuild into `g2/build/g2c-wave`),
`.waves/promote.py` (flip `link:false` units that fill unresolved symbols
without a strong clash), `.waves/link.sh` (arm-none-eabi-gcc final link into
`g2/build/g2c-link/`, undefined list in `.waves/link-undef.txt`),
`.waves/iarlz.py` (decodes the stock IAR LZ77 init rows to `.waves/init_*.bin`).

Apollo-main composed unresolved: 130 (original baseline) -> 104 (session start)
-> 33 now (includes 10 linker-script symbols and 3 intentionally-weak IAR stdout
selectors). 0 duplicate strong symbols throughout. Final GNU link: 50 -> 19
undefined.

Closed this session:
- Cordio svc_core/svc_dis wrappers around upstream with stock AddGroup bodies;
  AttsRemoveGroup stubbed (pinned atts_main.c has it `#if 0`; stock never calls it).
- AmbiqHAL clkmgr (rename wrapper), pin, mcuctrl from upstream ambiqhal-apollo510;
  spotmgr leaves decompiled (stock is an older AmbiqSuite than upstream).
- dmGetConnParamPtr and ~30 other defsyms (spotmgr, pwrctrl, display flush,
  wear detect, NEMA rectangle, FreeRTOS first-task entry).
- ~69 `link:false` candidate units promoted to link (graphics buffer handlers,
  display driver, SMP rows). These are candidate-quality and need review.
- GNU runtime: `runtime/g2c-gnu/g2c_vectors.c` (151-entry table from stock),
  `g2c_gnu_init.c` (IAR-row-compatible init table), `link/g2-apollo-main.ld`.
- First-party data (`runtime/g2c-data/g2c_first_party_data.c`): shell buffers,
  FAL flags, appdb table pointer, LVGL level names, role strings, menu icon,
  B2S eDMP image (from decoded stock init data), dashboard-ext rx record.
- Port leaves (`runtime/g2c-data/g2c_port_leaves.c`): OS_Tick_*, elog_port_deinit.
- Upstream InvenSense `sif_feature_extract_ir.c` (SIF_* initialisers).
- BLE leaves (`ble/g2c-leaves/g2c_ble_leaves.c`): AppDbRecordInUse,
  paired count, AppDiscRegister, AT radio reset.
- NEMA leaves (`graphics/g2c-nema/g2c_nema_leaves.c`): set_gradient(_fx),
  interpolate_rect_colors, nema_init.

Still undefined at link (19):
- nrf_fuel_gauge_* (8) + g2_npm1300_battery_model: Nordic binary-only library
  under LicenseRef-Nordic-5-Clause (forbids reverse engineering). Not
  decompiled; needs an owner decision (obtain Nordic .a, clean-room estimator,
  or leave unresolved).
- Ambiq LVGL draw units (9: arc, border, box_shadow, fill, line, mask,
  triangle, vector_shape, label). Upstream `ambiq-lvgl/src/draw/ambiq/*` exists
  but needs NemaGFX headers/library (third-party/upstream/ambiqhal-nema is empty).
- nema_vg_init_stencil_prealloc_522400 (pulls a large nema_vg context reset).

Open guesses (flagged in code): DIS 0x20003AC4 = disValSn; dual clkmgr state;
10 vector slots bound to a spin handler (0x442114, 0x4b80be, 0x4c9d44, 0x4d58a6,
0x504488, 0x57a4d8 I2S, 0x57b940, 0x5b0114, 0x5fa0c8, 0x5fa120); linker script
ignores the 67 fixed-address `*.ld` fragments; LVGL level-name slot 5 = NULL;
OS_Tick/elog deinit semantics from upstream not stock; NEMA default context size
0x100; pwrctrl enable/disable mapping (stock names "irq_off"=enable,
"irq_on"=disable by bit behaviour); profile_handler_entry 0x5fa056 aliased to
vRestoreContextOfFirstTask (stock value is 2 bytes before it).

## g2c wave 3 (2026-10-26) — ambiq draw, NemaGFX raster, fuel gauge

Link status: `.waves/link.sh` → 2 undefined (was 19):
`audio_uart_ambiq_draw_box_shadow_540036`, `audio_uart_ambiq_vector_shape_draw_5202ec`.
Build: 2868/2868 compiled, 0 duplicate strong symbols, composed ok.

Third-party drop-ins added (user-approved 2026-10-26):
| Component | Source | Version | License | Notes |
|---|---|---|---|---|
| nrf_fuel_gauge | github.com/nrfconnect/sdk-nrfxlib `nrf_fuel_gauge/` @ v3.0.2 | lib 1.0.1 (build 2025-03-24T16:07:58Z), cortex-m4 hard-float | LicenseRef-Nordic-5-Clause (`license.txt` kept) | Linked UNMODIFIED from `third-party/upstream/nrf-fuel-gauge-1.0.1`. Stock reports version `c205a2`, build `2025-04-28T13:29:15Z`: no public release has that build date, 1.0.1 is the closest earlier one. GUESS: the ABI matches (the 24-byte init params, the process/tte/ttf signatures and the VFP/SP hard-float attributes agree). |
| ambiq-lvgl draw/ambiq | already vendored | — | MIT | Upstream units arc, border, fill, line, mask_rect, triangle and vector are built in profile 57. box_shadow and private.c are excluded (box_shadow needs LV_DRAW_SW_COMPLEX; private.c needs a newer NemaGFX than the vendored headers). |
| NemaGFX headers | ambiq-lvgl/libs/nema_gfx/include and atc-miband8-fw ThinkSi NemaGFX_SDK include/ | — | Think Silicon (headers only) | No NemaGFX .c source is publicly available. The prebuilt STM32 libnemagfx .a files are not used. |

New files:
- `graphics/g2c-nema/include/gpu_patch.h` maps `lv_ambiq_gradient_create`/`dashline_create` to the 0x5fa238/0x5fa7c0 reconstructions.
- `graphics/g2c-nema/g2c_nema_raster.c` reconstructs from stock: 0x514d2c cl_enough_space (GUESS name), 0x522848 set_matrix_all, 0x522b30 raster_rounded_rect, 0x522a24 raster_triangle_f, 0x522e9c raster_quad_fx, 0x52330c raster_stroked_arc_aa, 0x523674 raster_stroked_arc_aa_mask, 0x524260 atan.
- `graphics/g2c-nema/g2c_nema_vg_init.c` reconstructs 0x522400 nema_vg_init_stencil_prealloc plus 0x5155d6, 0x515304 (context reset), 0x5675b4 and 0x5675a8. The context storage at 0x2006cd30 is sized 0x390 (GUESS).
- `drivers/power/npm1300/battery-model/g2c_npm1300_battery_model.c` holds the 5632-byte struct battery_model "EVENBAT", copied bit-exact from ROM 0x646bf8.
- `drivers/power/npm1300/battery-model/g2c_nrf_fuel_gauge_shim.c` forwards the address-named entry points to the Nordic library, and maps expf/logf/fabsf to the IAR reconstructions.

Defsym aliases: these were identified by matching the stock draw-function callee order against the upstream sources, and each is a GUESS unless noted.
- nema_raster_rect→522ae0, set_raster_color→522a16, bind_tex→4b1298, cl_*→5144fa/514384/514cf2/514d00, sin/cos→52405c/524130, f2fx→5242cc
- mat3x3 identity/translate/scale/rotate/invert→561810/561856/5618b8/561964/561b38, set_matrix→5226e8, set_matrix_translate→5228b0
- set_clip_temp→4b1516, set_clip_pop→4b1548, set_tex_color→4b146c, enable_aa→52266e, enable_aa_flags→5226b2
- lv_ambiq_color_convert→4b06a8, set_blend_fill→4b0730, set_blend_blit→4b0748, blend_mode_change→4b06c0
- lv_draw_ambiq_decode_image→4b0f50, bind_image_texture→4b0d38, stencil_buffer_adjust→4b0b5a
- stock ambiq draw arc/border/fill/line/mask/triangle → upstream lv_draw_ambiq_*
- 48a0be→lv_draw_label_iterate_characters; fmod→iar_fmod_57dc40; lv_image_decoder_close→48908c

Remaining:
- 0x5202ec is nema_vg_draw_path (not lv_draw_ambiq_vector). Its NemaVG tessellator subtree has not been reconstructed: 516b34, 516c82, 516e0c, 5171f8, 51d2e0, 51f798, 515148, 51520c, 567230, 5619f2, 4b14ca, 4b14fe.
- 0x540036 box_shadow: reconstruct from stock (lv_ambiq_shadow_blur_corner is not in g2).
- Not started this wave: em9305, touch, codec-a/b, bootloader, and the version-matching of the existing third-party/upstream sets (AmbiqSuite, Cordio, FreeRTOS, LVGL, ...).

## g2c wave 4 (2026-10-26) — NemaVG path/tessellator + box_shadow

Link status: `.waves/link.sh` → **0 undefined** (was 2). Build 2869/2869 compiled, composed unresolved 22 (aliases reduce further at link).

### Vector / shadow reconstruction
- `graphics/g2c-nema/g2c_nema_vg_path.c` (~14.8k lines): mechanical lift of 45 Ghidra decompilations covering `0x5202ec` (`audio_uart_ambiq_vector_shape_draw_5202ec` / nema_vg_draw_path) and its tessellator subtree, plus `0x540036` (`audio_uart_ambiq_draw_box_shadow_540036`).
- Closure addresses: 5202ec 540036 4b14ca 4b14fe 515148 51520c 516b34 516c82 516e0c 5171f8 51d2e0 51f798 5619f2 567230 4b1794 51778c 517796 5156b8 51a8ec 516cf8 5179d0 519290 5177a4 51785c 517e18 51b8f0 51bf7c 522622 522f1c 522f50 522fb4 523284 523a34 524218 51b140 56395c 5639e8 5657d8 51a694 516bde 51c5ec 51a660 564974 5653a0 5640e4.
- Tooling added (uncommitted): `.waves/lobpatch.py` / `lobpatch.txt` (ARMv8.1-M WLS/DLS/LE → Thumb-2 trampolines for Ghidra), `.waves/pdecomp.sh` + `G2PatchDecomp.java` (read-only LOB patch + forced signatures + two-pass param commit), `.waves/extsigs.txt` / `forcesigs.txt` / `allsigs.txt`, `.waves/pcl/` patched decompilations.
- `0x540036` Ghidra failure ("memory range beyond end of address space") was caused by an intentional crash stub at `0x5401ae` (`movs.w r1,#-1; str r0,[r1]; b .` after a failed assert). Patched that site to `movs.w r1,#1` for analysis-only decomp (not shipped).
- Local shim for `display_driver_nema_mode_commit_52294c` (stock `mov r1,r0; mov r0,#0x11c; b 514846`) so we need not flip `link:true` on the helpers unit.

### Guesses / unverified (flagged in code)
- All `extraout_*` / `unaff_*` / `in_s*` / `stack0*` leftovers zero-initialized (VFP/GPR tracking gaps after LOB and float helpers).
- `in_fpscr` ignored; `Vector*ToFloat` helpers use C casts.
- ROM float-pair slots at 0x5202d0/d8/e0 mapped to zero pairs; some `&DAT_*` sites rewritten to stock VAs.
- Float↔pointer punning via `g2c_ptr_as_float` / `g2c_float_as_ptr` at bad decomp sites.
- Fuel-gauge version still 1.0.1 vs stock `c205a2` (unchanged from wave 3).
- `g2c_nemavg_area_copy_540024` is a 16-byte struct copy (stock 0x540024).

### Other payloads (wave-4 status, no new drop-ins this turn)
| Payload | Build | Composed undef | Notes |
|---|---|---|---|
| g2-apollo-main | 2869/2869 | 22 (link 0) | vector+shadow done |
| g2-em9305 | 618/618 | 37 | no composition |
| g2-touch | 78/78 | 30 | composed |
| g2-codec-a | 344/344 | 5 | no composition |
| g2-codec-b | failed | — | `backup_stage2_gpio_irq_masks.c` |
| g2-apollo-bootloader | 381/381 | 3 | composed |

### Library sweep (partial)
Already under `third-party/upstream/`: ambiq-lvgl, ambiqhal-*, ambiqsuite-sdk, cmsis-*, cordio, easylogger, flashdb, freertos-kernel, goodix-gh3x2x, invensense-icm45608, liblc3, lvgl, lz4, nrf-fuel-gauge-1.0.1, nanopb, littlefs, … Version-matching against stock and EM9305/touch/codec vendor SDK downloads were **not** finished this turn (time spent on NemaVG/box_shadow for the clean link).

## g2c wave 5 (2026-10-26) — payload closure + library sweep start + nvg cleanup start

### Per-target link / compose status
| Payload | Build | Composed undef | Notes |
|---|---|---|---|
| g2-apollo-main | (unchanged wave 4) | 22 (link 0) | NemaVG cleanup started |
| g2-apollo-bootloader | 381/381 | **0** | compose `--defsym` ROM ABS (also `bind_resident_rom.py`); full ELF still Thumb ABS reloc warnings (ENTRY=`opencfw_boot_reset_entry`) |
| g2-codec-a | 345/345 | **0** | compose via new `csky-ld`; fpadd_parts_nan exported; stage1 CRT GUESS stubs |
| g2-codec-b | 332/332 | **0** | gpio_irq_masks compiles; sample_app linked; BSS clear stock 0x20017090..0x2002d79c |
| g2-touch | 81/81 | **0** | CapSense/PDL GUESS stubs + soft memset/uidiv; lp history enabled; CapSense v5/PDL staged (need cycfg) |
| g2-em9305 | 619/619 | **0** | compose via new `arc-ld`; ROM call bindings + GUESS app/QP/HCI closure |

### Files changed (high level)
- `tools/build/bind_resident_rom.py` — ROOT `parents[2]` fix
- `g2/src/sources.json` — csky-ld/arc-ld; codec/em compose; sample_app + touch/em glue
- codec-a: `resident_xip_fpadd_parts.c`, `uart_stage1_crt_initializers.c` (GUESS)
- codec-b: `backup_crt_clear_bss.c`, sample_app `link:true`
- bootloader: `link/g2-apollo-bootloader.ld`, `.waves/link-bootloader.sh`
- touch: `glue/touch_runtime_soft.c`, `touch_cybsp_stub.c`, `touch_pdl_capsense_stubs.c`, freestanding `string.h`; PDL symlinks in psoc4-touch-slice
- em9305: `application/em9305_link_closure.c`
- nvg: `g2c_nema_vg_path.c` — `g2c_fpscr_eq/lt` helpers; first FPSCR bitfields rewritten

### Library sweep (version-match notes)
| Component | Stock / target | Tree copy | Action |
|---|---|---|---|
| CapSense | v5.0 (upstream-map); LP APIs | `reference/infineon-capsense-v5` (5.0); pinned upstream 3.0.1 lacks LP | Prefer v5; cycfg missing → GUESS stubs for link |
| mtb-pdl-cat2 | PSoC4000T | `vendor-cache/.../touch-gcc-14.2/pdl-input` symlinked into psoc4-touch-slice | Partial |
| EM9305 SDK | product ROM | `local-vendor/sources/em9305-v4.6` (+ v4.2) | ROM addrs bound; SDK bodies not substituted |
| NationalChip LVP | image A/B | `nationalchip-lvp-kws` @ 8bf9ee5 | Already used for codec |
| AmbiqSuite | apollo-main | upstream + local R3.2.0 (`release_sdk_3_2_0-dd5f40c14b`) | Version note only |
| QP/C | 6.5.1 (myapp) | `qpc-official` acquisition | GUESS ctor/top for compose |

### Guesses (new this wave)
- uart stage1 initialize_*/start_application (stock 0x100001fc/1dd8/1378/2c8 not in seed set)
- touch CapSense/PDL/cybsp stubs; soft `__aeabi_uidiv(mod)`
- em9305 empty HCI tables; QP ctor/top; app veneers
- bootloader MRAM map in new `.ld`
- image-b BSS sentinel objects (clear uses stock absolute span)

### Remaining
- bootloader full ELF Thumb ABS; apollo-main composed-22
- touch: CapSense v5 + PDL once cycfg exists
- em9305: SDK/QP/Cordio for GUESS closure; HCI tables
- nvg: finish extraout/unaff/in_s* and remaining FPSCR bitfields; float↔pointer punning


## g2c wave 6 (2026-10-26) — real completeness: final ELF/bin + stub replacement + inventory

Goal: turn composed-0 into linked ELF/bin, replace GUESS stubs with upstream/stock, inventory remaining inference, continue nvg cleanup.

### Per-target final link status
| Payload | Composed undef | Final ELF | Final BIN | Notes |
|---|---:|---|---|---|
| g2-apollo-bootloader | **0** | `g2/build/g2c-w6-final-apollo-bootloader/g2-apollo-bootloader.elf` (290028 B) | `.bin` 171900 B | `resident_rom_thumb_set.S` (`.thumb_set` typed ABS); MRAM LENGTH 0x40000 |
| g2-codec-a | **0** | `.../g2c-w6-final-codec-a/g2-codec-a.elf` (200652 B) | `.bin` 88964 B | stage1 CRT = stock `.S` bytes |
| g2-codec-b | **0** | `.../g2c-w6-final-codec-b/g2-codec-b.elf` (173476 B) | `.bin` 89722 B | BSS stock span retained |
| g2-touch | **0** | `.../g2c-w6-final-touch/g2-touch.elf` (109504 B) | `.bin` 57572 B | CapSense v5 sensing_lp+generator_lp + PDL; text/data/bss 57416/156/1804 |
| g2-em9305 | **0** | `.../g2c-w6-final-em9305/g2-em9305.elf` (935772 B) | `.bin` 325624 B | HCI tables from stock; QP ctor/top real; NVM LENGTH 0x80000 + sdata |

Linker scripts: `g2/src/{apollo-bootloader,touch,codec,em9305}/link/g2-*.ld`. Driver: `.waves/link-final.sh`.

### Stub → real replacements
- **touch CapSense/PDL/cybsp**: upstream `infineon-capsense-v5` (`sensing_lp`, `generator_lp`, control/structure/sensing/processing/filter) + `psoc4-touch-slice` PDL (`cy_gpio/sysclk/syslib/msclp`…); `touch_cybsp.c` → `init_cycfg_all`; freestanding `stdlib.h`; `touch_syslib_cycles.c` (clang lacks `.func`); vectors + CapSense lib tails in `touch_vectors_and_capsense_tail.c`; stubs `build/link:false`.
- **em9305 HCI**: `em9305_hci_cmd_tables.c` — 56 stock entries at VMA 0x334xxx.
- **em9305 QP**: `em9305_qpc_ctor.c` — real `QHsm_top`/`QHsm_ctor`/`QActive_ctor` + minimal vtable; start/post still thin (inventory).
- **stage1 CRT**: `uart_stage1_crt_initializers.S` (stock bytes); `.c` disabled.
- **image-b BSS**: stock span in `backup_crt_clear_bss.c` retained.

### Remaining-inference inventory (definitive)
See `g2/docs/wave6-remaining-inference-inventory.md` (+ `.json`).

| target | GUESS | stub/placeholder | weak | raw-decompile | nvg leftovers |
|---|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 2 | 0 | 3 | 0 |
| g2-codec-a | 0 | 3 | 0 | 3 | 0 |
| g2-codec-b | 0 | 0 | 0 | 5 | 0 |
| g2-touch | 2 | 1 | 3 | 0 | 0 |
| g2-em9305 | 0 | 6 | 0 | 0 | 0 |
| g2-apollo-main | 104 | 28 | 3 | 14 | 340 |

### nvg cleanup (continued)
- `g2c_nema_vg_path.c`: `g2c_fpscr_*` usage ~93; leftover tokens still 245 (`in_fpscr`/`extraout_*`/`unaff_*`).
- `display_lv_init_children.c`: helpers + ~17 `g2c_fpscr_*`; leftover tokens 95.
- Bit-flag `(int)((uint)*(byte*)…<<N)<0` idioms and multiline VFP compares remain.

### Files changed (high level)
- touch: vendor `cycfg_capsense*.h`, `cycfg_peripherals.h`, glue (`touch_cybsp.c`, `touch_syslib_cycles.c`, `touch_system_core_clock.c`, `touch_vectors_and_capsense_tail.c`, freestanding `stdlib.h`, runtime aeabi), `link/g2-touch.ld`, CapSense/PDL units in `sources.json`
- em9305: `em9305_hci_cmd_tables.c`, `em9305_qpc_ctor.c`, `em9305_link_closure.c`, `link/g2-em9305.ld`
- codec: `uart_stage1_crt_initializers.S`, `link/g2-codec-{a,b}.ld`
- bootloader: `link/g2-apollo-bootloader.ld`, `link/resident_rom_thumb_set.S`
- nvg: `g2c_nema_vg_path.c`, `display_lv_init_children.c`
- build: `.waves/link-final.sh`, `g2/src/sources.json`
- docs: `wave6-remaining-inference-inventory.{md,json}`, this ledger section

### Remaining after wave 6
- apollo-main composed-22 / nvg leftover tokens (~340) and GUESS-heavy mechanical lift
- em9305: full QEQueue post / qf_actq; more SDK substitution
- touch: CapSense closed lib (`.a`) vs thin `UpdateThresholds_Lib`/`CalculateRawTarget`; cycfg from design.cycapsense
- Final images larger than stock in places (bootloader/em9305 MEMORY expanded) — not byte-identical

## Wave 7 — inference burn-down (2026-10-26 16:44 CDT)

Burned `wave6-remaining-inference-inventory` biggest-first; regenerated inventory.

| target | GUESS | stub/placeholder | weak | raw-decompile | nvg leftovers |
|---|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 0 | 0 | 0 | 0 |
| g2-codec-a | 0 | 0 | 0 | 0 | 0 |
| g2-codec-b | 0 | 0 | 0 | 0 | 0 |
| g2-touch | 0 | 0 | 2 | 0 | 0 |
| g2-em9305 | 0 | 0 | 0 | 0 | 0 |
| g2-apollo-main | 0 | 0 | 3 | 0 | 0 |

Wave6 baseline was 104/28/3/14/340 on apollo-main; nvg leftovers 340→0 (rename/lift); GUESS/stub/raw cleared.

### Link status
| target | compose U | final ELF |
|---|---:|---|
| g2-apollo-main | 22 (unchanged wave4/5 gate) | compose ok `g2/build/g2c-w7-apollo-main/` |
| g2-touch | 0 | `g2/build/g2c-w7-final-touch/` ELF+bin |
| g2-apollo-bootloader | 0 | w6 final ELF kept (comment-only edits) |
| g2-codec-a | 0 | w6 final ELF kept |
| g2-codec-b | 0 | w6 final ELF kept |
| g2-em9305 | 0 | w6 final ELF kept |

Residual weak: IAR optional putchar selects (3); PDL `Cy_SysLib_*` soft overrides in touch_cybsp (2).

### Notable proofs / fixes
- touch SP `0x20002000` (FWPK+0x20) in `touch_vectors_and_capsense_tail.c`
- `audio_uart_nema_error_set_4b127c` / `cl_node_release_514178` return types aligned to stock (via headless-decomp)
- path 0x514846 / 0x52294c / related returns verified; broken `g2c_fpscr_eq(x<0)` sites → `g2c_fpscr_lt`
- nvg: `in_fpscr`/`extraout_*`/`unaff_*` → `fpscr_bits`/`vfp_*`/`saved_*`/`vg_ctx_r6`; display got local `g2c_fpscr_*` helpers

### Files changed (high level)
- apollo-main: `g2c_nema_vg_path.c`, `display_lv_init_children.c`, `iar_stdout.c`, `g2c_*` data/port/vectors/clkmgr/ble leaves, UI comment scrub, shim/gpu_patch headers
- touch: `touch_vectors_and_capsense_tail.c`, `touch_cybsp.c`
- bootloader/codec/em9305: comment scrub only (false-positive inventory hits)
- docs: `wave6-remaining-inference-inventory.{md,json}`, this ledger section

## Wave 8 — audit of wave7 burn-down (2026-10-26 16:52 CDT)

Wave7 cleared inventory counts largely via **(c) comment scrub / renames**. Honest restore done.

See `g2/docs/wave8-audit-wave7.md` for per-class (a)/(b)/(c) tables.

### Audit split (markers removed from wave6 counts)

| target | (a) evidenced | (b) code unverified | (c) comment/rename |
|---|---:|---:|---:|
| g2-apollo-main | ~6 | ~10 | ~473 |
| g2-touch | 1 (SP) + reset entry added | CapSense thin tails | ~5 keyword scrubs |
| bootloader/codec/em9305 | 0 | 0 | all wave7 stub/raw burns |

### Honest inventory (restored)

| target | GUESS | stub | weak | raw | nvg | UNVERIFIED |
|---|---:|---:|---:|---:|---:|---:|
| bootloader | 0 | 3 | 0 | 3 | 0 | 3 |
| codec-a | 0 | 1 | 0 | 3 | 0 | 1 |
| codec-b | 0 | 0 | 0 | 5 | 0 | 0 |
| touch | 3 | 1 | 2 | 1 | 0 | 0 |
| em9305 | 0 | 2 | 0 | 0 | 0 | 2 |
| apollo-main | ~91 | ~7 | 3 | ~12 | ~341 | ~11 |

(Exact table in regenerated inventory md.)

### Link status
- apollo-main compose **U=22** — documented intentional (linker script 11 + IAR weak 3 + nrf_fuel_gauge 8)
- touch compose U=5 (`__data_*`/`__bss_*` from CRT); final ELF **U=0** with `touch_runtime_0164_reset_entry` @ stock VA 0x3464 shape
- bootloader/codec/em9305: w6 finals kept

### Files
- audit: `g2/docs/wave8-audit-wave7.md`
- touch: `glue/touch_runtime_0164_reset_entry.c`, vectors Reset_Handler → entry; `sources.json`
- nvg: restored `in_fpscr`/`extraout_*`/`unaff_*` in path + display_lv
- restored GUESS/UNVERIFIED/stub/Ghidra markers across scrubbed sites

## Wave 9 (2026-10-26, America/Chicago)

Evidence-gated burn of honest inventory. Markers removed only with stock VA +
corpus decompile/disasm or upstream file+version citation. No nvg renames
without FP/register recovery.

| target | GUESS | stub | weak | raw | nvg | UNVERIFIED |
|---|---:|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-codec-a | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-codec-b | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-touch | 2 | 2 | 2 | 0 | 0 | 0 |
| g2-em9305 | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-apollo-main | 90 | 0 | 3 | 0 | 344 | 3 |

Wave8 baseline: boot 0/3/3, codec-a 0/1/3 UV1, codec-b 0/0/5 UV4, touch 3/1/1,
em 0/2 UV2, apollo 91/7/12/341 UV11.

Link: all 6 compose ok; touch final U=0; apollo compose U=22 documented.
Details: `g2/docs/wave9-evidence-removals.md`.


## Wave 10 (2026-10-26)
- Touch: the CapSense UpdateThresholds_Lib/CalculateRawTarget stubs were removed. Their dead callers are gc-stripped, and the closed lib was proven absent from stock. Final ELF links with 0 undefined symbols.
- apollo-main: nvg 344→262 and GUESS 90→81, all in `g2c_nema_vg_path.c`. UNVERIFIED is still 3. Compose is 2869/2869 with U=22, the documented gate.
- See `wave10-evidence-removals.md` and `wave6-remaining-inference-inventory.md`.
- Bootloader final relink still fails (ld script syntax error, from Wave 9). Its compose gate is clean.

## Wave 11 (2026-10-26)
See g2/docs/wave11-evidence-removals.md. All 6 targets final-link with 0 undefined. Wave 10 apollo-main "no final link" claim corrected. apollo-main guess 81->17, nvg 262->133; touch stub/weak 0. FLAG: bootloader text overlaps 0x438000.

## Wave 12
See g2/docs/wave12-evidence-removals.md. apollo-main markers: guess 15, stub 1, weak 3, nvg 61, unverified 3. Other targets: 0. Bootloader now fits 0x410000..0x438000 with region enforcement.

## Wave 13 — loadable image origins (see g2/docs/wave13-loadable-images.md)
- touch 0x3300 / em9305 0x302400 / codec-a 0x10023400+XIP 0x10203004 / codec-b 0x10003000 now match stock, with bounded regions (overflow fails the link, tested).
- All 6 relinked from fresh w13 composes with 0 undefined: g2/build/g2c-w13-final-{touch,em9305,codec-a,codec-b,apollo-main,apollo-bootloader}.
- Step 3 (display_lv in_fpscr, draw_fill carriers, remaining apollo markers) not started; counts unchanged: guess 15, stub 1, weak 3, nvg 61, unverified 3.

## Wave 14
See g2/docs/wave14-ram-size-alias.md. touch: stock-layout reset RAM (954/964 bytes match plus relocated pointers), stack 4212 vs 4264 B. em9305: -Os, 216,988 B. codec: SRAM alias proven; codec-b overlap of 7052 B is still open. inventory.py now scans .ld files.

## Wave 15
See g2/docs/wave15-codecb-touch.md. codec-b fits the stock bound: -Os plus printf without float, ending 0x10016cd8 <= 0x1001708C. touch: SystemCoreClockUpdate rebuilt from stock; 36 B gap shown to be unused; .noinit discard made explicit. apollo display_lv/FPSCR work is not done.

## Wave 16
apollo-main in_fpscr 53->0; nvg 61->1, guess 16->15, unverified 3->2 (g2/docs/wave16-apollo-fpscr.md).

## Wave 17

## Ledger
- The stray root C-RECONSTRUCTION-PROGRESS.md (Waves 12-16) was merged into this file and deleted.

## display_lv_init_children.c
- Each of the 10 batch-3 sign tests has its own stock citation: 0x563106, 0x563188, 0x5632ec, 0x56336a, 0x563400, 0x563446, 0x5634e4, 0x56352e, 0x563588, 0x5635da. Pattern: vcmp #0; ite gt; vmov +/-1.0. Matched by order and sqrt-operand shape (flagged).
- The last NAN test was rewritten as `!(a >= b)` (stock 0x562ab2, it lt). The NAN macro was removed, and nvg_leftover went 1 -> 0.

## g2c_nema_vg_path.c
### draw_fill_51d2e0
- All FPSCR-carrier compares were rewritten as direct compares, each citing its branch condition (see the in-code comments).
- Decompiler bugs fixed:
  - NaN-only tests at 0x51dafa and 0x51df2e.
  - 8 zero-pair sites: the stock code copies the value, not the address.
  - sp+0 out0 slot (fStack_2d0).
- The uVar4 0xfffffff masks were removed. uVar14 is now only a stencil handle.

### vector_shape_draw_5202ec
- Fixed out-of-bounds UB: 3 scalar residuals were indexed `i*8`.
- Stock frame: push 9 regs, sub sp,#4, vpush d8-d15, sub sp,#104 (0x5202ec-0x5202f8). That puts sp at entry-0xd0.
- The 3 residuals and afStack_c4 (sp+0xc) now share one `uint g2c_sp_frame_5202ec[26]`.

### draw_box_shadow_540036
- Fixed a real semantic bug: stock 0x540938-0x540948 memcpy's 3 bytes from dsc+0x20 into [sp] and passes [sp] as color_resolve arg0. The decompiled C passed uVar5 (the old [sp] value) and discarded the memcpy.

### path_cmd_5156b8
- The two CONCAT31 GUESS sites were replaced with byte stores to sp+4: stock 0x515b22 and 0x516588 `strb.w sl,[sp,#4]`, read back as bytes at 0x515b8a and 0x5165ee. The old `(float)CONCAT31` was a value conversion, not a byte merge.

## Not done (still flagged; no evidence recovered)
- apollo guess (8):
  - file headers in g2c_ble_leaves, am_hal_clkmgr_g2, g2c_vectors, g2c_nema_leaves, g2c_ghidra_shim.h, gpu_patch.h
  - the vg_path file header (about 240 FPSCR/carrier sites remain outside draw_fill)
  - .ld MRAM/SSRAM size
- stub 1 (notify_app_icon), unverified 2 (vg_path header), inferred 11.
- .ld raw_decompile 1: this is the provenance line "Ghidra 12.1.4" in the memory-map note, a scanner false positive. Left as is.
- em9305 .ld FLAG/UNVERIFIED (RAMHI 0x80fe20..0x810000 unused by stock): the stock em9305 binary was not at hand this wave. Next check: grep it for 0x80fe20-0x810000 literals and the initial SP (the stack may sit there).
- codec-a .ld FLAG/GUESS (stage1/2 and generic .text ownership): not resolved.

## Builds (0 undefined each)
| Target | Output | Notes |
|---|---|---|
| apollo-main | g2/build/g2c-w17-final-apollo-main | from g2c-w17b-apollo-main; text 3,481,241 / data 168,651 / bss 1,999,768 |
| apollo-bootloader | g2/build/g2c-w17-final-apollo-bootloader | identical to w15 |
| em9305 | g2/build/g2c-w17-final-em9305 | |
| codec-a | g2/build/g2c-w17-final-codec-a | |
| codec-b | g2/build/g2c-w17-final-codec-b | |
| touch | g2/build/g2c-w17-final-touch | |

Inventory: g2/docs/inventory-w17.json

## Wave 18
See g2/docs/wave18-markers.md and g2/docs/inventory-w18.json. All 6 targets were relinked into g2/build/g2c-w18-final-* with 0 undefined. apollo-main text 3,480,737 (W17 3,481,241), data 168,651, bss 1,999,768. vg_path NAN( tokens 215 -> 158. em9305 pins added (FLAG/UNVERIFIED kept). codec-a stage2/res.text ownership cited. Inventory marker counts are unchanged from W17.

## Wave 19
- em9305 relinked against the current .ld (0 undefined).
- g2c_nema_vg_path.c: NAN( 158 -> 0 and g2c_fpscr_* 43 -> 0, all with per-site stock vcmp citations. The carrier macro and helpers are removed. The file compiles rc=0 with 54 uninitialized warnings (unchanged).
- stroke_path/fill_path: the 4 order-matched citations are now address-verified.
- em9305 myapp pin addresses were found as limm operands in stock (0xca2e/0xcb0e). Sizes are still UNVERIFIED.
- Compose g2c-w19-apollo-main: 2869/2869 compiled. Finals are in g2/build/g2c-w19-final-*, all 6 with 0 undefined.
- apollo-main text dropped 3,480,737 -> 3,479,921 (-816). The other 5 sizes are unchanged.
- Inventory (inventory-w19.json): identical to W18 except em9305 unverified 1 -> 2 (new honest sizes marker). Details in wave19-markers.md.

## Wave 20
- Scanner: explicit, documented rules in .waves/inventory.py (wave20-markers.md): a Ghidra word inside a stock-address citation or a tool-version line is not raw; an explicit negation of "inferred" is not counted. The wave19 stroke/fill comments are restored to their "Ghidra label" wording.
- apollo-main: guess 8->4, unverified 2->0, raw 1->0, inferred 11->5, stub 1, weak 3. .ld guess/raw/inferred 1/1/1 -> 0/0/0.
  - Evidence: vg_path header, nema ctx size, gpu_patch prototypes, MRAM/SSRAM upstream match, DIS serial attribute, app_db offsets.
- em9305: myapp AO 36 B / queue 16 B verified from the ARC objdump corpus (unverified 2->1); "not plain ARC" corrected.
- codec-a: 11 libgcc routines and crc32_no_comp verified in stock image_a_xip; DSP has no image_a body (GUESS kept).
- Builds g2c-w20-apollo-main (2869/2869) and g2/build/g2c-w20-final-*: all 6 targets 0 undefined, sizes identical to W19 (comment-only source changes).
- inventory-w20.json written. The unresolved list with reasons is in wave20-markers.md.

## Wave 21

- Vectors: the 10 spin-alias slots are bound to stock-verified bodies (8 existing, 2 new: 0x4b80be GPIO0_607F, 0x4d58a6 IRQ82). The vectors GUESS is removed, and the readback of the linked table is checked.
- Clock manager: full stock RAM map of g_sClkMgr* state (pools 0x4c43dc..0x4c46a0). clock_release_all is reimplemented from stock 0x4c45a4. This fixes a real no-op: the upstream copy walked an empty private bitmap. The GUESS is narrowed to the upstream-only private_clkgen helpers.
- g2c_ghidra_shim.h had no includers and is removed (backup in .waves/w21-bak).
- em9305: the 16 gp loads (43 gp operands) are rodata mis-decoded at 0x334122..0x334ca4, gp is never written, and no code touches 0x80fe20..0x80fe28. The UNVERIFIED is narrowed to possible ROM use.
- inventory.py: new CORPUS citation rule (documented in the script).
- Builds: g2c-w21-apollo-main (2869/2869), and g2c-w21-final-* for all 6 targets, each with 0 undefined. apollo-main text is 3,479,921 -> 3,480,017; the other targets are unchanged.
- apollo-main inventory: guess 4->2, raw 0, stub 1, weak 3, inferred 5. Other targets unchanged. Details are in wave21-markers.md and inventory-w21.json.

## Wave 22
- Correction: wave 21 claimed "stock has no private_clkgen helpers". That was wrong. Stock am_hal_clkgen_control 0x4d3628 calls 0x4c45fc/0x4c465c/0x4c4668/0x4c46b4; Ghidra corpus just has no function entries there. am_hal_clkmgr_g2.c now carries stock-derived release_all and the hfadj/hf2adj helpers, and the upstream include is dropped. The clkmgr GUESS is removed.
- ble +0xc3 GUESS is resolved: it is the link-role byte (AppDbNewRecord 0x47a71c, Master/Slave log).
- aging_test LVGL callees are string-anchored to lvgl 9.3. The dmic/i2s providers are verified against decomp. Citations were added for em9305 controller_init and touch FLAG.
- inventory.py: CORPUS extended, NEG2 added (both documented inline).
- inventory-w22 versus w21:
  - apollo-main: guess 2→0, stub 1, weak 3, inferred 5→2.
  - codec-a: guess 1, flag 1.
  - codec-b: raw 1→0, inferred 2→0.
  - touch: flag 1.
  - em9305: unverified 1, flag 1, inferred 1→0.
- Links: all 6 have 0 undefined. apollo-main is 3,476,849/168,627/1,999,612.
- Remaining items: wave22-markers.md.

## Wave 23
- Scope: em9305 inline asm -> C (the largest remaining share, 29.5% of FUNC bytes). The unmatched apollo-main runs were triaged first and are mostly not unported code:
  - 0x5d2fee..0x5d8908 (22.8 KB, 114 runs) is FreeType 2.9.1 psaux cf2_* (upstream-map.tsv, followups.md line 16). It is covered by an upstream unit and only unmatched because IAR inlines it.
  - `_bleSlaveProcMsg` 0x46e098 already has source in ble-slave/display_ble_slave_proc_msg.c (the coverage tool misses it by name).
  - The remaining first-party unmatched runs (113 runs, 50,540 B) need per-function string/xref matching and are queued for wave 24.
- em9305: 59 lowered-asm units in qpc-scheduler/initializer_lowers are now C (symbol names unchanged, so the remaining asm units still link to them):
  - 29 leaf/tail-call wrappers and 30 more (enter_s/push_s call chains, small predicates, record writers).
  - Evidence for each unit: the C was compiled with the g2-em9305-1 profile (arc-elf32-gcc 15.2, -mcpu=arcem -mcode-density -Os) and its disassembly was diffed against the stock-lowered asm unit with `.waves/em-conv.sh`.
  - 4 units are byte-identical. The other 55 differ only by delay-slot scheduling (ARC `b.d`/`j_s.d` slots, which gcc does not fill), a redundant `extb_s`/`exth_s` after a volatile byte/halfword load, absolute-address `ld`/`st` forms, and strength reduction of `a % 625` (child_31340c). Each diff was read by hand. Each unit's header says so.
  - Delay-slot pitfall handled: a `bl.d` slot runs before the call, so `mov_s r13,r0` in the slot captures the original r0 (the arguments are `a`, not the callee's result).
  - Each unit carries its stock address range. No guess markers were added.
- Metrics (em9305):
  - asm-defined FUNC bytes: 61,860 -> 61,138 (29.5% -> 29.2%).
  - unit files still containing `__asm__`: 464 -> 411 by the file scan (the scan was taken after the first conversion, which is why it is -53 rather than -59).
  - text: 216,984 -> 217,032 (+48, mostly gcc `extb_s` and `nop_s` padding).
  - The compose is 621/621 with the same 6 libgcc/memcpy externals as wave 22, and the final link has 0 undefined (`g2/build/g2c-w23-final-em9305`, -Os kept).
- Other targets: no source changes this wave, so their wave-22 links stand (apollo-main 3,476,849 / 168,627 / 1,999,612).
- Paired sim vs stock: not re-run. This wave changed only em9305 ARC sources, which the Renode paired sim does not execute (it models the EM9305 as a peripheral). The apollo-main image is unchanged, so the earlier GPUJIM=1 results stand.
- inventory-w23.json: em9305 unverified 1 / flag 1 (unchanged). apollo-main now shows guess 5: these are the honest GUESS flags added by the sim-fix RAM-cell work after wave 22 (stock_ram_cells.c x3, display_ring_descriptor_data_20002c48.c, g2-apollo-main.ld ucHeap base). They are flagged, not new decompilation guesses.
- `make sources-check` reports one existing gap unrelated to this wave: g2/src/apollo-bootloader/link/resident_rom_thumb_set.S is not in sources.json.
- Tooling: `.waves/arc.sh` runs any arc-elf32-* tool in the container, `.waves/emdump.sh` prints a compact disassembly of a lowered unit, and `.waves/em-conv.sh` compiles a candidate, diffs it against the stock lowering, and replaces the unit only on an identical match (or with FORCE=1 for the same size).
- Next: the larger em9305 units (1-2 KB each, e.g. associated_callback_329888, dispatch_child_31d6a4, radio_cb_31dfd0) and the first-party unmatched apollo runs (0x5bdfbc, 0x5bd3a0, 0x504d2c, 0x5a2d24).

## Wave 24
- Scope: the "113 first-party unmatched apollo runs (50.5 KB)" first, then large em9305 asm units, then coverage-tool honesty and `resident_rom_thumb_set.S`.
- Apollo triage: the 113 runs were mostly not first-party. `.waves/sim-fix/coverage3.py` now reads the four reference maps plus the new `ranges-w24.tsv` and classifies every TSV row (see apollo-coverage-map.md, "Wave 24 re-measurement"). Result: 8,445 strong (matched 6,890, upstream 1,238, lvgl 184, data 10, blocked 19, range-upstream 104), 376 weak attributions (family / sandwich / callee / name-ref / stock-anchor / addr-ref), 23 residual functions (1,746 B). The strong total is the number to quote; the weak ones are flagged as attributions.
- `ranges-w24.tsv` rows are decompile-checked (ftglyph.c, ftstroke.c, ftbitmap.c, am_hal_uart/i2s/syspll statics). The npmx static range 0x55ea40..0x55fab0 is weaker evidence (all callers are npmx_*) and is labelled so.
- No apollo source was changed, so no apollo rebuild or paired sim was required. The apollo-main image is unchanged, and earlier GPUJIM=1 results stand.
- `resident_rom_thumb_set.S` is first-party (three `.thumb_set` ABS symbols that give the resident-ROM entries a Thumb FUNC type), but it is a link helper assembled by `.waves/link-final.sh` with `g2-apollo-bootloader.ld`. Adding it as a compose unit would double-define the symbols, so `sources.json` has a new top-level `not_built` map (read by `tools/build/sources.py`) that records it with that reason. `./g2/make.sh sources-check` passes again (5,064 units, 1 not built). `sources.json` is kept at the repo's 1-space JSON indent.
- em9305: 7 more lowered-asm units are C (init_native_child_30e910, 315d68, 316384, 319978, 31a900, 328814, init_native_enc_action_315dd8). Method as in wave 23: arc-gcc 15.2 -Os profile, `.waves/em-conv.sh` (same-size, diff read by hand). 319978 returns `a+826`, the incidental r0 from the stock code. Not ported because gcc's output has a different size and would shift later addresses: init_native_child_325c9c, 32cb2c, 32d598, init_native_dispatch_child_32543c. A further 14 small units (gen4: 31636c, 325cb4, 31c9f4, 315d50, 325648, 315c18, 31a920, 31a3ec, 3268e8, 3268cc, 326a48, 325284, dispatch_callback_31ca0c, pawr_queue_resume_31694c) were tried and all came out a different size (gcc does not use the IAR-style delay slots and absolute-address forms), so they stay asm. The large units (associated_callback_329888, 592 instructions) are not ported by hand, because the Renode sim does not execute the EM9305 and nothing could verify them.
- Metrics (em9305): asm-defined FUNC bytes 61,138 -> 60,984 of 209,394 (29.2% -> 29.1%). Compose 621/621, 6 libgcc/memcpy externals as before, final link `g2/build/g2c-w24-final-em9305` has 0 undefined, -Os kept.
- Other targets: no source changes, so their links stand.
- inventory-w24.json: unchanged versus w23 (em9305 unverified 1 / flag 1; apollo-main guess 5, stub 1, weak 3, inferred 2). No markers added or removed.
- Next: the 23 residual functions, then the em9305 units that need a hand-written ARC asm -> C pass (dispatch_child_31d6a4, radio_cb_31dfd0, associated_callback_329888), which are best done together with an ARC emulator check.

## Wave 25
- ARC execution check (new): QEMU arc-2026.03 harness that runs the stock lowered unit and the C candidate on random inputs with mocked externs and compares r0, call log, memory, callee-saved registers and sp. See `g2/docs/em9305-arc-harness.md`. A negative-control mutant is caught. Caveats: random inputs (not exhaustive), stub side effects and MMIO not modelled, arity taken from the candidate's extern prototypes.
- em9305: all 14 gen4 units are now C (31636c, 325cb4, 31c9f4, 315d50, 325648, 315c18, 31a920, 31a3ec, 3268e8, 3268cc, 326a48, 325284, dispatch_callback_31ca0c, pawr_queue_resume_31694c). Each is QEMU-equivalent on 500 tests; several are a different size (24-36 B vs 24-28 B), accepted because their references are symbolic. Metrics: asm-defined FUNC bytes 60,984 -> 60,632 of 209,430 (29.1% -> 29.0%). Compose 622/622 (new `qp_module_names.c`), same 6 external refs, final link `g2/build/g2c-w25-final-em9305` has 0 undefined, -Os kept, image 217,096 B.
- Absolute addresses: base vs +0x100 shifted-link audit in `g2/docs/em9305-abs-address-audit.md`. Fixed the 4 QP assert module-name strings (symbolic now). Remaining stock-address tables / function pointers / HCI handler addresses are listed there as NOT fixed. The image was already not stock-layout, so those literals are already wrong in our build.
- Big units (dispatch_child_31d6a4 ~885 asm lines, associated_callback_329888 ~1,190 lines, radio_cb_31dfd0) are now checkable with the harness but NOT converted this wave.
- Apollo: no source changes, so no apollo rebuild or paired sim was run (apollo-main image unchanged; earlier GPUJIM=1 results stand). Coverage: residual 23 -> 17 functions (1,746 -> 1,150 B) via six cited rows appended to `upstream-map.tsv` (elog_set_text_color_enabled, elog_output_lock, elog_set_filter_tag_lvl_default, elog_get_filter_tag_lvl, lv_label_revert_dots, poll_rtc_clksrc_edge_and_wait). New `verified-w25.tsv` (decompile-vs-source side-by-side, evidence per row): pcm22 sequences 13 (0x5A326C) and 11 (0x5A2EEA). strong 8,445 -> 8,453, weak 376 -> 374.
- Weak firm-up: a literal-set cross-check of the 84 stock-anchor weak functions was inconclusive (Ghidra shows literal-pool values as DAT_*, and the source factors them through helpers), so nothing was promoted on that basis. 374 weak remain; the rest need per-function side-by-side review like `verified-w25.tsv`.
- inventory-w25.json equals w24 except files_scanned (+1).
- Unresolved residual (17 fns, 1,150 B): 0x4416b8, 0x47e812, 0x47e93c, 0x48086a, 0x480ed8, 0x483030, 0x492114, 0x492198, 0x492200, 0x4bfdf4, 0x4c387e, 0x4c4058, 0x4d3dda, 0x4d94e6, 0x529ae4, 0x529d40, 0x53456c.
- Next: convert dispatch_child_31d6a4 / associated_callback_329888 / radio_cb_31dfd0 with the harness; turn the remaining hard-coded tables into symbols; continue side-by-side verification of the weak list (31 PCM2.x functions first).

## Wave 26
- Priority 1 (em9305 hard-coded stock addresses) done. See `g2/docs/em9305-abs-address-audit.md`. Found that the stock image begins with a 66-word interrupt vector table that our image lacked (stock 0x30ed96 sets `int_vector_base` to 0x302400), and about 160 stock functions that were reachable only by raw address (HCI vendor handlers, ISRs, vendor-NVM closure, lctr decode, PML/RF helpers). New units, all in `sources.json` (origin g2c-wave26): `application/stock_residual_code.c` (lowered stock asm, 5,673 instructions), `application/stock_residual_data.c` (vector table, radio tables, lctr pointer table, INI tail), `qpc-scheduler/stock_data_tables.c`. Regenerated `em9305_hci_cmd_tables.c` (symbolic handlers; first table now 34 records, count still 12: flagged). Linker script: vector table first and asserted at the NVM base, `opencfw_em9305_image_end` symbol.
- Metrics: compose 625/625, 0 duplicate strong symbols, final link `g2/build/g2c-w26b-final-em9305` 0 undefined, -Os kept, image 217,096 -> 237,884 B (the added bytes are code that was missing before, not growth of existing units). Shift-link audit clean (6 legitimate masks/flash-base/vector-pin literals, 2 coincidental u16 pairs). `.waves/abs/audit.py` now automates the audit.
- Caveats: the lowered code is asm, not C, so the asm share of the image goes up (asmshare script still reports 29.0% because it scores the stock function set); QEP/QF real functions still unported; two over-wide regions duplicate 1.5 KB of ported code; flags listed in the audit doc. inventory-w26.json: em9305 flag markers 1 -> 5 (new honest FLAG notes only).
- Priorities 2 (convert big units with the harness) and 3 (weak-list verification, PCM2.x first) were NOT started this wave. No apollo changes, so no apollo rebuild or paired sim.


## Wave 27 (checkpoint 1: upstream QP/C identified and ported to wrapper units; NOT yet integrated into the image)
- Priority 1 (QEP/QF = upstream QP/C): the stock 0x310d18..0x3117d8 is **QP/C 6.5.1** (GPL-3.0-or-later). Basis is code structure, not a version string: QMsm-era `QHsm` vtable `{QHsm_init_, QHsm_dispatch_}` at stock 0x33450c, `QActiveVtable {init, dispatch, start_, post_, postLIFO_}` at 0x3344e8, `QEP_reservedEvt_ = {0,1,2,3}` at 0x3344fc, `Q_REQUIRE_ID` ids 200/210/220 (init_), 400/410/510/520 (dispatch_), 410 (QK_sched_), `QPSet` as a 16-bit set with `QK_attr_` fields at stock offsets (readySet at +6, intNest at +4), and the six module-name strings (`qf_act`, `qep_hsm`, ...). Upstream pulled as submodule `third-party/upstream/qpc` at 416dcec8 (v6.5.1); no upstream file is modified.
- New port + wrappers (untracked until `sources.json` registration): `g2/src/em9305/qpc-port/{qep_port,qf_port,qk_port,qp_unit}.h` and seven `*_unit.c` that `#include` the unmodified upstream .c (QF_MAX_ACTIVE 16, QF_MAX_EPOOL 2, `clri/sync` critical section, `uint_fast8_t`=u8, `uint_fast16_t`=u32, `log2p1` ext insn, `Q_onAssert` -> `opencfw_em9305_assert`, SRAM globals pinned to stock addresses by section name). All seven compile clean with `-Os -Werror` (ARC profile). `qp_module_names.c` gained `qf_act` (0x334528) and `qep_hsm` (0x334530).
- Verification with the QEMU harness (random inputs, call-log + memory + callee-saved comparison, stock lowered unit vs upstream-compiled function): EQUIVALENT on 300-400 tests for `QActive_get_`, `QActive_post_`, `QActive_postLIFO_`, `QActive_ctor`, `QF_add_`, `QF_gc`, `QF_newX_`, `QF_poolInit`, `QMPool_get`, `QMPool_init`, `QMPool_put`, `QK_sched_`, `QHsm_ctor` (aligned `me`), `QHsm_top`. `QF_add_`, `QF_gc`, `postLIFO_` needed `--nor0` (void functions). Harness artifacts explained: stub module-name pointers (fixed by renaming to the shared symbol), QK_attr_/QF_active_ pins (linker PROVIDE), vendor `log2p1` unsupported by QEMU (harness-only soft-log2 via `OPENCFW_QEMU_SOFT_LOG2`, a bit-length substitution that is an assumption about the instruction).
- Found deviations: stock `QF_bzero` is `memset` when len != 0 (not the upstream loop), so upstream `QF_bzero` must stay excluded; stock `QF_init` differs from upstream (no `QF_timeEvtHead_` bzero; `QF_subscrList_` 0x801390, `QF_maxPubSignal_` 0x801364) so the hand-written `QF_init` stays. Stock `QHsm_ctor` sets `vptr` (the old stub ctor did not).
- Not yet verified: `QHsm_init_`, `QHsm_dispatch_`, `QActive_start_`, `QK_activate_` (need function-pointer mocks). Harness now has `--handlers/--mockobj/--mockact` (mock state handlers + mock vtable, assert aborts the test via longjmp); `QHsm_init_` matched the first 24 tests exactly, then the candidate hangs on test 25 (orig aborts on 2nd assert). Cause unknown (possibly the candidate loops where the stock aborts via assert); open.
- Not done this checkpoint: linker pins/discards in `g2-em9305.ld`, `sources.json` registration, removing `em9305_qpc_ctor.c` stub vtables, dead duplicate regions (priority 2), residual asm -> C (3), weak list (4). The built image and all six targets are unchanged by this wave so far (no source in the build touched except the two new module-name strings); apollo unchanged, no paired sim needed.
- Tooling edits (untracked `.waves/`): `qrun.py` (`--clamp`, `--chunks`, `--mockobj/--mockact/--handlers`, per-build stub files, pin PROVIDE symbols), `qemu-arc/h/driver.c`, `w27/{cc.sh,q.sh,mkorig.py}`.

### Wave 27 (step log, 2026-10-27 ~10:35 PM America/Chicago)
- QHsm_init_ EQUIVALENT on 300 QEMU tests (`--mockobj`). The earlier "hang" was the harness stub `Q_onAssert` returning (real one never returns); the stub now aborts the test at the first assert.
- QHsm_dispatch_ EQUIVALENT on 300 tests (`--mockobj --mockeq --nor0`; 6.5.1 dispatch_ is `void`). `mockeq` makes `temp == state` (required by assert 400); a counting mock `mhtop` replaces `QHsm_top` in the mock objects so state-machine walks terminate.
- QActive_start_ and QK_activate_ EQUIVALENT on 300 tests each, run against a combined stock unit (start + activate + QK_sched_ lowered together, so both sides run real callees): `--mockobj --mockact --noevt --args7`; 27k / 32k stub calls, 228 / 286 outcome classes.
- Harness additions: `--mockeq`, `--noevt`, `--args7` (r4..r6 args; `--clamp 4=,5=,6=`), QK_attr_ initialised (intNest=0) under `--mockact`, all `QF_active_[]` entries valid mock objects, dispatch-mock call cap, weak `QHsm_top` in the stub files.
- All QP/C 6.5.1 functions the stock image uses are now verified EQUIVALENT except QF_init / QF_run / QF_bzero (kept hand-written: documented stock deviations).
- QEQueue_init (`qf_qeq_unit.c`, upstream `qf_qeq.c`) EQUIVALENT on 300 tests; replaces `qpc-queue/qequeue_init.c`.
- **Integration done (10:45 PM America/Chicago):** 8 wrapper units registered in `sources.json` (origin `g2c-wave27`, flags `-I` qpc-port/include/src/qf/qk, `-ffunction-sections -fdata-sections -mno-sdata`; -Os profile unchanged). Removed the hand-written replacements `activate.c`, `event_gc.c`, `queue_pool.c`, `scheduler.c`, `log2p1_port.c`, `qpc-queue/qequeue_init.c`, the stub-vtable `application/em9305_qpc_ctor.c`, and the hand-written `QF_newX_` / `QMPool_get` / `QMPool_init` bodies in `controller_init.c`. Callers now use the upstream names (`QF_newX_`, `QMPool_get`, `QMPool_init`, `QK_activate_`, `QK_sched_`); `framework_init.c`/`framework_run.c`/`idle.c` keep stock bodies and are renamed `QF_init`/`QF_bzero`/`QF_run`/`QK_onIdle` (upstream QF_init / QF_run / QF_bzero are renamed `*_upstream_unused` in the wrappers and discarded). Link scripts (`g2-em9305.ld`, `.waves/abs/base.ld`, `shift.ld`): `/DISCARD/` for upstream functions the stock image does not link (QTicker, QF_remove_, QF_stop, QK_schedLock/Unlock, QHsm_isIn, QEQueue_post/get, ...) and pins for `QF_active_` 0x80131c, `QF_maxPool_` 0x801360, `QF_pool_` 0x801368, `QK_attr_` 0x801394.
- Build `g2/build/g2c-w27-em9305`: 626/626 compiled, 0 duplicate strong symbols; composed object lists 7 more unresolved names than before (`QF_onCleanup`, `QF_onStartup`, `QF_tickX_`, `QF_timeEvtHead_`, `QF_maxPubSignal_`, `QF_subscrList_`, `..._qf_qeq`), all referenced only from discarded sections; final link 0 undefined, image 239,152 B (was 237,884; the vtable stubs were replaced by real QActive_start_/post_/dispatch_/init_ code). Shift-link audit unchanged (6 insn masks, 2 data coincidences). `tools/build/sources.py check` ok (5069 units).
- Priority 1 complete (QP/C integrated, built, linked, audited, docs updated). inventory-w27: em9305 guess/stub/weak 0, flag 5, unverified 1 (unchanged). Starting priority 2 (dead duplicate lowered regions).
- P2 step: removed dead duplicates from stock_residual_code.c: 0x302664..0x3026a8 (ported as dispatch_child_302664), 0x3027c8..0x302844 (ported child_3027c8/3027f4/stack_check_302820), whole 0x329574..0x329842 (ported callback_329574 + child_329610). KEPT 0x3026a8..0x3027c8 and 0x302844..0x30299c: referenced by lowered callers (undefined L302760 when removing everything). Residual object text 17,536 -> 16,628 B. Rebuilding.
- Priority 2 complete: build g2/build/g2c-w27b-em9305 626/626 compiled, 0 duplicate strong symbols; final link g2c-w27b-final-em9305 0 undefined, -Os kept; image 239,152 -> 238,244 B (-908); shift audit unchanged (6 insn, 2 data, 0 undef refs). Apollo/other targets untouched, no paired sim. Next: priority 3 (residual asm -> C, harness) and 4 (weak list).
- P3 step 1 (wave 28): lctrSlvBigBeginOp 0x3288b0 (450 B asm) -> C (g2/src/em9305/lctr/lctrSlvBigBeginOp.c), QEMU EQUIVALENT 400 tests, 3 mutants caught; compiled 508 B (-Os). New harness bits: qrun --pre FILE (per-test RAM setup hook) and --outb name:argidx (stub writes a byte through an out-pointer, arg excluded from hash); tool .waves/w28/conv.py (rename/convert+register). Callees lctrBigTxCtrlQueuePeek/lctrSlvBisSetupTxData/lctrSlvBisTxData renamed from stock_<addr>. Not yet rebuilt.
- P3 step 1b (wave 28) BUG FOUND+FIXED in the lowering: `.waves/lower.py` silently dropped every DSP instruction whose mnemonic objdump prints on a continuation line after a "Warning: disassembly may be wrong" (ARCv2 DSP mpywhl/mpywhul, 233 occurrences in stock2.dis). 10 were missing in `stock_residual_code.c` (blank `"\n"` asm lines; incl. the kept 0x3026a8 64-bit divide helper and lctrSlvBisTxControl/TxData), so those lowered units were NOT byte-equivalent to stock. All 10 restored from stock2.dis (mpywhl/mpywhul), lower.py fixed (continuation-line mnemonic), the older initializer_lowers/ files were already correct. lctrSlvBigBeginOp's `{lo,hi}` pair was wrong too: hi = mpywhl(w+0x24, byte+0x18) + hi(mpydu), not ptr+hi; C fixed (FLAG: mpywhl = 32x16 multiply, product bits [47:16], per the ARCv2 DSP definition; QEMU arcem has no DSP so qrun now substitutes a base-ISA sequence on the orig side, `dspsub`, and rewrites short conditional branches to long forms for range). Harness: driver.c `pre_cb` (logs the pair the callback sees) now makes the pair observable; the old wrong C fails (8/60), fixed C EQUIVALENT 60.
- P3 step 1c (wave 28): lctrSlvBisSetupTxData 0x329230 (196 B) -> C (g2/src/em9305/lctr/lctrSlvBisSetupTxData.c, 224 B), QEMU EQUIVALENT 100, mutants 0x20->0x10 and >=0 -> >0 caught. Renamed callees lctrBisFlushStaleSdus (0x317534), lctrBisTxQueuePeek (0x317890). Residual text now 16,024 B. Not yet rebuilt.
- P3 step 1d (wave 28): lctrSlvBisTxControl 0x3293e0 (130 B -> 176 B C) and lctrSlvBisTxData 0x329464 (152 B -> 252 B C; macdu/ACC 64-bit callback arg, mpywhl hi word) converted (lctr/lctrSlvBisTxControl.c, lctrSlvBisTxData.c), QEMU EQUIVALENT 150 tests each with the callback path observed (pre_cb2); mutants caught: acc col2->col, kind +2->+3, mode mask 0x1c->0x18, mpywhl >>16 -> >>15. BbBleBisTxData 0x302fa8 renamed in the residual. Residual text 15,740 B.
- P3 step 1e (wave 28): lctrSlvBisTxCompletionInterleaved 0x3292f4 (116 B -> 156 B C) and lctrSlvBisTxCompletionSequential 0x329368 (118 B -> 172 B C) converted (lctr/lctrSlvBisTxCompletion*.c), QEMU EQUIVALENT 120 tests each, 7 mutants caught (+0xb0 / 0x198 / +0xc|+0x30 field offsets, >= vs >, cursor byte). The whole 0x3288b0..0x3294fc BIS slave family (7 functions) is now C. Residual text 15,504 B (was 17,536 at wave-28 start; 16,628 after priority 2).
- Build g2c-w28a-em9305 (630/630 compiled, includes the lower.py mpywhl fix + setuptx/txctl/txdata/BigBeginOp; comp pair installed after it): link/audit 6 insn hits, 2 data hits, 0 undefined refs; final link g2c-w28a-final-em9305 0 undefined, image 238,540 B (+296 B vs w27b: the 10 restored instructions and the C unit sizes).
- P3 step 2 (wave 28): QF_maxPubSignal_ (0x801364, enum_t) and QF_subscrList_ (0x801390, QSubscrList *) defined as pinned data (qpc-port/qp_unit.h externs, definitions in qpc-scheduler/framework_init.c, pins `.bss.stock_801364/801390` added to g2-em9305.ld, .waves/abs/base.ld, shift.ld; QP global size ASSERT extended). QF_init now uses the symbols (QF_subscrList_, QF_maxPool_, QF_maxPubSignal_, QF_active_, QK_attr_.actPrio/.lockPrio = QF_MAX_ACTIVE) instead of literal addresses; same stores as stock (checked in objdump). framework_init.c's sources.json entry gained the QP include flags. Remaining literal QK_attr_ users: framework_run.c (0x801396 lockPrio), startup_hook.c / controller_init.c (0x801398 intNest at QK_attr_+4... see next wave).
- P3 step 1f (wave 28): three more residual BIS helpers converted to C and verified in the QEMU-ARC harness (all EQUIVALENT: qpeek 100, flush 300, qpk 500 tests): lctr/lctrBigTxCtrlQueuePeek.c (0x3172ec, 24 B), lctrBisFlushStaleSdus.c (0x317534; note stock's `ld.as r0,[r0,76]` sits in the delay slot of the auxiliary_elapsed call, so arg0 = cfg->+0x130, not cfg), lctrBisTxQueuePeek.c (0x317890, 238 B; two wsf_event_at scan loops, mpyw/mpyuw/min semantics replicated). Removed from stock_residual_code.c; registered in sources.json (g2c-wave28). Build g2c-w28b pending.
- P3 step 3 (wave 28): weak-list verification, PCM2.2 transition sequences in audio/transition-snapshot/producers.c (the only PCM2.x file with weak rows; transition.c/completion.c do not exist). 12 more verified side-by-side (new g2/docs/reference/coverage-2.2.6.10/verified-w27.tsv; coverage3.py reads it): sequences 3, 8, 9, 10, 12, 14, 15, 16, 17, 19, 20, 21. Method: .waves/decompr.sh (Ghidra decompile + resolved literal-pool values; new G2DecompR.java / .waves/words.sh) and every pool address checked against the source literals (0x200742d4..e8 publish block, 0x2005665c table, 0x4002004c/44/48/80/37c, 0x400083e0/40008064 wait). No source diffs found. Weak 374 -> 362 fns (52,054 B). Still unverified: sequences 0,1,2,4,5,6,7,18,22,23 (+24..26 empty stubs) and the helper functions; pcm22_sequence_10 is a known dedupe of 8.
- Build g2c-w28b-em9305 (BigBeginOp/SetupTx/TxControl/TxData + Completion pair + 3 queue helpers + pinned QF_subscrList_/QF_maxPubSignal_): 635/635 compiled, 0 duplicate strong symbols; abs audit 6/2/0 undef 0; final link g2c-w28b-final-em9305.bin 238,680 B; nm confirms QF_maxPubSignal_=0x801364, QF_subscrList_=0x801390. sources.py check: 1 not built (unchanged, presumed resident_rom_thumb_set.S).
- P3 step 1g (wave 28): lctrDecodeCtrlPduCasePduChannelMapInd (0x319268, 48 B) converted to C (lctr/lctrDecodeCtrlPduCasePduChannelMapInd.c) and verified EQUIVALENT in the QEMU-ARC harness (300 tests, 140 distinct outcome classes). Removed from stock_residual_code.c (stock_residual_data.c reference renamed, still symbolic); registered in sources.json. Skipped lctrDecodeCtrlPduCasePduConnUpdateInd (0x31936c): it uses `mpywhul` whose exact semantics are unproven (the Bluetooth supervision-timeout rule `(latency+1)*interval < timeout*4` suggests a plain 32x16 product, but the campaign model is the DSP [47:16] reading), so it stays lowered asm until the mpywh* semantics are settled (same FLAG as BigBeginOp). Build pending.
- P3 step 1h (wave 28): lctrDecodeCtrlPduCasePduCisTermInd (0x319310, 40 B) converted to C (lctr/lctrDecodeCtrlPduCasePduCisTermInd.c), harness EQUIVALENT (300 tests; memory hash covers the three byte copies), removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1i (wave 28): lctrDecodeCtrlPduCasePduPwrCtrlReq (0x3195cc, 38 B) converted to C (lctr/lctrDecodeCtrlPduCasePduPwrCtrlReq.c), harness EQUIVALENT (300 tests), removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1j (wave 28): lctrDecodeCtrlPduCasePduPwrCtrlRsp (0x3195f4, 42 B) converted to C (lctr/lctrDecodeCtrlPduCasePduPwrCtrlRsp.c), harness EQUIVALENT (300 tests), removed from stock_residual_code.c, registered in sources.json. Build pending.
- Build g2c-w28c-em9305 (+4 lctrDecodeCtrlPdu cases: ChannelMapInd, CisTermInd, PwrCtrlReq, PwrCtrlRsp): 639/639 compiled, 0 duplicate strong symbols; abs audit 6/2/0 undef 0; final link g2c-w28c-final-em9305.bin 238,688 B (+8 vs w28b); sources.py check still '1 not built'. Residual lowered asm extents now 14,714 B (14,882 B before this step).
- P3 CORRECTION (wave 28): the harness model of ARCv2-DSP `mpywhl`/`mpywhul` was WRONG (earlier rows for lctrSlvBigBeginOp, lctrSlvBisTxControl, lctrSlvBisTxData assumed product bits [47:16], i.e. `(x*(int16)y)>>16`). Public docs (ARCv2 DSP ISA, binutils arc-opc/arc-dis, GCC arc builtins, nSIM, QEMU-arc) give only "32x16 integer multiply" and do not pin the result slice; the slice is settled from firmware usage instead: `mpywhl r0,r0,72/656/912/784/1250/1000/625/0xb08` and `mpywhl d,0x01010101,byte` are plain scale/µs/replicate multiplies (only the LOW 32 bits make sense), the BigBeginOp/TxControl/TxData `{+0x24:+0x20} * byte(+0x18)` is a 64-bit multiply (mpydu for lo/hi of the low word + mpywhl(+0x24,byte) added to hi), and ConnUpdateInd's `(latency+1)*interval < timeout*4` is the Core-spec supervision rule. So `mpywhl d,x,y` = low32(int32 x * int16 y[15:0]); `mpywhul` = low32(uint32 x * uint16 y[15:0]). Confidence high, unproven on silicon. Fixed: .waves/qrun.py dspsub (now emits sext/zext16 + mpy), the three C files (`hi = W32(big+0x24)*b + (prod>>32)`, FLAG lines removed). The old harness runs had passed only because the model and the C shared the wrong shift; re-run with the corrected model: BigBeginOp 100/100, TxControl 100/100, TxData 100/100 EQUIVALENT, and a negative control (old >>16 C) now MISMATCHes 35/100 in TxControl, so the harness discriminates. This changes the C (and image) of those three functions; build pending.
- P3 step 1k (wave 28): lctrDecodeCtrlPduCasePduConnUpdateInd (0x31936c, 106 B) converted to C (lctr/lctrDecodeCtrlPduCasePduConnUpdateInd.c) with the corrected mpywhul model; harness EQUIVALENT (800 tests, targeted pre-hook for the latency-500 edge and product==timeout*4 equality; mutants `lat*iv`, `>` vs `>=`, `lat<499/501`, `timeout<<3` and `window>` are all caught). Removed from stock_residual_code.c (residual extent sum now 14,608 B), registered in sources.json. Build pending.
- P3 step 1l (wave 28): lctrGetBigRefTime (0x31afd4, 38 B) converted to C (lctr/lctrGetBigRefTime.c): BIG table entry lookup (base 0x805c3c, 0x200-byte entries, handle-7), state byte==1 returns the +0x130 word and stores +0x134 through the optional out pointer. Harness EQUIVALENT (300 tests, 102 outcome classes; a handle-offset mutant is caught). Removed from stock_residual_code.c (extent sum 14,570 B), registered in sources.json. Build pending. lhciVsExtDecodeCmdPkt (0x332b70) skipped: it calls a ROM address (0x101e48) the harness cannot mock.
- P3 step 1m (wave 28): three more decode cases converted to C in lctr/ and harness-verified EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduCteReq (0x3193d8; feature bit 2, type 2, splits src[1] into pdu+0xc/+0xd), lctrDecodeCtrlPduCasePduCteRsp (0x319400; feature bit 1 only), lctrDecodeCtrlPduCasePduMinUsedChainInd (0x319450; the first harness run caught a wrong `bmsk_s r2,r2,2` reading: ARC `bmsk` masks bits [u:0], so it is &7 not &3; fixed, a `>219` mutant is caught; it validates a PHY mask and a count in 2..37, so the stock name is probably a typo for MinUsedChannelsInd, FLAG: name kept, semantics guessed from the range). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1n (wave 28): five more decode cases converted to C in lctr/ and harness-verified EQUIVALENT (300 tests each; shared pre-hook `.waves/w28/mk.sh` generates orig/pre/run for the "flag bit + packet type + child validator" shape): lctrDecodeCtrlPduCasePduCisInd (0x319298; word 0x805a94 bit 29, type 0x10, child packet_child_32dbe4), CisReq (0x3192c0; bit 29, type 0x24, child 32dc40), CisRsp (0x3192e8; len==1 rejected, bit 28, type 9, child 32dd20), ConnParamReq (0x319338; byte 0x805a94 bit 1, type 0x18, child 32de08), ConnParamRsp (0x31935c; len==1 rejected else tail-calls ConnParamReq; 110 outcome classes). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1o (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduPeriodicSyncInd (0x3194f4; byte 0x805a97 bit 1, type 0x23, child 32dffc), PeriodicSyncWrInd (0x319518; same, type 0x2b, child 32e068), and the two copies in the stock block "unnamed 0x31948c" which are two identical functions at 0x31948c/0x3194ac (feature byte 0x805a97 bit 2, type 2, copy src[1] to pdu+0xc). The opcode dispatch table lctr_decode_actions_334d0c is indexed by the LL control opcode (BT Core Vol 6 Part B 2.4.2): slots 0x1d/0x1e are CLOCK_ACCURACY_REQ/RSP, so the two are named lctrDecodeCtrlPduCasePduClockAccuracyReq/Rsp (FLAG: names from the opcode position, not from stock symbols). Same table position also confirms 0x19 = MIN_USED_CHANNELS_IND for MinUsedChainInd (FLAG removed). Residual extent sum now 14,158 B. Build pending.
- P3 step 1p (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduPhyReq (0x31953c; byte 0x805a95 &9, type 3, child 32e114), PhyRsp (0x319564; len==1 rejected else tail-calls PhyReq), PhyUpdateInd (0x319574; len==0 rejected, &9, type 5, child 32e128), PwrChangeInd (0x3195a0; byte 0x805a98 bit 2, copies src[1..4], type 5). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1q (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlCasePduRejectInd (0x3191ac; stores 0xff/err code, type 2), lctrDecodeCtrlCasePduVersionInd (0x3191c4; child 32e1f4, type 6), lctrDecodeCtrlPduCasePduChReportingInd (0x319208; len!=0, byte 0x805a98 bit 7, copies src[1..3], type 4), lctrDecodeCtrlPduCasePduChStatusInd (0x319234; its `lp` hardware loop is a 10-byte copy src[1..10]->pdu+0xc; QEMU does execute the loop, a 9-byte mutant is caught, so `lp` code IS harness-testable when the loop has no MMIO). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1r (wave 28): the rest of the small LL control PDU decode cases converted to C in lctr/, each harness-EQUIVALENT (300 tests): lctrDecodeCtrlPduCasePduPerFeatureReq (0x3194cc; len==1 rejected, byte 0x805a94 bit 3, child 32dfe8, type 9), RejectExtInd (0x319620; bit 2, copies src[1..2], type 3), and from stock blocks the image calls 'unnamed'/shares: FeatureReq (0x319414; len==0 rejected, then the FeatureRsp body), FeatureRsp (0x319420; child 32dfe8, type 9), LengthReqRsp (0x319438, referenced by both the LENGTH_REQ and LENGTH_RSP slots; child 32deac, type 9), TerminateInd (0x3196ec) and UnknownRsp (0x319700) (copy src[1], type 2), and lctrDecodeCtrlPduCaseDefault (0x319204, always 0x19, 8 table refs). FLAG: the six unnamed ones are named from their slot in the stock opcode dispatch table 0x334d0c vs BT Core Vol 6 Part B 2.4.2 opcode numbers (consistent with every named neighbour), not from stock symbols. Removed from stock_residual_code.c (extent sum 13,706 B; was 17,536 B at the start of wave 28), registered in sources.json. Only SubrateInd/SubrateReq (0x319644/0x319698, 82/84 B) remain of the decode cases. Build pending.
- P3 step 1s (wave 28): lctrDecodeCtrlPduCasePduSubrateInd (0x319644, len==0 rejected) and SubrateReq (0x319698, len==1 rejected) converted to C in lctr/ (byte 0x805a98 bit 5; five little-endian halfwords src[1..10] -> pdu+0xc..0x15; type 0xb), harness EQUIVALENT (300 tests each; the first SubrateReq run hung because my lowering extent cut off the function epilogue, fixed to 0x319698-0x3196ec). All 0x3191xx-0x3196xx LL control PDU decode cases are now C. Residual extent sum 13,540 B. Build pending.
- Build g2c-w28d-em9305 (steps 1k-1s: corrected-mpywh BigBeginOp/TxControl/TxData, ConnUpdateInd, GetBigRefTime and 30 more LL control PDU decode cases): 671/671 compiled, 0 duplicate strong symbols; abs shift-link audit 6/2/0 undef 0 (unchanged); final link g2c-w28d-final-em9305.bin 238,692 B (w28c 238,688 B); sources.py check still '1 not built'. Residual lowered asm extent sum 13,540 B (14,714 B before this round, 17,536 B at the start of wave 28).
- P3 step 2a (wave 28): ROM-call mocking needs no new harness feature: a ROM call goes through a named facade `opencfw_em9305_rom_<name>_<hex>` (em9305_link_closure.c, absolute IROM address inside), and `--rename 0x101e48=<facade>` on the stock side turns the lowered `jl 0x101e48` into an ordinary stub call that both sides log. lhciVsExtDecodeCmdPkt (0x332b70, 36 B, the boot-installed callback) converted this way (lctr/lhciVsExtDecodeCmdPkt.c + new facade opencfw_em9305_rom_lhci_vs_ext_101e48 with args (opcode halfword, len byte, arg, 0xff, 256-byte stack scratch)); harness EQUIVALENT (200 tests; a 0xff->0xfe mutant is caught). What the ROM routine does is unknown (ROM not in the repo). Removed from stock_residual_code.c; controller_init.c prototype updated. Build pending.
- P3 step 2b (wave 28): the unnamed 202-B block at 0x302a1c was two things: a 4-byte `b 0x30299c` veneer (the word after AOAD_Init in ini_record_335820) and a verbatim stock duplicate of 0x302a20 that controller_init.c already carries as C (`opencfw_em9305_controller_initialize_stack`). Harness (new `--deref name:NWORDS[:idx=mask]` option hashes the words a stub's pointer argument points at, so struct contents built on the stack are compared) shows the C EQUIVALENT to stock on 100 tests, and a changed `capabilities` constant is caught. Residual block removed (-198 B asm); veneer is now C (application/AOAD_Init_veneer.c, EQUIVALENT, 50 tests) and the data word renamed to opencfw_em9305_AOAD_Init_veneer_302a1c. Note: wsf_os_register_start_304610 in em9305_link_closure.c is still an empty stub, so initialize_stack has no caller (pre-existing).
- P3 step 2c (wave 28): the EM9305 SDK `em_system` vendor-command handlers (EMSG_*/EMSMM_*/EMSRC_*, 0x304bb4..0x3058c0, ~4 KB, all of the shape handler(op, plen, params, ctx, resp): write the status at resp[3], then reply through ROM 0x102588(op, resp length, ctx, resp, after-callback)) are being converted as a family with the harness. New in the tooling: `fam.sh` (one-line harness per handler, ROM calls mocked through facades via --rename/--arity), `--mmio` (maps and hashes the 0xf00000..0xf05000 MMIO window as RAM so register read-modify-write order is compared), 5th-argument hashing for 5-arg stubs (4-arg hashing silently dropped the callback argument), `mut.sh` (mutant check), `inst_em.py` (installer) and `chkref.py` (every opencfw_em9305_stock_X reference has a definition). Batch 1 installed, 21 functions (EMSG_CallWeakFunction + callback + weak default hook, three reset commands + callbacks, GetEmCoreInformation, SetBootModeFlags + callback, SetPublicAddress, SetRssiOffset, SetSleepOptions, SetUartBaudRate + callback, SvldMeasurement, NVMEraseFull, NVMEraseMain, status-1 reply), each EQUIVALENT on 100 tests with at least one mutant caught for the data-dependent ones. Three new ROM facades in em9305_link_closure.c (0x102588 reply, 0x1020e8 delay, 0x104b98 uart baud: the last two names are inferred from use). Nameless handlers are `emsys_*_<addr>` because the command id/name is not recoverable from the sources. Global labels added for 0x30ef04/0x30ef0c (NVM erase wrappers, `b nvm_op` with op 8 / 4) so the C can call them.
- step 2c cont.: e22-e25 (EMSMM_NVMErasePage/ReadAtAddress/WriteAtAddress/WriteContinue) installed; callees 0x3059d8/0x305a20/0x30ef14 given global labels in the residual. WriteAtAddress/WriteContinue only reply when op == 0xfd03/0xfd04 on success (the original compares the op against a long immediate).
- step 2c cont.: e26-e29 (four identical 'status 1 if NVM magic valid else 0x2f' handlers, opcodes 0xfd81..0xfd84, mutant caught) and e30-e32 (EMSRC_EmCoreReceiver154TestEnd/ReceiverTest/ReceiverTestEnd, opcodes 0xfccf/0xfcc5/0xfcc6) installed, all EQUIVALENT on 100 tests with mutants caught. New harness option `--outp name:argidx:nbytes[:argidx:nbytes]` (qrun.py + driver.c stub_outp): hashes an out-parameter buffer on the stack or in the RB window before the call, then fills it with PRNG bytes, so the C is checked on how it uses the callee's out values without depending on stack layout. Found: 0x30592c..0x305940 (6 stubs) are weak default hooks returning 0xc (the EMSRC test functions call them); em_system_command_gap 0x30592c is 6 stubs + a region classifier (0x305944) + memory read (0x3059d8) + write (0x305a20), a later conversion target. The HCI opcode for each handler is in em9305_hci_cmd_tables.c.
- P3 step 2d (wave 28 checkpoint, Oct 28 2026 ~2:30 AM CT): rebuilt after the em_system handler batches (build w28f): 705/705 units compile, 0 duplicate strong symbols, shift-link audit 6 insn / 2 data-word hits (unchanged, expected), undef 0, final link OK, image 238,436 B (was 238,692). First build failed only on -Werror=unused-parameter in six handlers (fixed with (void) casts). Installed this wave: 32 em_system handlers (e1-e32), 3 new ROM facades, 5 new global labels in the residual (0x30ef04, 0x30ef0c, 0x3059d8, 0x305a20, 0x305930). Not yet paired-sim'd: em9305 only, apollo unchanged, so no sim required.
- step 2e (wave 28): em_system_command_gap 0x30592c (392 B) converted: 6 weak default hooks that return 0xc (0x30592c/30/34/38/3c/40; callers: EMSRC receiver/adv-pattern/scan/transmitter test commands), emsmm_region_id_305944 (memory-map classifier), emsmm_read_memory_3059d8 and emsmm_write_memory_305a20 (word-copy ROM facades 0x100ca8/0x100d20 added; 0x30f014 flash-write helper stays asm). 9 functions EQUIVALENT on 100 tests. New harness option --stubret name:v1:v2:... makes a stub return from a fixed list; it was needed to reach the flash-write branch (the random stub returns 2/3 too rarely, so the first mutants survived). With it the region-base, region-accept and return-code mutants of the write helper are all caught (the list must contain duplicated 1/2 entries; the distribution of the hash index is uneven). mut2.sh passes extra opts to mutants.

### P3 step 2f (Oct 28 2026, ~3:40 AM America/Chicago): EMSRC e42-e45
- Converted EMSRC_EmCoreScan15_4 (0x3052dc, HCI 0xfcce), EMSRC_EmCoreStartAdvPattern (0x305328, 0xfcc9), EMSRC_EmCoreTransmitterTest (0x305358, 0xfcc1), EMSRC_EmCoreTransmitterTestEnd (0x3053b4, 0xfcc2) to C. Each is EQUIVALENT to the lowered stock on 100 QEMU-ARC tests; 24 mutants were killed (status codes, parameter indices, int8 sign, loop bound 0x63, reply length 3, delay 0x32, LE32 shifts, W32 source).
- Harness: stub arg names extended to 8 (`g`,`h`) for the 7-arg hook 0x30593c; `--outp` now hashes args 5/6 correctly (out index >= 4 was an IndexError).
- Survivors (2, by construction): in TransmitterTestEnd the loop's `[0x8019a1] == 0` arm (`>= 0x64` bound and the `[0x8019ac]` test) is unreachable while the flag byte is static, which the stubbed delay cannot change. Kept verbatim from the stock branch structure (flag is volatile and set by ISR code).
- 0x333b48 (the transmitter-test parameter check) got a global label in stock_residual_code.c; still residual asm.
- Note: TransmitterTestEnd replies with length 3 (status + LE16 count) but also zero-writes resp[6..7]; copied verbatim. The reply length counts from resp[3].
- Not yet rebuilt (build after the next batch).

### P3 step 2g (Oct 28 2026, ~4:00 AM America/Chicago): second EMSRC command table, e46-e52
- Converted to C, each EQUIVALENT to the lowered stock on 100 QEMU-ARC tests with all mutants killed (about 50 mutants): EMSRC_ReceiverTest (0x305448; opcodes 0xfcc5/0xfccc/0xfccd), emsrc_receiver_test_end_3054f0 (0xfcc6; name inferred), emsrc_status1_reply_305548 (0xfcc3), EMSRC_SetRfPower (0x30555c, 0xfcc4), EMSRC_TransmitterTest (0x3055ac; 0xfcc1/0xfcca/0xfccb), EMSRC_TransmitterTestEnd (0x3055f8; 0xfcc2), EMSRC_setAOADCteConfig (0x305658; 0xfcce).
- Harness: `--outp` size with bit 0x1000 set skips hashing the incoming bytes (for uninitialised stack out-structs); `--stubret` now also fills `--outp` buffers; `--stkw 5` for 20-byte config structs.
- Misread caught by the harness: SetRfPower stores the return of radio_mode_312290 (not the level byte) at resp[5].
- Interrupted mutant runs left `cand/e47.c` and `e49.c` mutated; restored from /tmp/mut_*.good and rerun (both killed).
- 0x302760 got a global label; chkref `bad 0`; residual extent sum now 10,142 B (was 11,502).
- Next: rebuild into a fresh dir, then EMSS_Le*.

### P3 step 2h (Oct 28 2026, ~3:50 AM America/Chicago): build w28g checkpoint
- Fresh build `g2/build/w28g`: 725/725 units, 0 duplicate strong symbols, audit insn hits 4 / data-word hits 2 (was 6 / 2; two absolute-address hits went away with the converted handlers), undef 0, final link OK (`w28g-final-em9305`).
- Image 238,404 B (w28f: 238,436 B; stock-extent residual sum 10,142 B, was 11,502 B). `sources.py check` result as in earlier waves.
- Remaining: EMSS_LeDecrypt/LeDecryptKC/LeEncrypt/LeEncryptKC/LeRand (0x3056ac..0x3058c0), remaining unnamed blocks, weak list, PCM2.2 Ghidra retry, harness doc.

### P3 step 3a (Oct 28 2026, ~4:40 AM America/Chicago): EMSS_Le* handlers e53-e57
- Converted EMSS_LeDecrypt (0x3056ac, HCI 0xfc8a), EMSS_LeDecryptKC (0x30573c, 0xfc8b), EMSS_LeEncrypt (0x3057b8, 0xfc88), EMSS_LeEncryptKC (0x305844, 0xfc89), EMSS_LeRand (0x3058c0, 0xfc87). All EQUIVALENT on 100 QEMU-ARC tests; about 45 mutants killed (byte reversal indices, flag, lengths, status codes, config constants, plen boundary).
- New facades in em9305_link_closure.c: rom_le_cipher_1060c4 (6 args), rom_le_cipher_kc_10093c (4 args), names inferred from the callers. rom_random_10a7f8 now has the 3-argument signature its callers already use (was declared with 1 argument; same tail-call code).
- Harness: new `--derefb name:argidx:nbytes:hexmask[:...]` hashes selected bytes of an in-parameter buffer (skips uninitialised stack padding); combines with `--outp` and `--stubret`. `stub_derefb` in driver.c.
- FLAG: LeRand's stack config struct is largely uninitialised in stock; C zeroes byte 3 of word 0 and leaves the rest untouched.
- Not rebuilt yet.

### P3 step 4a (Wed Oct 28 2026, before the w28h build): tiny unnamed/named blocks to C
- Converted 20 tiny functions (`.waves/w28/inst_small.py`, compiled -Os instructions compared with the lowered stock code; no harness run for these): noop 0x302d80, 0x30f6d8, 0x30fab0, 0x30fabc, 0x313778, 0x3137f4, 0x3137f8; PML_ClearConfigurationModeFlag (0x30f1f8), PML_ClearModeFlag (0x30f208), PML_SetConfigurationModeFlag (0x30f710; name INFERRED from the Clear sibling, same bit 23 of 0xf00430) plus its byte-identical copy 0x30f720; PML_VoltMonitorReStoreConfig (0x30fa9c); 0x30f6c8 timer/mode update, 0x30f6dc (restore then 0x30f6c8), 0x30f934 (two empty calls), dispatch_child_30fab4 (tail to common_activate_310580); 0x311f84 (u16 store at 0x805fdc), 0x3122f0 (RSSI offset byte at 0x80fd5e), 0x3335c8 (2 when transport idle is 0 else 1). Names marked inferred in each header.
- The residual copy of 0x30fab8 (`b common_activate_310580`) was dropped: the same address is already defined in C by dispatch_child_30fab8, so this also removes a duplicate.
- chkref: bad 0. Not yet rebuilt (next fresh dir w28h).

### P3 step 5 (before the w28h build): harness doc
- g2/docs/em9305-arc-harness.md: added the em_system handler workflow, ROM-mocking recipe, new options (--derefb, --outp no-hash bit, --stubret+--outp, 8-arg stubs) and the pitfalls.

### P3 step 6 (before the w28h build completed): PCM2.2 Ghidra retry + weak list
- The Ghidra headless retry worked this time (`.waves/decompr.sh`, one or two addresses per call, run in the background). Sequence addresses come from the dispatch table at 0x200002a8 (init image offset 680).
- Verified side-by-side against the source (pool values resolved, writes and order compared): sequences 0, 1, 2, 4, 6, 7, 18, 22, 23 (9 rows appended to g2/docs/reference/coverage-2.2.6.10/verified-w27.tsv). coverage3.py: weak 362 -> 356 fns, 52,054 -> 50,074 B; residual unchanged (17 fns, 1,150 B).
- **FINDING (not fixed, not added to the TSV): pcm22_sequence_5 (stock 0x5A26BE) differs from audio/transition-snapshot/producers.c.** Stock has the same early exit as sequence 0: if (0x400083e0 & 1) and next == [0x200002a4], it runs ton_adjust(ton,next), sets 0x40020044 field = nc, calls the timer stop (FUN_004802ce = pcm22_timer_stop) and sets byte 0x20004540 = 0x1a, then returns before publishing. The source has no such branch. The rest of the body matches. Proposed fix: copy sequence 0's early block to the top of sequence 5 (needs next/old/ton, nc, `W(g2_stock_ram_20000290+0x14)`). It is an apollo-main source change, so it needs an apollo rebuild and paired sim; left for the user to approve. Sequence 0..4,6..23 otherwise verified or earlier verified; still unverified: 24..26 (empty stubs) and the helper functions.

### Build w28h checkpoint (Wed Oct 28 2026, ~4:21 AM America/Chicago; earlier "~" times in steps 4a-6 above were estimates, the clock is the box clock)
- g2/build/w28h (e53-e57 + the 20 small functions): 749/749 units compiled, 0 duplicate strong symbols, 0 undefined. Audit: insn hits 4, data-word hits 2 (unchanged), undef 0. Final link g2/build/w28h-final-em9305: 0 undefined, -Os kept, image 238,424 B (238,404 B at w28g, +20 B). Residual extent sum 9,324 B (10,142 B at w28g). sources.py check: 5,192 units, 4,871 source files, 1 not built (unchanged).
- Only em9305 changed: no apollo rebuild or paired sim needed.

### P3 step 7 (Wed Oct 28 2026, ~4:30 AM America/Chicago): pcm22_sequence_5 fixed to match stock
- Approved by the user. audio/transition-snapshot/producers.c: pcm22_sequence_5 now starts with the same early exit as pcm22_sequence_0 (same helpers and symbols: W(0x400083e0)&1 test, `g2ref_g2_stock_ram_20000290+0x14` compare with `next`, stock_ton_adjust, field(0x40020044,nc,0,7), pcm22_timer_stop, B(g2ref_g2_stock_ram_20004530+0x10)=26). Verified against the Ghidra decompile of 0x5A26BE (pool 0x200002a4 = 20000290+0x14, 0x20004540 = 20004530+0x10). Apollo rebuild `g2c-w28i-apollo-main` and a paired GPUJIM=1 sim follow.
- Apollo build `g2c-w28i-apollo-main`: 2870/2870 compiled, 0 duplicate strong symbols, 24 unresolved in the composed object (same as the prior apollo build), sim link ok (bin `simw28i.bin`, 3,862,175 B).
- Paired sim (GPUJIM=1 WIDE LISTPAGE PAIRED NOSILENT TOUCHONLY; hooks lst=common_list_container_inject_event, lcb=common_list_event_callback, resolved from each ELF/stock symbol suffix; one `single` tap + release, a GUESS at the earlier TOUCHX): runs nsw28i (ours) vs nsstk2 (stock2210). Hooks lst 1 / lcb 1 per arm on both. 22 notifs each. After masking the seq/CRC bytes (the first-payload byte that differs by a constant 0x1a, a counter offset) they are identical except idx 1 and 4 (heartbeat counters), the same as the earlier ns68/nsstk result. No regression. The touch scenario does not exercise the new sequence-5 branch (unverified; no PCM2.2 hook was run), so this only shows nothing else moved.
- verified-w27.tsv: added pcm22_sequence_5 (0x005A26BE). coverage3: weak 355 fns / 49,560 B, residual 15 runs / 1,150 B.

### P3 step 8 (Wed Oct 28 2026, ~4:45 AM America/Chicago): apollo unresolved-symbol check (w28i)
- Composed object `g2c-w28i-apollo-main`: 24 undefined symbols = 21 `U` + 3 weak (`g2_iar_fputc_weak`, `g2_iar_putchar_select_a/_b`, by design weak, resolve to 0). The 21 U are all linker-script symbols (`__bss_end/__bss_start/__data_end/__data_load_start/__data_start/__dtcm_bss_*/__start_kvdb_migration/__stop_kvdb_migration/_estack/_etext/_sstack/_stext`) or `nrf_fuel_gauge_*` from the vendor library; every one is defined in the final ELF.
- Final link (`g2c-w28i-final-apollo-main`): 0 `undefined reference` in link.log, `nm -u` on the ELF = 0.
- Versus the previous apollo build (`g2c-sim68-apollo-main`): that composed object had 26 (the same 24 plus `__stack_chk_fail` / `__stack_chk_guard`), so w28i is a strict subset, not an identical set; the two stack-protector symbols are no longer referenced. The `report.json` count of 24 for w28i is therefore correct, but "same as prior" was only true for the 24.

### P3 step 9 (time not recorded; between 4:49 and 4:53 AM America/Chicago): 0x30611c identified; ISR-wrapper family
- 0x30611c is the vector-table slot 23 handler (`opencfw_em9305_vector_table`, `stock_residual_data.c`): slot 21 = Cmp0 (0x306050), slot 22 = default (30f170), slot 23 = 0x30611c, slot 24 = Cmp3 (0x3061e4). Body: full context save, `st 4,[0xf00820]` (1<<2), sync, call 0x333404 with arg 2, restore, rtie (Cmp0 writes 1/arg 0, Cmp3 writes 8/arg 3). Header comment now `IRQHandler_ProtocolTimerOutCmp2`, FLAGGED as an inferred name (not in the stock symbol table); the symbol stays `opencfw_em9305_stock_30611c`.
- ISR family finding: 19 `rtie` blocks in stock_residual_code.c share a ~44-instruction compiler-style frame (st.aw r0,[sp,-88] ... saves r0-r12, r30, blink, r58/r59, lp_count, lp_start/lp_end, aux 1409/1411; `rtie`). Only the middle (MMIO ack plus indirect callback or call) differs. The ARC gcc `interrupt` attribute does not emit this frame (it saves only what it needs), so a C rewrite would not be byte-identical and would silently drop the context save. They stay residual asm; no conversion attempted. No size change (coverage3 residual runs 15 / 1,150 B unchanged: this metric counts the non-first-party runs, the em9305 asm is counted in the 9,324 B extent sum).
- 0x311c14 (210 B, channel-2 radio completion IRQ body, root record 0x8019d4 = the `radio_schedule_311ef0` record: +0 pending, +4 callback, +8 fallback callback, +0xc u16 base, +0xe u16 delta): written as C in `.waves/w28/cand/irq2.c`, NOT installed. Semantics read from the lowered code: status 0xf00860 bit0 -> ack 1 at 0xf00868, refresh(1), delta = base - byte(0xf0407c) + (field(lr 1686,>>8,13 bits) != 0x1fff ? ~field : 0) after `sr 4,[1666]`, store delta, exit unless bit 7 of 0xf04054, then call callback(0, delta) (callback = +4, else +8, clearing +0/+4); bit4 -> ack 16, restore(), same measure, callback(2, delta). The ARC gcc -Os build is 248 B vs stock 210 B (no `xbfu`, extra extb/exth, different branch layout), and I have not run it in the harness (needs aux-register and indirect-call mocking), so the stock block stays in stock_residual_code.c. Exact reproduction via rewriting is not achievable with this compiler; the next step would be a harness equivalence run (--mmio) for behaviour only.

### P3 step 10 (time not recorded; before 4:45 AM America/Chicago): PCM2.2 sequences 24-26
- Dispatch-table entries 24/25/26 = 0x5A40B0 / 0x5A40B2 / 0x5A40B4 (2 bytes apart). Ghidra decompile of each: empty `return;`. Matches the empty `pcm22_sequence_24/25/26` in producers.c. Three rows added to verified-w27.tsv (coverage3 weak count unchanged at 355 fns / 49,560 B; these were not in the weak count). Correction: 25 of 27 PCM2.2 sequences have TSV rows; sequences 11 (0x5a2eea) and 13 (0x5a326c) have none and are still to be verified. The static helpers (setup_profile, load_core, switch_low, doubled_boost, publish, finish_previous) were compared as part of each sequence's decompile but have no stock symbol of their own to cite, so no separate row.
- No em9305 code changed this step (comment-only edit at 0x30611c), so no em9305 rebuild; last built image remains w28h (238,424 B, residual extent sum 9,324 B).

### P3 step 11 (time not recorded; before 4:53 AM America/Chicago): shared ISR frame, 11 handler bodies in C (user request)
- New `g2/src/em9305/application/em_irq_frame.h`: the stock 88-byte frame (save r0-r12/r30/blink/r58/r59/lp_count, aux lp_start/lp_end/1411/1409; restore; rtie) as one asm template (`EM_IRQ_SAVE`/`EM_IRQ_RESTORE`) plus `EM_IRQ_HANDLER(SYM, BODY)` = save, `bl BODY`, restore. The save/restore were checked byte-for-byte equal across the stock handlers by script (the 11 standard ones; RadioRx/RadioTx differ only in having the call in the `bl.d` delay slot). Bodies are C; the handlers are a few bytes larger than stock (a call instead of inline code).
- Converted with conv.py (blocks removed from stock_residual_code.c, symbols renamed in the vector table, registered in sources.json, origin g2c-wave28): `opencfw_em9305_IRQHandler_` ArcTimer0 (0x305b1c), ArcTimer1 (0x305be0), PmlClock (0x305d84), ProtocolTimerOutCmp7 (0x305f74, 4 vectors), ProtocolTimerOutCmp0 (0x306050), ProtocolTimerOutCmp2 (0x30611c, FLAG inferred name), ProtocolTimerOutCmp3 (0x3061e4), ProtocolTimerSync (0x3062ac), RcCalib (0x3064fc), SWI7 (0x30660c, 6 vectors), SleepTimerFullVal (0x3066e8). Bodies written from the lowered asm; NOT harness-run (they are MMIO/aux-register handlers) so they are transcriptions, flagged as such in each file header.
- An interrupted tool call left Cmp3 half done (block removed and renamed, file missing); fixed by installing the file and registering it by hand. conv.py was not re-run for it.
- Still residual: the 6 `enter_s`-frame ISRs (SWI0, SWI1, QK_noPreemption, GPIO, PmlSvld, SleepTimerOutCmp3) and RadioRx/RadioTx (their bodies are 0x311ab4 RF_HandleInterrupt_Rx and 0x311c14).

### P3 step 12 (~5:05 AM America/Chicago): 0x311c14 harness-equivalent
- Discovery: IRQHandler_RadioTx (0x306440) is the shared frame with `bl.d L311c14` in the prologue's last delay slot, so 0x311c14 is the Tx body and 0x311ab4 (RF_HandleInterrupt_Rx, 350 B, still asm) is the Rx body. Name for 0x311c14: `RF_HandleInterrupt_Tx`, FLAG inferred from its sibling.
- Harness `.waves/w28/run_txirq.sh` (--mmio --nor0; pre `pre_txirq.h` sets the 0x8019d4 record with callbacks = the harness `pre_cb2` logger or null, and a RAM word standing in for aux 1686): EQUIVALENT on 60 tests, 53 outcome classes, 45 stub calls. QEMU has no aux registers 1666/1686 (`helper_sr` assertion), so for the run both sides had `sr 4,[1666]` -> no-op and `lr r0,[1686]` -> `ld` of a RAM word (orig by text substitution, cand by macro in a copy `cand/txirq_h.c`); the installed source uses the real `__builtin_arc_sr/lr`. Limits: the aux register values are not modelled beyond one random word, and 45 stub calls in 60 tests is modest coverage.
- Mutants, all killed: field compare 0x1fff->0x1ffe, bit 7 -> bit 6 test, fire(2)->fire(3), ack 16->17, pending clear removed, shift 8->9, callback clear removed, status bit 0x10->0x20 (8 of 8).
- Install is waiting for the em9305 w28j build (running since 4:53 AM) to finish so the tree is not changed mid-build.

### P3 step 13 (Wed Oct 28 2026, ~5:10 AM America/Chicago): w28j build of the 11 C ISR wrappers
- `g2/build/w28j`: 760/760 compiled with -Werror, 0 duplicate strong symbols, 0 undefined refs after link; abs audit ran; final link OK.
- Image 238,548 B (was 238,424 B in w28h; +124 B for 11 handlers, the cost of the `bl BODY` indirection). The 11 bodies are still NOT harness-run (transcribed from lowered asm).

### P3 step 14 (Wed Oct 28 2026, ~5:11 AM America/Chicago): 0x311c14 installed in C; RadioTx/RadioRx wrapped
- 0x311c14 `opencfw_em9305_RF_HandleInterrupt_Tx` (harness-equivalent, 8/8 mutants killed; 240 B vs 210 B stock, no `xbfu`) installed as `RF_HandleInterrupt_Tx.c`; removed from `stock_residual_code.c`.
- `IRQHandler_RadioTx.c` (frame + `bl RF_HandleInterrupt_Tx`) and `IRQHandler_RadioRx.c` (frame + `bl opencfw_em9305_stock_311ab4`, the body is still stock asm) replace the stock blocks 0x306440/0x306384; vector table renamed; chkref `bad 0`. Both differ from stock only in where the last aux save sits relative to the call (stock uses the delay slot).
- Rebuild `g2/build/w28k` started 5:11 AM; result not yet checked.

### P3 step 15 (Wed Oct 28 2026, ~5:18 AM America/Chicago): PCM2.2 sequences 11 and 13 verified; enter_s ISR wrapper prepared
- Sequences 11 (0x005A2EEA) and 13 (0x005A326C): side-by-side Ghidra decompile vs `producers.c` matches on order, fields, masks, the 0.9f factor (0x3f666666, unsigned convert rounding toward zero) and clamps. Rows added to `verified-w27.tsv`. Limit: the literal-pool values of the switch-helper register pointers were not printed (same helpers as sequences 9/18). With this, all 27 PCM2.2 sequences have rows (fixes the 25-of-27 note in step 8's correction). `coverage3.py` still reports weak 355 fns / 49,560 B (these two were not counted in the weak set by that script), residual 15 runs / 1,150 B.
- Prepared (not yet installed, build w28k is running): `.waves/w28/cand/irq/em_irq_frame_e.h` (second frame macro, `enter_s [r13,blink]` / `[r13-r15,blink]`, same save order as stock) and bodies for GPIO 0x305ca4, SleepTimerOutCmp3 0x3067b8, PmlSvld 0x305e68. They compile with -Wall -Wextra -Werror and the disassembly matches the stock sequence structurally; NOT harness-run. FLAGS: aux 1034 unnamed; PmlSvld's controller_timer_changed argument taken from timer_apply's return (guess), and the bit-6 timer-context read kept as a volatile read.
- SWI0 0x30251c, SWI1 0x3025f8 and QK_noPreemption 0x3025d0 are the QK preemption glue (they build a fake frame and `rtie` into QK_activate_), not a frame around a body; they stay asm.

### P3 step 16 (Wed Oct 28 2026, ~5:27 AM America/Chicago): w28k build OK; enter_s ISR wrappers installed
- `g2/build/w28k` (RadioTx/RadioRx wrappers + `RF_HandleInterrupt_Tx` in C): 763/763 compiled with -Werror, 0 duplicate strong symbols, 0 undefined refs at final link; image 238,584 B (w28j 238,548 B; stock 210,888 B).
- Installed `em_irq_frame_e.h` plus `IRQHandler_GPIO.c`, `IRQHandler_SleepTimerOutCmp3.c`, `IRQHandler_PmlSvld.c` (blocks removed from `stock_residual_code.c`, vector table renamed, registered in `sources.json`, chkref `bad 0`). Bodies are NOT harness-run (flags in step 15 and file headers).
- Rebuild `g2/build/w28l` started 5:26 AM; result not yet checked.
- All 19 `rtie` ISRs now have their frame as one shared macro and the body in C, except SWI0/SWI1/QK_noPreemption (kernel preemption glue, stay asm) and RF_HandleInterrupt_Rx 0x311ab4, which is a C wrapper around a body that is still asm (350 B).

### P3 step 17 (Wed Oct 28 2026, ~5:40 AM America/Chicago): w28l build OK (checkpoint)
- `g2/build/w28l`: 766/766 compiled with -Werror, 0 duplicate strong symbols, abs audit run, final link 0 undefined; image 238,640 B (w28k 238,584 B, w28j 238,548 B, w28h 238,424 B, stock 210,888 B). +216 B total vs w28h for 16 C ISR wrappers and `RF_HandleInterrupt_Tx` (240 B vs 210 B stock).
- Not harness-verified: the 14 ISR bodies other than 0x311c14 (transcriptions of lowered asm; flags in file headers). Still asm: SWI0, SWI1, QK_noPreemption, RF_HandleInterrupt_Rx 0x311ab4 (350 B body). Next: 0x311ab4 harness lift, then 0x30ecf8, 0x30f014, 0x333a94/0x333b48.

### P3 step 18 (Wed Oct 28 2026, ~5:50 AM America/Chicago): harness for the transcribed ISR bodies
- Method: `.waves/w28/isrh.py` lowers each stock handler and removes its frame (88-byte frame or `enter_s` frame, replaced by `push_s blink` ... `pop_s blink; j_s [blink]`) so the stock middle runs as a plain function; the candidate is the installed `IRQHandler_<Name>.c` (its `_body`, aux 1034 replaced by a RAM word at 0x801ff8 on both sides). Driver: `isrrun.sh NAME STARTHEX 'arity'`, mutants: `isrmut.sh`; hooks `pre_isr_common.h` (every callback slot 0x801900..0x80192f is 0 or the logging callback) plus `pre_isr_<Name>.x`. MMIO 0xf00000.. randomised and hashed. Not covered: the frame itself (save/restore order was checked by script earlier), `rtie`, real aux semantics.
- ArcTimer0 (0x305b1c): EQUIVALENT on 60 tests (47 outcome classes); mutants: slot 0x801904->0x801908 killed (callhash mismatch in 27 tests), unconditional call killed (hangs on null call).

### P3 step 19 (Wed Oct 28 2026, ~6:10 AM America/Chicago): 13 more ISR bodies run in the harness; 2 real bugs found and fixed
- Baseline (60 tests each, outcome classes / stub calls): EQUIVALENT for ArcTimer1 (46/45), PmlClock (26/39), ProtocolTimerOutCmp0 (36/60), Cmp2 (36/60), Cmp3 (36/60), ProtocolTimerSync (26/102), RcCalib (55/18), SleepTimerFullVal (49/49), GPIO (43/110), SleepTimerOutCmp3 (50/105), PmlSvld (17/96); this also confirms the PmlSvld guess that controller_timer_changed receives timer_apply's return, because the stub return values depend on the argument.
- MISMATCH (callhash, 43 and 44 of 60 tests) for ProtocolTimerOutCmp7 and SWI7: the stock code leaves the vector index in r0 at the callback call, so the callback receives it. Fixed in the installed files: Cmp7 calls `cb((uint8_t)(cause-0x15))`, SWI7 `cb(cause-0x38)` (unmasked, as stock). Both then EQUIVALENT on 60 tests. The earlier transcription (`cb()` with no argument) would have changed behaviour if the callback reads its argument.
- Mutant runs in `/tmp/isr_mut.log` (N=30); results in the next step. The installed headers still say "not harness-run" and need updating once all mutants are in.

### P3 step 20 (Wed Oct 28 2026, time not recorded, before 6:25 AM America/Chicago): 0x311ab4 RF_HandleInterrupt_Rx lifted to C (candidate; installed in step 21)
- `.waves/w28/cand/RF_HandleInterrupt_Rx.c`: five paths on status 0xf00860 (bits 25, 22, 16, 21), record at 0x8019c4 (same layout as the Tx record at 0x8019d4), callback codes 3, 4/7/8/10, 9, 5; measure uses aux 1666/1689 (FLAG: unchecked; Tx uses 1686/`sr 4`). Header documents each path.
- Harness (`rxrun.sh`, orig = lowered 0x311ab4..0x311c12; aux lr/sr substituted on both sides as for Tx, plus `mov_s r0,0` before the two stock `bl common_radio_restore` calls since that function ignores its argument and the stock r0 there is leftover junk): EQUIVALENT on 60 tests (44 outcome classes, 86 stub calls). Mutants in `/tmp/rx_mut.log`.

### P3 step 21 (Wed Oct 28 2026, 6:26 AM America/Chicago): mutant results; RF_HandleInterrupt_Rx installed; headers updated; w28m build started
- ISR mutants (`/tmp/isr_mut.log`, 30 mutants over the 14 bodies, N=30): 26 killed at once (memhash, callhash or ncalls mismatch). Four came back EQUIVALENT, which showed weak hooks, not equal code: PmlClock `status & 6 -> 7` (needed a status word covering all 16 low-bit patterns), GPIO `0xfff -> 0xffff` (pending word had to be shifted so the lowest bit can be >= 12), SleepTimerOutCmp3 `0xf -> 0x7` (the lr 1034 stand-in word had to be forced to 0x1f + 0..7). Hooks fixed (`pre_isr_PmlClock.x`, `pre_isr_GPIO.x`, `pre_isr_SleepTimerOutCmp3.x`); baselines still EQUIVALENT on 60 tests and the three mutants now die (ncalls, memhash, memhash).
- One mutant stays unobservable: PmlSvld `flags & 64 -> flags & 32`. The guarded statement is a dead volatile read of 0x80fde0 (the stock `ld` result is not used), so no harness can see it. Kept in C as a read for fidelity. The header says so.
- Rx mutants (`/tmp/rx_mut.log`, 11 mutants): all killed. The `? 4u : 10u` swap needed N=200 (killed in 4 of 200 tests, since it needs status bit 16 with ctl bit 6 set and bits 4/5 clear).
- Installed `g2/src/em9305/application/RF_HandleInterrupt_Rx.c` through `conv.py` (0x311ab4 block removed from `stock_residual_code.c`, `IRQHandler_RadioRx.c` now calls the C body, `chkref.py` bad 0). FLAG: aux 1666/1689 meanings are unchecked (harness substitutes lr/sr on both sides).
- The 14 ISR headers now say "harness-checked" with the method and the limits (frame, `rtie` and real aux semantics are not covered); SWI7 notes the index argument.
- Build `g2/build/w28m` started in the background (log `/tmp/w28m.log`).

### P3 step 22 (Wed Oct 28 2026, 6:47 AM America/Chicago): w28m checkpoint
- `g2/build/w28m`: 767/767 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object (ok, same as the composed pass before aliases); `.waves/abs/link.sh` + `audit.py`: undef refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link `g2/build/w28m-final-em9305` links with 0 undefined, image 238,708 B (w28l 238,640 B, +68 B for the C Rx handler; stock 210,888 B).
- The em9305-only change needs no paired sim. Remaining stock asm in `stock_residual_code.c`: SWI0 0x30251c, QK_noPreemption 0x3025d0, SWI1 0x3025f8 (QK preemption glue, stays asm), and the gaps 0x30ecf8, 0x30f014, 0x333a94/0x333b48.

### P3 step 23 (Wed Oct 28 2026, 7:43 AM America/Chicago): the three gaps lifted and harness-checked (not yet installed)
- Interrupted at 7:37 AM: stray mutant runs killed, candidate files restored from the `.good` copies. The Mac load average was about 200, so docker runs hit the 90 s timeout at N>=200 (a timeout is not a result; rerun at lower N).
- 0x30ecf8 (three functions): F1 `.waves/w28/cand/nvmgap1.c` (EQUIVALENT, 60 tests, 5/5 mutants killed), F2 `nvmgap2.c` (100 tests, 98 outcome classes, 11/11 mutants killed; the `sleep_rom_start(3)` mutant needed N=200 because the path needs the warm-boot branch), F3 `nvmgap3.c` (60 tests, 5 of 6 killed; the `0xf0041e = 14` mutant is unobservable because the final restore overwrites it). Combined file `cand/application_boot.c`, ROM facades added to `em9305_link_closure.c` (names are address-only).
- 0x30f014 (NVM write, called by emsmm_write_memory_305a20): `cand/nvmw.c`, EQUIVALENT on 60 tests with args clamped (bank 0..3, index < 0x4000, count < 32) and hooks that put the range at the 0x2000/0x20000 limits, 128-word and 2K-word boundaries. 0x30f170 in the same block is the vector filler (88-byte frame + system reset): becomes `EM_IRQ_HANDLER(opencfw_em9305_stock_30f170, em9305_rom_system_reset_103f14)`; the restore half is unreachable in stock too.
- 0x333a94 / 0x333b48: `cand/sbi.c` (transmitter test command: EQUIVALENT 100 tests) and `cand/sbv.c` (parameter check, modes 0/1/2: EQUIVALENT 150 tests). Mutants running (boundary hooks added because ret-only functions hide off-by-one mutants at random inputs).
- FLAGS: stale ROM arguments (boot_status/ready, packet_limit(1) = leftover validator result); roles of ROM 0x103180, 0x104ce4, 0x1030f8, 0x103c00, 0x1032b4, 0x103370 unknown; mode word at 0xf02800 unknown; int_vector_base aux 0x25 written by F2; bytes 9..11 and 17..19 of the 0x333a94 command record are uninitialised in stock and stay so.
- NOTE: the first nvmw runs used `--nor0` by mistake (ignores the return value); removed. Baseline and mutants must be rerun with return values compared before installing.

### P3 step 24 (Wed Oct 28 2026, 8:41 AM America/Chicago): gap 0x333a94 / 0x333b48 installed as `transmitter_test_params.c`
- Stray mutant runs killed at 8:27 AM, candidate files verified against their `.good` copies. Only this one gap was installed in this session (the smallest, 342 B).
- `0x333b48` (`opencfw_em9305_stock_333b48`, parameter check for the transmitter-test commands, modes 0/1/2): EQUIVALENT on 150 qemu-arc tests with boundary hooks; 24 of 24 mutants killed (off-by-one on every limit, mode tests, power sign handling).
- `0x333a94` (`opencfw_em9305_stock_333a94`, called by EMSRC_TransmitterTest): EQUIVALENT on 60-100 tests; 14 of 20 mutants killed (the `power <= limit` boundary needed a hook that makes the power equal the limit). Not run for lack of time: `0x7f -> 0x7e`, `cmd[8]`, `cmd[2]`, `cmd[0]`, the `params[0]/params[1]` argument swap, and `return r -> return 1` in the 305ab4 path. FLAGS: packet_limit_3047fc is called with the leftover validator result, written as 1; bytes 9..11 and 17..19 of the 20-byte command record stay uninitialised as in stock.
- Installed through `conv.py` (0x333a94 block removed from `stock_residual_code.c`, `stock_` names kept, file registered in `g2/src/sources.json`). `chkref.py` now also accepts C definitions of `opencfw_em9305_stock_*` symbols (a lifted block keeps its stock name); `bad 0`. The arc compile of the new file is clean with -Wall -Wextra -Werror.
- Build `g2/build/w28n` started at 8:40 AM (log `/tmp/w28n.log`, 13-20 min). Audit and final link still to do.
- Ready but NOT installed: `cand/application_boot.c` (0x30ecf8, F1-F3 all harness-equivalent, compiles) and `cand/application_nvm_write.c` (0x30f014 + the 0x30f170 vector filler, harness-equivalent with return values compared, 11 of 11 sampled mutants killed, compiles). `em9305_rom_page_103370` facade added to `em9305_link_closure.c`.

### Step 25 (Wed Oct 28 2026, 9:19 AM CDT): remaining 0x333a94 mutants, 0x30ecf8 + 0x30f014 installed, build w28o

- The 6 remaining 0x333a94 (sbi) mutants are all killed (`0x7fu->0x7eu`, `cmd[8]=2u->3u`, `cmd[2]=params[1]->params[2]`, `cmd[0]=0u->1u`, argument swap `params[0],params[1],params[4]`, `return r -> return 1u`). With the earlier ones, sbv/sbi mutants are 100% killed.
- Installed `application_boot.c` (0x30ecf8 hook/boot + 0x30ed80 + 0x30ee78 and the 0x30ef04/0x30ef0c wrappers) and `application_nvm_write.c` (0x30f014 plus the 0x30f170 vector filler) via conv.py. The remaining asm in `stock_residual_code.c` (NVM_ErasePage) called the local label `L30ee78`; now `bl.d opencfw_em9305_stock_30ee78`. chkref `bad 0`.
- Build w28o (-Os, fresh dir): 770/770 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object (as before). Audit: undefined refs 0, 350 in-range words, insn hits 4, data-word hits 2. Final link (g2-em9305): 0 undefined, image 238,888 B (w28m 238,708 B; stock 210,888 B).
- FLAGS (guesses): roles of ROM 0x103180, 0x104ce4, 0x1030f8, 0x103c00, 0x1032b4, 0x103370 unknown (address-only facade names); mode word 0xf02800 unknown; stale-register ROM args (boot_status/ready ignored; packet_limit_3047fc(1)); F2 writes aux 0x25; 0xf0041e=14 transient unobservable; sbi cmd record bytes 9..11, 17..19 uninitialised; C 0x30f170 saves aux 1409 before the reset call (stock saves it in the delay slot).
- w28n (superseded) was killed and removed.

### Step 26 (Wed Oct 28 2026, 10:39 AM CDT): ProtTimer_StoreConfig 0x310c08 (226 B) + ProtTimer_RestoreConfig 0x310aa8 (96 B) lifted to C

- New `application/ProtTimer_Config.c` (both functions, void; the state record at 0x80fd20 is addressed by literal as in stock: saved-config pointer at +0xc, timer index byte at +0x14). Registered once in sources.json.
- Harness (QEMU-ARC, `--mmio --nor0`, `run_ptc.sh`, hook `pre_ptc.h` with fixed saved-block pointer, idx set {0..5,16,17,31,32,33,255}, wake-marker path forced in 2/3 of tests, 0xf0047a/c..f preset): baseline EQUIVALENT on 60 tests for both. 14 mutants (`t<3->t<4`, `1u->0u`, `&0xf->&0x7`, 512->513, 2->3, `1<<17->1<<16`, `!=3->!=2`, `&2->&4`, loop 14->13, second+1, `|240->|224`, `0xf00480->0xf00484`, `&31->&15`, cleared 0->1): all killed in Restore and/or Store. One unobservable: `&0xf->&0x7` in StoreConfig (the bit it sets in 0xf0047a is cleared again at the end of the same call), still killed in RestoreConfig. The spin on bit 0 of 0xf0180c is not covered (the hook keeps the bit clear).
- Install: conv.py (two blocks, duplicate sources.json entry removed); chkref `bad 0`.
- Build w28p (-Os, fresh): 771/771 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit undefined refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link g2-em9305 0 undefined, image 238,940 B (w28o 238,888 B; stock 210,888 B).
- FLAGS (guesses): register meanings at 0xf018xx/0xf0047x/0xf0383b and the saved-block words 17..19 are address-only names; the four `nop`s after the wake-marker write are kept (delay purpose unknown); the state record at 0x80fd20 is not allocated by the linker (stock does the same).
- ini (0x30ef44 + 0x333c24 + 0x31435c) was a candidate at this point; installed in step 27.

### Step 27 (Wed Oct 28 2026, 12:25 PM CDT): NVM_InitCopy 0x30ef44 (206 B) + validate 0x333c24 (32 B) + _initdatCopy 0x31435c (20 B) lifted to C

- New `application/NVM_InitCopy.c` (`opencfw_em9305_stock_30ef44(record, ram_flag, full, high_flag)`, `_333c24(record)`, `_31435c(data, size, destination, &out)`), registered once in sources.json. New ROM facade `em9305_rom_1030dc(void)` in `em9305_link_closure.c` (address-only).
- Harness (QEMU-ARC, `--handlers --args7 --mmio`, `run_ini.sh`, hook `pre_ini.h`: 'INI' record with versions {0..5, random}, bad-signature cases, 1..5 entries from address pools, plus a boundary mode on odd tests with edge addresses around 0x801000, 0x80e978, 0x1ff000, 0x200000 and the ROM limit, `full`/`ram_flag` varied, `high_flag` forced 0): baseline EQUIVALENT on 64 tests (text 260 B orig and cand). The first orig hang was my own harness error (the orig extraction had dropped the last two instructions of the 0x31435c block).
- Mutants killed: skip window edges (0x801000->0x801004, 0x80e978->0x80e97c, 0x1ff000->0x1ff004, 0x200000->0x1ffffc), ram_flag and high_flag inverted, version <3->4 and >=4->5, entry start +4->+8 and +8->+12, advance size>=1->2 and (size+3)&~3 -> (size+2)&~3, memset size +1, signature 'N' check, full!=0 -> ==0, `addr==0` terminator (hang), `<0x801000 -> <0x800ffc`, limit +4, limit +2, `>=limit -> >limit`.
- Unobservable (flag): `*out = size+1` in `_31435c` (out word lives on the stack, which is not hashed).
- Install: conv.py (three blocks, duplicate sources.json entries removed); chkref `bad 0`; the three C/asm files compile with -Wall -Wextra -Werror.
- Build w28q (-Os, fresh): 772/772 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit undefined refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link g2-em9305 0 undefined, image 238,944 B (w28p 238,940 B; stock 210,888 B).
- FLAGS (guesses): ROM 0x1030dc role unknown (named by address only; stock passes a stale r0 = version byte, no arguments modelled; the only caller passes full == 1 so that path is unreached); the weak `opencfw_em9305_image_end` test mirrors stock, reason unknown; the copy-callback signature (data, size, destination, &out) is inferred; the 0x1ff000..0x200000 branch only tested with high_flag == 0.

### Step 28 (Wed Oct 28 2026, 1:45 PM CDT): PML_Init 0x30f4b0 (184 B) lifted to C

- New `application/PML_Init.c` (`opencfw_em9305_stock_30f4b0(void)`, returns the ROM init result), registered once in sources.json. Standalone and harness-verified against the lowered stock asm; the earlier `opencfw_em9305_controller_init` candidate in `qpc-scheduler/controller_init.c` is a separate copy of the same logic and was left untouched. The stock table in `stock_residual_data.c` still references the symbol `opencfw_em9305_stock_30f4b0`, now the C function.
- Harness (QEMU-ARC, `--handlers --mmio`, `run_pml.sh`, hook `pre_pml.h`: config pointer 0x80fb8c into a random-filled RAM block, mode/flag bytes zero or non-zero, factor set {0,1,2,3,100,0x7fff,0x8000,0xffff,random}, small/random sum words, 0xf00404 random/all-ones/zero): baseline EQUIVALENT on 40 tests (text 212 B orig, 208 B C, 163 stub calls). 30 mutants (sum - instead of +, operand swap, `(int16_t)` factor, every store offset/value, flag/mode byte sources, mode test, +36 values, configure_mode arg, `xbfu` position 4, +37 destination, prepare_timer condition and its source byte, last ROM arg byte, timer_reset/finish_init args 0): 29 killed. The one equivalent mutant, `(uint8_t)(field & 1u)` for the xbfu result, confirms that `xbfu r0,r0,3` yields a single bit (bit 3 of 0xf00404).
- Install: conv.py (one block); chkref `bad 0`; PML_Init.c and stock_residual_code.c compile with -Wall -Wextra -Werror.
- Build w28r (-Os, fresh): 773/773 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,968 B (w28q 238,944 B; stock 210,888 B).
- FLAGS (guesses): `xbfu` kept as inline asm; the mpywhul product is the low 32 bits (settled model); 0xf00404, the parameter record at 0x80fb80 and the power-management record at 0x80fb8c are named by address only (no field names); the stale-register arguments to `timer_reset`/`finish_init` are modelled as the previous return values.

### Step 29 (Wed Oct 28 2026, 3:27 PM CDT): RF_InitHw 0x311d2c (138 B) + RF_TestModeStart 0x312430 (138 B) lifted to C

- New `application/RF_InitHw.c` (`void opencfw_em9305_stock_311d2c(uint32_t incoming)`) and `application/RF_TestModeStart.c` (`uint32_t opencfw_em9305_stock_312430(uint32_t mode)`), each registered once in sources.json. RF_Init (still asm) tail-branches to the first by symbol; `stock_residual_data.c` references it by symbol.
- RF_InitHw: waits for ROM boot-ready when the boot status has bits 0x300 and ready is 0, clears 0x805fe0 and 0xf04404, copies the (index, value) halfword pairs at the pointer in 0x80fd4c into 0xf04800 + ((index << 2) & 0x3fc), writes 0xf04079 = 0, 0xf04078 = 16, 0xf04080 = 1 then 2, and calls RF_IrqConfigure (still asm, 0x311db8). Harness (`run_ihw.sh`, `--handlers --mmio --nor0`, hook `pre_ihw.h`: pair counts {0,1,2,3,4,5,9,255,6,7,16,33}, pointer into RAM, 0xf03838 bits forced set): baseline EQUIVALENT on 40 tests (text 144 B orig, 140 B C). 22 mutants, 20 killed (status mask, status test polarity, wait mask by timeout, 0x805fe0/0xf04404 values, count test, pairs formula, index mask/shift, base, entry[1]->[0], 0xf04079/0xf04078 values, 0xf04080 2->3, call removal, ready arg, RW16->RW32, pointer address). Equivalent (flag): `ready(status) == 0` -> `!= 0` (affects only the 0xf03838 wait, which the hook always satisfies) and the first `0xf04080 = 1` -> 3 (transient, overwritten by the following 2).
- RF_TestModeStart: mode >= 8 returns 0; modes 0/1 write 0xf04040 = 272/0x6000, 0xf04044 = 0xffffffff, 0xf04050 = 16, 0xf040bc = 0x10000; modes 2..7 write 0xf040bc = {0, 0xffff, 0x5555, 0x3333, 0x0f0f, 0xff}, then 0xf04050 = 0, then set bit 16 of 0xf040bc; then call the transmit trigger (0x312390, C) and return 1. Harness (`run_tms.sh`, `--handlers --mmio`, hook `pre_tms.h`: modes 0..9, 255, 0xffffffff, 0x80000000, random): baseline EQUIVALENT on 40 tests (text 140 B orig, 138 B C, 22 stub calls). 19 of 19 compilable mutants killed (bound 7/9, <=1 split, every constant and pattern, `|= 0x10000`, trigger call removed, return 1->0); one mutant (`case 4:` -> `case 5:`) is a duplicate case and does not compile. Not mutated: order of the 0xf040bc / 0xf04050 writes (only the final memory hash is compared).
- Install: conv.py (two blocks); chkref `bad 0`; both new files and stock_residual_code.c compile with -Wall -Wextra -Werror.
- Build w28s (-Os, fresh): 775/775 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,972 B (w28r 238,968 B; stock 210,888 B).
- FLAGS (guesses): register meanings at 0xf04040/0xf04044/0xf04050/0xf040bc/0xf04078..0xf04080/0xf04404/0xf04800 and the table at 0x80fd4c/0x80fd50 are address-only names; `incoming` is the caller's untouched r0 (RF_Init reaches it with 0x3a); the 0xf03838 wait loop is untestable (hook sets both bits); stock RF_TestModeStart keeps blink in r3 across the trigger call and relies on 0x312390 not clobbering r3, the C version has no such dependence (orig harness variant pushes blink instead).

### Step 30 (Wed Oct 28 2026, 9:21 PM CDT): System_Save 0x313880 (130 B) + System_Restore 0x3137fc (130 B) lifted to C

- New `application/System_SaveRestore.c` (`void opencfw_em9305_stock_313880(void)`, `void opencfw_em9305_stock_3137fc(void)`), registered once in sources.json (conv.py ran twice into the same file; duplicate entry removed). `stock_residual_data.c` references both by symbol. The record pointer word at 0x80fd80 is re-read through a volatile access before every record access, as stock does.
- Save: record word 0x4c = (0xf03800 & 1); record offsets 4..0x2c = 0xf03804..0xf0382c (11 words); 0x30 = 0xf03830; 0x34 = 0xf03834; 0x44 = 0xf03844. Restore: passes record word 0x4c to the sleep ROM prepare routine (0x103ab4, `opencfw_em9305_sleep_rom_prepare`), then writes the same registers back (0xf03800 is not rewritten directly).
- Harness (QEMU-ARC, `--handlers --mmio --nor0`, `run_sys.sh` with `SYM=`, hook `pre_sys.h`: record pointer into random-filled RAM, and on every fourth test pointed so a record store overlaps the pointer word at 0x80fd80, offsets {0x4c, 4, 8, 0x2c, 0x30, 0x34, 0x44, 0}): both baselines EQUIVALENT on 40 tests (text 264 B orig for both functions, 184 B C). 24 mutants (12 per function: `& 1`, record offsets, loop bound 10/12, loop start, stride, source/destination register addresses for 0x30/0x34/0x44, prepare argument and call removal): 22 killed. Two equivalent, genuinely so: loop bound `i <= 12` in both functions (the extra iteration copies word 0xf03830 <-> record 0x30, which the next line writes identically).
- Install: chkref `bad 0`; `System_SaveRestore.c` and `stock_residual_code.c` compile with -Wall -Wextra -Werror.
- Build w28t (-Os, fresh): 776/776 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,892 B (w28s 238,972 B; stock 210,888 B).
- FLAGS (guesses): registers 0xf03800..0xf03844 and the record fields are address-only names; stock leaves the record pointer (Save) and record word 0x44 (Restore) in r0, treated as void; the record at 0x80fd80's target is not allocated by the linker (stock does the same); the aliasing of a record store onto the pointer word is exercised by the hook and matches stock.

### Step 31 (Wed Oct 28 2026, 11:42 PM CDT): AOAD_Init 0x30299c (126 B) + receiverTestCheckParameters 0x3335f4 (128 B) lifted to C

- New `application/AOAD_Init.c` (`void opencfw_em9305_stock_30299c(void)`) and `application/receiverTestCheckParameters.c` (`uint32_t opencfw_em9305_stock_3335f4(const uint8_t *p, uint32_t length, uint32_t mode)`), each registered once in sources.json. New address-only ROM facade `em9305_rom_102b00(index, value)` in `em9305_link_closure.c`. `AOAD_Init_veneer.c` (0x302a1c `b 0x30299c`), `EMSRC_ReceiverTest.c`, `EMSRC_EmCoreReceiverTest.c` and `stock_residual_data.c` already reference the symbols; unchanged.
- AOAD_Init: clears byte 0x8019f1; when the enable byte at 0x80fb60 is non-zero, copies words 0x80fb48/4c/50 to 0xf04c04/08/0c and, for each non-zero flag byte i (0..11) at 0x80fb54.., clears bit i in 0xf0340c/0xf03408/0xf03400, sets bit i in 0xf03404 and calls ROM 0x102b00(i, 0xd). Harness (`run_aoad.sh`, `--handlers --mmio --nor0`, `--rename 0x102b00=em9305_rom_102b00 --arity 2`, hook `pre_aoad.h`: enable byte {0,1,0xff,2}, flag bytes random zero/non-zero plus all-zero and all-one tests): baseline EQUIVALENT on 40 tests (text 128 B orig, 160 B C: the volatile read-modify-writes are larger than stock's). 27 mutants (enable test, enable/clear addresses, each copied word source/destination, loop bound 11/13, start index, flag base, flag test, each register address, set/clear polarity, bit index +1, ROM args): 27 killed.
- receiverTestCheckParameters: mode 0 needs length 6, p[0] < 0x28, p[1]-1 < 5; mode 1 needs length 7, the same, and p[6] < 2; mode 2 (length unchecked) needs p[0] < 0x28, p[1]-1 < 5, p[6] < 2, p[7] == 0 or 2..0x14, p[8] < 3, p[9]-1 < 2 and (uint8_t)(p[10]-76) > 181; other modes return 0. Harness (`run_rtc.sh`, `--handlers --mmio`, hook `pre_rtc.h`: 52 deterministic boundary tests, each field's edge values per mode, wrong lengths, invalid modes 3/0xffffffff/0x80000000, then random-valid tests): baseline EQUIVALENT on 56 tests (text 128 B orig and C). My first hook (random boundaries) left 17 of 27 mutants alive, so it was replaced by the table above. 29 mutants (every limit and constant, the p[7] special cases, the p[10] range, mode and length checks): 29 killed.
- Install: conv.py (two blocks); chkref `bad 0`; new files, `em9305_link_closure.c`, `stock_residual_code.c` and the three referencing files compile with -Wall -Wextra -Werror.
- Build w28u (-Os, fresh): 778/778 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit insn hits 4, data-word hits 2, in-range words checked 349 (was 350: the `ini_record_335820` word that held 0x335fd4 now holds 0x3365a8, i.e. an address that moved past the 0x336000 audit window because the image grew by 36 B; not a stale hard-coded address); final link g2-em9305 `undef refs: 0`, image 238,928 B (w28t 238,892 B; stock 210,888 B).
- FLAGS (guesses): ROM 0x102b00 role unknown (arguments (index, 0xd), named by address only); registers 0xf03400..0xf0340c, 0xf04c04..0xf04c0c and the record at 0x80fb48 are address-only names; stock leaves a stale r0 from AOAD_Init (treated as void); receiverTestCheckParameters field meanings (channel, PHY, etc.) are inferred from the HCI LE receiver-test layout and unverified; the callers seen (EMSRC_ReceiverTest, EMSRC_EmCoreReceiverTest) only pass modes 0 and 1, so the mode-2 branch (and the p[10] test) is verified by the harness only; length is ignored in mode 2 as in stock.

## 2026-10-29 — rescan, untagged upstreams, bootloader SYSPLL from upstream

- Rescan of all seven payloads against every local upstream/vendor tree:
  `g2/docs/reference/untagged-upstream-dependencies.md`. Main finding: the Even
  bootloader links the AmbiqSuite 5.1.0 HAL pinned for apollo-main but built
  none of it from source (64 functions, 16.8 KB mapped in
  `coverage-2.2.6.10/bootloader-ambiq-hal-map.tsv`). Second: 1,182 named
  EM9305 functions exist in open Cordio r20.05c (Apache-2.0) while about 810 are
  being lifted from lowered assembly. The EM SDK v4.6 Packetcraft headers are
  confidential/proprietary and are not used.
- Bootloader now builds `am_hal_syspll.c` from `third-party/upstream/ambiqhal-apollo510`
  (generated copy `ambiqhal-apollo510-boot/am_hal_syspll.c` compiles out
  `am_hal_syspll_mux_select`, absent from stock). New profile
  `g2-apollo-bootloader-6` (bootloader flags plus HAL includes). Removed hand
  copies `clock_pll_math.c`, `syspll_disable_4273dc.c` and the PLL generators in
  `clock_generators.c`. `clock_class_provider6.c` calls the HAL API. New
  `clock-manager/syspll_hal_bindings.c` holds the stock `am_hal_pwrctrl_syspll_*`
  and `am_hal_sysctrl_clkmuxrst_pll_fref_update` bodies until those upstream
  files are built here. `am_hal_delay_us{,_status_check}` are aliases of the
  existing stock implementations. The IAR libm helpers are now `floorf/roundf/ceilf/fmodf`.
- Verification: `g2/evidence/bootloader-syspll-upstream-review.json` — REA/Ghidra
  decompile of stock 0x42740c matches `am_hal_syspll_configure`; Unicorn
  differential of stock bytes against the new C, 3,036 cases (generators,
  configure incl. MMIO write order, enable/disable/deinitialize/lock_wait),
  0 mismatches; a one-operator mutant is caught (25/600).
- Build: `sources.py check` 5,221 units / 4,899 files; bootloader 381/381
  compiled, 0 duplicate strong symbols, 0 unresolved; final link OK, image
  157,636 B (was 157,364 B; stock 148,599 B). Other payloads not rebuilt.
- Hazard recorded, not fixed: bootloader `.bss` (`opencfw_boot_iom_contexts`,
  0x20000000..0x20004540) overlaps 89 hard-coded stock RAM cells.
- Next: `am_hal_queue.c`, `am_hal_cmdq.c`, `am_hal_clkgen.c`, `am_hal_mspi.c`
  (reuse apollo-main's control variant), then SPOTMGR, for the bootloader.

## 2026-10-29 — bootloader RAM layout follows the stock map

- Stock places the IOM contexts at 0x2001455c (literal 0x42cdb4 loaded by the
  claim at 0x42c4c6; 8 x 0x8a8 to 0x20018a9c) and `g_SysPLLState` at
  0x20027010 (literal 0x4275a4, `am_hal_syspll_initialize` 0x4272ac). Both lie in
  the stock zero record 0x2000055c..0x200271c8 that startup clears; stock
  initialized cells are 0x20000000..0x2000055c. UART (0x20024400) and ADC
  (0x20026df0) pools match literals 0x4233e4 and 0x42f150.
- `apollo-bootloader/link/g2-apollo-bootloader.ld` now pins those four objects
  at their stock addresses (with slot-size asserts), places generic
  `.data`/`.bss` in `DTCM_FREE` 0x200271c8..0x2007d000 (between stock zeroed
  cells and the stack limit), and asserts both are empty, because startup only
  runs the stock init records and never copies `.data` or clears `.bss`.
- Verification: fresh `sources.py build` of the bootloader: 381/381, 0
  duplicate strong symbols, 0 unresolved; `.waves/link-final.sh` links,
  image still 157,636 B. `build/check_bootloader_ram_overlap.py` (ignored
  build tree) compares every `0x20xxxxxx` literal in
  `g2/src/apollo-bootloader` (205 distinct) with the ELF's RAM symbols and
  writable sections: 0 overlaps after; 72 before (the old 0x20000000 placement).
  This resolves the hazard in
  `reference/untagged-upstream-dependencies.md`.

## 2026-10-29 — bootloader queue, PRIMASK, CMDQ and CLKGEN from upstream

- The bootloader now builds `am_hal_interrupt.c` and `am_hal_queue.c` verbatim,
  and generated copies of `am_hal_cmdq.c` (`am_hal_cmdq_pause` compiled out)
  and `am_hal_clkgen.c` (only the eight private leaves stock links), from the
  pinned AmbiqSuite 5.1.0 tree, all with profile `g2-apollo-bootloader-6`.
- Removed hand copies: `critical_save.S`, `irq_guard.S`,
  `critical_save_adapter.c` (23 callers renamed to
  `am_hal_interrupt_master_*`), the UART ring functions, the CMDQ bodies in
  `nor_mspi_queue.c`, `queue_descriptors.c/.h`, `resources.c`, two leaves of
  `control_request_helpers.c`, `clock_generators.c/.h`, and the CLKGEN statics
  (with their duplicates) in `clock_class_provider4/5.c` and
  `startup_clock_config.c`. The dead duplicate clock-gate body in
  `nor_mspi_queue.c` went with profile `g2-apollo-bootloader-5`.
- `gAmHalCmdq` is pinned at stock 0x200262f0 in the link script.
- Differential tests of stock bytes against the final linked image (Unicorn;
  PRIMASK and Armv8.1-M CSEL emulated): queue 500 sequences, CMDQ 800
  operation sequences with a CQ hardware model, CLKGEN 4,000 calls; 0
  mismatches; mutants caught. Record:
  `evidence/bootloader-hal-upstream-review.json`; the HAL map marks 36 rows
  Verified.
- Build: `sources.py check` 5,219 units; bootloader 379/379, 0 duplicate
  strong symbols, 0 unresolved; final link OK, image 157,380 B. Other
  payloads not rebuilt (no shared files changed).
- `thread-creation/*.ld` and `nor-mspi-queue/module.ld` are old per-module
  link scripts no build uses; they still name removed symbols.
- Next: `am_hal_mspi.c`. It needs the clock-manager and power-control
  bindings first; see `reference/untagged-upstream-dependencies.md` §1.

## 2026-10-29 — bootloader is AmbiqSuite SDK 5.0.0; MSPI from upstream

- The bootloader HAL is SDK 5.0.0 RTM (ambiqhal_ambiq `392042e`), not 5.1.0:
  stock `am_hal_mspi_device_configure` has the 5.0.0 `bNewDDR` branch, stock
  `am_hal_mspi_control` uses the 5.0.0 request enum (the "stock variant"), and
  the image lacks the aperture table added by the post-RTM fix `9df2220`.
  5.0.0 is pinned as `third-party/upstream/ambiqhal-apollo510-sdk5.0.0`
  (shallow submodule; staged with `.gitmodules`). Profile
  `g2-apollo-bootloader-6` now uses it, plus `-fno-vectorize
  -fno-slp-vectorize` (clang otherwise emits MVE loops; stock has none).
- `am_hal_mspi.c` builds verbatim from 5.0.0, control included. Removed the
  hand split of control (`nor-mspi-init/control_*.c/.h`), `fifo_transfer.c`,
  `blocking_transfer.c`, `nor-mspi-power/device_configure`, `power_control*`,
  `mspi_clockgen_control.c`, `nor-mspi-queue/`, `mspi/`, the MSPI glue in
  `glue/`, the MSPI leaves of `hal_leaves.c` and `am_hal_mspi_initialize` in
  `nor_mspi_init.c`. NOR-driver callers now use the `am_hal_mspi_*` names.
  `g_MSPIState` is pinned at stock 0x2001caa0. The hand clock-manager and
  power-domain functions carry upstream-name aliases for it.
- Differential (Unicorn, final linked image vs stock, callees stubbed equally):
  MSPI 1,500 operation sequences over all 13 public functions, 0 mismatches;
  two mutants caught (244/400, 381/400). Queue, CMDQ and CLKGEN re-run on the
  5.0.0 image: 0 mismatches. Record: `evidence/bootloader-hal-upstream-review.json`.
- Build: `sources.py check` 5,197 units; bootloader 357/357, 0 duplicate
  strong symbols, 0 unresolved; final link OK, image 158,108 B.
- apollo-main's MSPI "stock variant" control also uses the 5.0.0 enum; see
  `reference/untagged-upstream-dependencies.md` §1.

## 2026-10-29 — bootloader status helpers and UART from upstream

- `am_hal_delay_us_status_change/check` (0x41d21c/0x41d246) build from a
  generated 5.0.0 `am_hal_utils.c` that keeps only those two; 17 callers
  renamed, `status_poll.c` and `runtime_wait_adapter.c` removed. Stock
  `am_hal_delay_us` calls the boot-ROM loop at 0x41 rather than the SDK's ITCM
  loop, so it stays hand code. Differential: 3,000 cases, 0 mismatches.
- The UART HAL is the 5.1.0 `am_hal_uart.c` (stock state layout is 5.1.0, not
  RTM), built verbatim from the 5.1.0 pin against the 5.0.0 headers.
  `g_am_hal_uart_states` is pinned at 0x20024400. Removed the hand UART HAL
  (`uart_rx.c/.h`, `uart_irq_dispatch.c`, `uart_irq_status.c`,
  `uart_context.h`, most of `uart_context.c` and `elog_uart_tx.c`,
  `glue/post_configure_alias.c`, the guard in `runtime.c`); Even's IRQ row
  wrapper and log send stay. Differential: 400 sequences, 0 mismatches
  (baud 0 excluded: undefined in the upstream C).
- So the bootloader HAL is a snapshot between 5.0.0 RTM and 5.1.0; choose the
  revision per file by test.
- Build: bootloader 353/353, 0 unresolved, image 157,300 B; `sources.py
  check` 5,193 units.
- Next: the power core, `am_hal_pwrctrl.c` + `am_hal_spotmgr*.c` +
  `am_hal_clkmgr.c`. SPOTMGR alone needs about 55 globals pinned at stock
  addresses and stock init records for 140 B of `.data`.

## 2026-10-29 — bootloader PWRCTRL from upstream; harness IT-state fix

- The stock PWRCTRL block 0x41b8f8..0x41cae8 is SDK 5.0.0 `am_hal_pwrctrl.c`
  in source order with unlinked functions dropped (25 functions). It now builds
  verbatim. Its state is pinned at the stock cells: `g_ui32TrimVer`
  0x20000098, `g_DefaultMcuMemCfg` 0x2000009c, `g_eCurMcuPwrMode` 0x20000552
  (initialized record, which already holds the SDK initializers),
  `g_sINFO1regs` 0x200267f8, five trim snapshots 0x2002704c..0x2002705c, the
  GPU/ROM mode bytes and `g_bOrigTrimsStored` 0x200271a5..0x200271a8, and
  `g_ui8TRCENAcount` 0x200271a3. Clang drops eleven write-only static trim
  snapshots that stock stores at 0x20027060..0x2002708c; nothing reads them.
- Stock `am_hal_pwrctrl_temp_update` takes its float in `s0` (hard-float HAL,
  softfp bootloader). A generated `am_hal_pwrctrl.h` gives it
  `pcs("aapcs-vfp")` and profile -6 searches that copy first.
- Removed 22 hand files (the PWRCTRL halves of `platform-control/`, the
  register-carry startup root, memory-config and TON-gate leaves, query table,
  power guards, GPU mode) and the PWRCTRL functions in eight more. The SPOT
  dispatcher wrappers, INFO1 read, debug trace release and clock-mux reset
  keep their hand bodies under upstream alias names until their files move.
- Linker pins now assert with `ABSOLUTE(.)`. Inside an output section `.` is
  section-relative, so the earlier `. <= limit` checks could never fail.
- Harness defect: a Unicorn memory-write hook that fires inside a Thumb IT
  block leaves IT state set, so later instructions are skipped as if
  conditional. MMIO now uses `mmio_map` callbacks, the PRIMASK/CSEL emulation
  hooks only those instructions, and every module was re-run on the new image:
  queue 500, PRIMASK 4, CMDQ 800, CLKGEN 4,000, MSPI 1,500 (10M budget), status
  polls 3,000, UART 400, PWRCTRL 1,500, all 0 mismatches. PWRCTRL mutants
  caught 37, 43 and 11 of 400.
- Build: bootloader 338/338, 0 unresolved, image 157,012 B; `sources.py
  check` 5,178 units.
- apollo-main's PWRCTRL has the same function sizes and its "older-revision"
  variants describe the 5.0.0 text, so its PWRCTRL and SPOTMGR hand variants
  are 5.0.0 too (see untagged-upstream-dependencies.md).

## 2026-10-29 — bootloader CPDLP duplicates, no MVE, SPOTMGR revision

- `thread-creation/idle_sleep/sleep_helpers.c` held second copies of stock
  0x41c9ca/0x41ca0c (`am_hal_pwrctrl_pwrmodctl_cpdlp_config/get`) and the SPOT
  autoswitch wrappers 0x41ce26/0x41ce3c. The sleep code now calls the upstream
  PWRCTRL functions and the wrappers' upstream names; the file is gone.
- Bootloader hand profiles -1/-3/-4 add `-fno-vectorize -fno-slp-vectorize`
  (as -6 already did): clang had emitted 475 Helium/MVE instructions
  (`dlstp`/`letp` copy loops and others) that the stock image does not
  contain. Image 154,652 B.
- The differential harness now also emulates MRS/MSR for BASEPRI, WFI/WFE,
  Armv8.1-M DLS/WLS/LE, and enables VFP, so whole-image paths (startup init
  records, float SPOT code) run.
- SPOTMGR was swapped to upstream, tested, and reverted: the stock SPOTMGR is
  an unpublished Ambiq revision between `66185cb` and 5.1.0 (see
  untagged-upstream-dependencies.md). The hand SPOTMGR stays; the tested swap
  is in `build/snap-stage2/` and `build/boot-hal-diff/diff_spotmgr.py` is
  ready for the per-context work.
- Harness: VFP is now enabled and VSEL emulated. Before that, both sides
  faulted on their first VFP instruction and the PWRCTRL run counted the
  matching faults as agreement, so `temp_update` was not really tested. Faults
  are now counted separately; the remaining ones are NULL-argument calls that
  fault at address 0 on both sides.
- Final image re-run: queue 500, PRIMASK 4, CMDQ 800, CLKGEN 4,000, MSPI 1,500,
  status polls 3,000, UART 400, PWRCTRL 1,500, all 0 mismatches; PWRCTRL
  mutants caught 39, 58 and 20 of 400. Build 337/337, 0 unresolved,
  154,652 B; `sources.py check` 5,177 units.
- SYSPLL re-verified on the final image (harness ported to the IT-safe base,
  VSEL emulated): 3,036 cases, 0 mismatches, 0 faults.

## 2026-10-30 — apollo-main PWRCTRL from upstream SDK 5.0.0

- apollo-main's PWRCTRL block (0x47ef18..0x4800e4) is the same SDK 5.0.0
  `am_hal_pwrctrl.c` as the bootloader's: equal function sizes in source
  order and the same callee at every one of its call sites. It now builds
  verbatim (profile `g2-apollo-main-108`: 5.0.0 headers, no vectorizer, no
  global merge). Retired: `hal/x-03-pwrctrl/`, `hal/final-r1-pwrctrl/`,
  `drivers/power/power-vendor/`, `runtime/info-memory/memory.c/.h`,
  `ble/ble-flash/display_ble_flash_mode.c`, `system/glue/memory_config_aliases.c`,
  the generated 5.1.0 copy with its 27 replacements, and the duplicate
  `audio_ble_flash_mode` cell (it is `g_eCurROMPwrMode`). Callers keep their
  names through compose aliases.
- Test: the manifest object linked standalone with its globals at the stock
  cells and its callees at the stock addresses, run against the stock OTA
  image (`build/main-pwr/diff_main_pwrctrl.py`): 1,500 cases, 0 mismatches;
  mutants caught 4, 34 and 4 of 400.
- Harness: the PRIMASK trace was shared across a case's steps, and GFX/CRYPTO
  paths were rarely hit; both fixed in the bootloader harness too, which
  re-ran at 1,500 cases, 0 mismatches.
- All apollo-main profiles now use `-mcpu=cortex-m55+nomve`. Stock main has
  no Helium/MVE instructions, but clang lowered memcpy and struct copies to
  MVE (155 `dlstp`/`letp` loops, about 1,000 `vldr*`/`vstr*` across 258
  objects); the vectorizer flags alone did not change that. The composed
  object now has none.
- apollo-main 2,863/2,863 compiled, 0 duplicates, the same 24 unresolved
  names; `sources.py check` 5,170 units.

## 2026-10-30 — apollo-main MSPI from upstream SDK 5.0.0 RTM

- apollo-main's MSPI (0x4bfa10..0x4c2af6) is instruction-for-instruction the
  bootloader's verified SDK 5.0.0 RTM MSPI, plus three functions the
  bootloader does not link. It now builds the 5.0.0 file unchanged (profile
  `g2-apollo-main-108`). Retired: the 12-file hand split of
  `am_hal_mspi_control` under `drivers/flash/mspi/` and the generated 5.1.0
  copy with its 12 replacements; `g2_norflash_config_transfer_4c0f78` is now a
  compose alias of `am_hal_mspi_control`.
- Callers already used the stock (RTM) 24-byte device config and request
  numbers, so the implementation now matches them; the 5.1.0 copy did not.
- Test (`build/main-pwr/diff_main_mspi.py`, standalone link against the stock
  OTA image, stock CMDQ running natively): 1,500 cases, 0 mismatches; mutants
  caught 381, 139 and 13 of 400.
- apollo-main 2,851/2,851 compiled, 0 duplicates, the same 24 unresolved;
  `sources.py check` 5,158 units.

## 2026-10-30 — bootloader SPOTMGR from upstream

- Project goal clarified by the user: a working firmware, not stock identity.
  Newer upstream text is preferred where it does not change how the hardware
  is driven.
- The bootloader builds `am_hal_spotmgr*.c` from SDK 5.0.0 + AmbiqSuite patch
  `66185cb`. On top of that it takes the 5.1.0 hunks stock also has: three in
  PCM2.0, the HFRC2 force in PCM2.2 `SWITCH_TO_HP`, and the PCM2.1 deep-sleep
  override without the TIMER A test. The 78 hand SPOTMGR files are removed;
  the RAM pins and transition-table copy are those from the earlier attempt.
- The earlier "per-sequence" divergence was largely a harness error (`r0`
  compared after void sequences); the real differences were the two hunks
  above.
- Verification: standalone overlay (`build/spot-sa/`) with 27 x 30 direct
  sequence calls, 0 mismatches, and 1,500 cases, 0 mismatches; mutants caught
  53 and 12 of 400. On the linked image (155,064 B) the full suite matches:
  SPOTMGR 1,500, PWRCTRL 1,500, MSPI 1,500, CLKGEN 4,000, CMDQ 800, queue 500,
  UART 400, status polls 3,000, SYSPLL, all 0 mismatches.
- Build: 299/299; the three compose-unresolved names are the transition-table
  linker symbols the final link defines.
- Correction (later the same day): apollo-main SPOTMGR is the same text as
  the bootloader's, and it now builds the same upstream source (see the next
  section).

## 2026-10-30 — remaining assembly to C, case image linked, duplicates removed

Policy as above: a working firmware, not stock identity. Assembly stays only
where the architecture needs it. Scratch work and harnesses for each step are
under `build/` (the directory named in each step).

- **EM9305 lowered units.** All lowered-assembly units under
  `em9305/qpc-scheduler/initializer_lowers/` are now C, along with
  `application/stock_residual_code.c` and `stock_residual_data.c`.
  - Each unit is proven against its stock copy under QEMU-ARC
    (`.waves/qrun.py`, 100 random cases, with a mutant check for branchy
    code).
  - Results: `build/em-lift/results-slice*.tsv` and `results-big-{A,B}.tsv`.
    `311e04` is a partial proof (log2p0/fssub).
  - The four QK context-switch entries stay in assembly
    (`application/qk_port_swi.c`).
  - Fixed while doing this: `__divdi3` (the lowered copy had lost a
    `leave_s`); `32b82c` and `32db0c` each had two copies and now have one.
- **EM9305 `controller_init.c` and inline assembly.** The 10 top-level
  assembly functions and about 230 pinned arithmetic statements are now C;
  hardware statements use `__builtin_arc_*`.
  - 192 changed functions are EQUIVALENT in QEMU, and every mutant is caught.
    Results: `build/em-ctl/results-*.tsv`; harness `build/em-ctl/qm.py`.
  - Bugs fixed:
    - `ll_slot_apply_308708` read r2 after a call had clobbered it;
    - `config_link_has_remainder` read Z without setting it.
  - Still assembly:
    - ILINK accesses (no builtin exists);
    - the calibrated `lp_count` delay;
    - the APEX `bswp8`/`log2p0` instructions.
- **EM9305 profile.** `g2-em9305-1` now adds
  `-mdiv-rem -mbarrel-shifter -mswap -mnorm -mmpy-option=wlh1`, the core
  options listed in `findings-codec-em9305.md`.
  - C division now uses hardware `div`/`rem`; `__divsi3`, `__udivsi3`,
    `__modsi3` and `__umodsi3` are gone from the unresolved list (13 → 9).
  - Stock and our startup both set STATUS32.DZ, so a zero divisor raises
    EV_DivZero and the unused-vector handler resets the chip. The C therefore
    has no zero-divisor guards.
  - Re-proved under the new flags: 192/192, and 39 of 47 sampled slice units.
- **apollo-main naked functions.** 34 functions are now C, including veneers
  turned into typed aliases.
  - Bugs fixed: the `APP_StartServiceDiscovery` log argument; ANCS app IDs of
    62 characters or more now send nothing, where they used to overflow.
- **ARM inline assembly (bootloader, apollo-main, case).**
  - 88 halt loops are now `for (;;) {}`.
  - SDIV/UDIV, VFP arithmetic, converts and compares are C with ARM edge
    semantics: divide by zero gives 0, INT_MIN/−1 gives INT_MIN, VCVT
    saturates, and multiply-adds are not fused.
  - LDREX/STREX use builtins.
  - 26 Unicorn differential tests (`build/arm-pin/pindiff.py`) show 0
    mismatches, and each catches its mutant.
  - Fixed while doing this: LLVM turned `-(a/b)` into `(-a)/b`, which changed
    the sign of NaN results; the `*_neg` helpers are now `noinline`.
- **Codec (C-SKY).**
  - Stage-1 CRT initialisers and the residual `.S` files are now C. The IRQ
    entries use `__attribute__((isr))`, which produces the stock entry.
  - Stage-1 clock helpers rebuilt from stock: rail A/B/C, PLL config and
    module clock rate. Bugs fixed in the rate helper, which had put a wrong
    value in 0xa0400024:
    - DMA was mapped to the wrong clock (SCPU);
    - the 1M/12M case returned 0;
    - the DTO mask was not 25-bit;
    - a missing divider field returned 0.
  - Stage-1 data now lives in named objects in `.stage1.data` at 0x20002004.
    Stage-1 read-only data stays in STAGE1, not XIP flash.
  - Divide, shift and DSP pins are C (`codec/csky_ops.h`). Proven in XuanTie
    QEMU: shifts 810 cases, divides 420, DSP ops about 400k, and the
    inverse-RFFT split 12,700 outputs, all identical.
  - Still assembly: the reset/exception entries, `frecips`, and system-control
    registers.
- **Case firmware linked for the first time.**
  `case/link/g2-case.ld` places `.data`/`.bss` above 0x20002c88, because the
  case C reaches all of its stock RAM state (0x20000000..0x20002c88) by
  absolute address.
  - A 20-byte record at 0x080000b8 gives `case_crt_init_0270` the copy and
    zero ranges.
  - `.waves/link-final.sh` gained a `g2-case` branch.
  - Unicorn boot test (`build/case-link/boot.py`) against `firmware_box.raw.bin`
    on four paths, all identical to stock in peripheral writes and console
    text:
    - reset to first task switch (4,009 writes);
    - about 6 s of tasks (6,570 writes);
    - no devices attached;
    - first-boot option-byte programming.
  - 11 bugs fixed that had stopped it booting. The main ones:
    - RCC_CR `|= 0x1000` written where stock sets FLASH_ACR prefetch;
    - an oscillator-setup loop that never exited;
    - ADC calibration always skipped;
    - six strings one byte early;
    - six log calls missing an argument.
  - Duplicates: 81 stock functions had several implementations; 93 names
    became aliases and 39 units were removed. Where copies differed, the one
    matching stock was kept, which removes:
    - a hang in queue-send-from-ISR;
    - a 3-word timer command where the queue copies 4;
    - a busy-bus read that returned 0.
  - Software-bus timing now matches stock: PMIC/fuel-gauge about 225 kHz;
    2510/4005 single-wire pulses within 1–2 cycles. Measured with
    `build/case-link/timing.py` at 64 MHz with 2 wait states.
  - The unused stock compiler-runtime helpers (Thumb jump-table dispatcher,
    64-bit udivmod) were removed.
  - Image: 60,168 B (stock 55,752 B).
- **Duplicate stock functions in apollo-main and the bootloader**
  (`build/dedup-main/`). An inventory maps every linked function to its stock
  entry, and every candidate pair was reviewed against stock.
  - apollo-main: 198 duplicate bodies removed. The libc cores are shared, WSF
    and SMP now use the Cordio originals, and LVGL callers use upstream names.
    The kept copies now match stock: memcpy/memset return the destination, and
    the 0x43d0ce log gate and log line 306 are corrected.
  - Bootloader: 10 duplicate bodies removed (STIMER/PRIMASK copies, 0x415fae
    printf, 0x417b7c, 0x41d90e, the 0x41560c fill). 82 emptied units removed.
- **Build (`build/final-1030`).** Every payload compiles fully with 0
  duplicate strong symbols:

  | Payload | Units | Unresolved |
  |---|---|---|
  | bootloader | 226 | 3 |
  | apollo-main | 2,771 | 24 |
  | case | 366 | 0 |
  | codec-a | 347 | 0 |
  | codec-b | 332 | 0 |
  | em9305 | 772 | 9 |
  | touch | 101 | 12 |

  - All seven final links (`build/final-1030-link/`) have 0 undefined
    references.
  - `sources.py check`: 4,920 units.
  - Bootloader HAL diffs show 0 mismatches: spotmgr 400, pwrctrl 1,500,
    syspll, utils 3,000, clkgen 4,000, cmdq 600, queue 500, uart 400 and
    mspi 400.
- **Not run on hardware.** These remain unverified:
  - The proofs model the EM9305 APEX/DSP instructions (`mpywhl`, ASLACC) and
    the C-SKY `mulaca` saturation corner rather than running them on silicon.
  - Case clock/PLL, low-power modes, UART receive, OTA flash programming, the
    real tolerance of the 2510/4005 protocol, and the 6% shorter device
    timeouts.
- **Known stale:** `g2/evidence/case-semantic-strings.json` still lists the six
  string addresses that were one byte early.
- **Staged entries:** some codec and EM9305 application files appear in the git
  index. No worker in this pass ran git commands; the index was left as found.

## 2026-10-30 — apollo-main SPOTMGR from upstream; runtime helpers from libgcc

- **SPOTMGR.** Stock apollo-main SPOTMGR is the bootloader's text: SDK 5.0.0,
  patch `66185cb` and the same five 5.1.0 hunks.
  - apollo-main builds the bootloader's generated
    `{gen}/ambiqhal-apollo510-boot/am_hal_spotmgr*.c` with profile `-108`.
    40 hand units are removed, as are 50 compose aliases and the SPOTMGR RAM
    cells.
  - Scored against stock over 300 cases:
    - bootloader text: 0 mismatches;
    - plain `66185cb`: 50;
    - 5.1.0, `48793d7` and 5.2.0: 237 each. They change init register writes,
      simobuck waits and INFO1 reads, so they were rejected.
  - Test: `build/dedup2/spot/diff_main_spotmgr.py`, 1,500 cases, 0
    mismatches. Mutants caught: 3, 28 and 14 of 400. The weakest is the
    rarely reached PCM2.1 TIMER A path.
  - Bugs fixed: the sleep path read override flags and INFO1 from a RAM copy
    nothing wrote.
- **LVGL and ring duplicates moved to upstream:**
  - `_450672` → `lv_anim_path_ease_out`; the ease_in and ease_in_out copies
    too (204k cases);
  - the hand image cache and font LRU → `lv_image_cache`/`lv_cache_lru_rb`
    (20,000 cases); the hand vtables lacked `iter_create_cb`;
  - `audio_uart_lv_free` → `lv_free`;
  - `codec_ring_initialize` → `ring_buffer_init`.
- **Compiler runtime.**
  - `__aeabi_uldivmod` and `__aeabi_ldivmod` now come from libgcc
    (`thumb/v8-m.main+dp/hard`), because only compiler-generated calls used
    them. As a result apollo-main lists 26 unresolved names before the final
    link, where it had 24; the final link resolves them.
  - Removed because nothing called them: the IAR `cdrcmple`/`dcmpgt`/`cdcmple`
    helpers and the bootloader's `double_compare_flags.S`.
  - Test: 6,970 Unicorn edge cases, 0 mismatches. Two differences remain:
    - divide by zero returns all-ones where stock returned the numerator;
      `drv_buzzer.c` has a guard for its one reachable case;
    - NaNs with a zero upper mantissa now compare unordered, as the ABI
      requires.
- **Assembly that remains, all needed by the architecture:**
  - reset entries;
  - exception, context-switch and PendSV entries (FreeRTOS `portasm.c`,
    bootloader `exception_entry.S`/`first_task_transfer.S`, case
    PendSV/context switch, EM9305 `qk_port_swi.c`, codec
    exception/reset);
  - the bootloader handoff to the application;
  - setjmp/longjmp;
  - CmBacktrace's HardFault entry;
  - EM9305 ILINK accesses, the `lp_count` delay and the APEX `bswp8`/`log2p0`;
  - the case single-wire delay counters;
  - the codec `frecips`;
  - the bootloader's fixed-address ITCM helpers and init-record data;
  - single-instruction system intrinsics (CPSID/MSR/MRS/DSB/ISB/WFI, `mfcr`/
    `mtcr`, `kflag`/`sr`).

  Every lowered-assembly unit, naked function and pinned arithmetic statement
  in the reconstruction is now C.
- **Final build** (`build/final2-1030` and `build/final3-main`): every unit
  compiles, with 0 duplicate strong symbols.

  | Payload | Units | Unresolved | Image (B) |
  |---|---|---|---|
  | bootloader | 225 | 3 | 154,224 |
  | apollo-main | 2,717 | 26 | 3,827,387 |
  | case | 366 | 0 | 60,168 |
  | codec-a | 347 | 0 | 2,155,932 |
  | codec-b | 332 | 0 | 81,600 |
  | em9305 | 772 | 9 | 246,768 |
  | touch | 101 | 12 | 28,784 |

  - All seven links have 0 undefined references; images are in
    `build/final2-1030-link/`.
  - `sources.py check`: 4,865 units.
  - `system/glue/i2s_power_aliases.c` `#include`d a retired SPOTMGR file, so it
    was removed too.
- **Needs hardware:** boot, deep sleep and wake, HP/LP switching and GPU
  power under the upstream SPOTMGR on the device's PCM revision; the buzzer
  at frequency 0.

## 2026-10-31 — simulator findings: uncopied initialised data, EM9305 ROM cells, EM9305 stubs

**apollo-main `.data` (fixed).**
- 0x14aa4 bytes of writable named sections (`.g2_locale_data_*`, `.g2_conversate_*_2xxxxxxx`, `.g2_bss_*`, `.g2_pdm_clock_pin_words`) were orphans placed after `__data_end`, so the region-table copy row never loaded them.
- The jimrandomh Renode emulator read the lv_i18n locale tables as 0.
- Fix: `g2-apollo-main.ld` `.data` now collects `INPUT_SECTION_FLAGS (SHF_WRITE) *(.g2_*)`. After the fix the sim reads the ELF initial values; code addresses do not change.
- Evidence: `g2/docs/sim-test-report.md` (2026-10-31).

**EM9305 ROM-owned cells (fixed).**
- `g2_em_qf_next_priority` was `= 16u` in `.sdata` at 0x80fe20, and `g2_em_app_start_callback` was in `.sbss` at 0x80fe24. No EM9305 startup code copies or clears those sections, so on silicon both would hold garbage.
- Stock uses 0x8012bc (read and decremented at 0x30ead6/0x3140ec) and 0x8010a4 (`ld r12,[0x8010a4]` at 0x30ec6c). It never writes either, and the package's four records are NVM-only, so the ROM owns them.
- Both are now NOLOAD pins at the stock addresses (`g2-em9305.ld`, `em9305_link_closure.c`). The externs carry the section so ARC GCC addresses them absolutely, not gp-relative.
- Build: 772/772 compiled; the final link has 0 undefined.

**Correction to the 2026-10-30 entries: the EM9305 image still has empty stubs for eight stock routines** in `em9305_link_closure.c`: `BSP_Init` (0x302e80), `irq_set_user_callback_3069b8`, `wsf_os_init_only_veneer_30460c` (stock `b 0x314068`), `wsf_os_register_start_304610` (stock `bl 0x3140a8; bl 0x3140d0`, WSF active-object ctor/start), `lhciCmdVsExtInterfaceEM`, `wsfOsRunIdleTasks`, `application_startup_hook_30482c` and `volt_monitor_measure_zero_3119a8`. The image compiles and links, but it is not functionally complete, and it must not go to hardware until these have stock bodies.

**EM9305 stubs replaced (same day).**
- New unit `qpc-scheduler/wsf_os_ao.c` implements the WSF OS active object ("WsfOs"):
  - WsfOsInitOnly 0x314068: clears the context at 0x805ff4 (0x7c B), then `QActive_ctor(0x80139c, initial)`.
  - The init-callback store 0x3140a8 (RAM 0x8019e4).
  - WsfOsStartOnly 0x3140d0: assertion 653, priority from 0x8012bc, queue 0x80faac ×16.
  - The initial pseudo-state 0x333db8.
  - The dispatch state 0x333c44: entry runs the init callback; signal 8 services queued messages, expired timers and the 16 per-handler event half-words, using the existing `opencfw_em9305_wsf_*` helpers.
  - `wsfOsRunIdleTasks` 0x333d7c.
  - The two veneers 0x30460c and 0x304610; 0x304610 registers `opencfw_em9305_controller_initialize_stack` 0x302a20.
- `em9305_link_closure.c` now carries the stock bodies of:
  - `BSP_Init` (stores 3 to 0xf00a78, then sync);
  - `irq_set_user_callback_3069b8` (RAM 0x80190c);
  - `lhciCmdVsExtInterfaceEM` 0x32e5a8 (allocate, copy, send at header−2, callback set, return 1);
  - `application_startup_hook_30482c` (`pal_metadata_register(0x8012e4)`);
  - `volt_monitor_measure_zero_3119a8` (`timer_enable(0)` at 0x313ae4).
- Build: 773/773 compiled under -Werror; the final link has 0 undefined; `make sources-check` passes.
- Verification: each body was reviewed instruction by instruction against the corpus disassembly. It is **not** emulator-checked, because no stock-lowered reference unit exists for these routines.
- Still open: about 127 stock call targets in 0x302400..0x3340bc are not named in any EM9305 source (heuristic scan). Each needs to be classified as dead, renamed, or missing.

**apollo-main bond records (fixed, 2026-10-31).** The Cordio app_db bond page (10×256 B at mapped MRAM 0x7ff000) was linked into SSRAM .bss because its `.ld` fragment was never included. The sim OTA round trip showed the retained phone key rejected (HCI 0x06). It is now pinned in `g2-apollo-main.ld` beside the OTA flag page. Evidence: `g2/docs/sim-test-report.md`.

**apollo-main file-API mutex (fixed, 2026-10-31).** Stock RAM 0x200748f4 was split into `g2_codec_redirect_mutex` (created by redirect_init 0x474d9c) and `audio_file_api_mutex` (locked by file_open/read/write/close, never set). Every file-API open therefore failed, including the OTA receiver's filesystem health probe, so OTA START returned status 10. The fix makes them one object (an alias). Evidence: `g2/docs/sim-test-report.md`.

## 2026-11-10 — fresh all-payload compile and strict source linkage

**Codec image-A AOUT SRAM placement (2026-11-10).** The source linker now
places the 52-byte AOUT context at `0x10026b94`, the 84-byte dispatch table at
`0x10026bc8`, and the 88-byte hardware configuration at `0x10026c1c`, with
link-time size assertions. They occupy the stock gap before the UART receive
configuration. The strict seven-payload source link passes without an external
archive; image-A SRAM falls from 14,940 to the locked 14,716 bytes. The hardware
configuration matches stock exactly, while relocation-bearing context and
dispatch words differ. At this placement snapshot, the exception and IRQ
vector targets also differed. Image-A XIP
remains 10,280 bytes over its locked limit. Evidence:
`g2/evidence/codec-a-aout-sram-placement-20261110.json`.

**Codec image-A startup and exception placement (2026-11-10).** The reset,
BSS clear, system initializer, C trap handler, and architectural trap entry
now link at their stock SRAM addresses. The exception vector target at
`0x10023640` is the trap's branch back to its entry, as in the locked image.
The first 32 vector words match stock byte for byte. Reset matches 38/40
bytes; its call to `main` still differs because the source-linked function
is at a different address. The trap matches 75/80 bytes; the assembler
reuses a literal that stock duplicates. The IRQ vector still targets
`0x10025810` rather than `0x10025574`. The final full source gate compiled
4,877/4,877 enabled units without failures or duplicate strong symbols,
and all seven payloads linked strictly. Evidence:
`g2/evidence/codec-a-exception-vector-placement-20261110.json`.

**Codec image-A trap entry converted to C (2026-11-10).** Replaced the
standalone `resident_exception_entry.S` manifest unit with a naked C function
that retains the necessary C-SKY register-save and trap-stack instructions.
The source-linked codec A flat binary, SRAM, XIP, and BINH stage-1 outputs are
byte for byte unchanged. The final all-payload source gate compiled 4,877
enabled units and linked seven payloads without an external archive. Six
build-enabled assembler units remain in the G2 manifest. Evidence:
`g2/evidence/codec-a-trap-c-conversion-20261110.json`.

**Bootloader transitions converted to C (2026-11-10).** Replaced the vector
handoff and first-task transfer assembler units with naked C functions that
retain their required Thumb instructions. The handoff conversion preserves
the full bootloader binary. The first-task `.text` body remains byte-identical
at 32 bytes, while the compiler adds unwind coverage that changes one
`.ARM.exidx` byte in the linked bootloader. The final full G2 gate compiles
4,877 enabled units and strictly links all seven payloads. Four enabled
assembler units remain. Evidence:
`g2/evidence/boot-transfer-c-conversion-20261110.json`.

**All build-enabled G2 translation units now compile as C (2026-11-10).**
Converted the bootloader reset and stack entry, its fixed 24-byte ITCM helper
image, the SVC/first-task/PendSV exception entries, and Apollo-main's
CmBacktrace HardFault entry from standalone assembler units to naked C
functions with explicit architecture instructions. The reset/stack and ITCM
code bytes, the three exception bodies, and the HardFault body match their
prior linked forms. The manifest has 4,877 build-enabled `.c` units and no
build-enabled `.S` units; one upstream touch `.S` unit remains disabled and
unlinked. `sources-check`, the 4,877-unit full build, and the strict seven
payload links pass with zero compilation failures or duplicate strong symbols.
This is a C compilation milestone, not source completeness, byte identity,
or hardware qualification. Evidence:
`g2/evidence/g2-c-entry-source-gate-20261110.json`.

**Codec image-A vectors fully placed (2026-11-10).** The source linker now
pins the compact IRQ entry at `0x10025574` after pre-IRQ resident functions
and their source-owned literal data. All 64 vector words match the locked
firmware byte for byte. The 14,716-byte source SRAM image still fits the
locked span and its matching byte count rises from 2,655 to 2,857; most code
and data remain different. The XIP image is still 10,280 bytes over its
locked limit, and NPU command/weight source and full BINH A packaging remain
unresolved. The source linker now rejects a changed SRAM length or vector
hash. The strict seven-payload source link passes without an external
archive. Evidence: `g2/evidence/codec-a-full-vector-placement-20261110.json`.

- `./g2/make.sh sources-check`: 4,867 registered units, 4,527 source files,
  one documented not-built link helper.
- `tools/build/sources.py build --device g2 --out build/g2-current-20261110`:
  all 4,862 build-enabled units compiled, zero failed and zero duplicate strong
  symbols. The seven relocatable link groups composed. Full receipt:
  `build/g2-current-20261110/report.json` (SHA-256
  `deb032fb83f0d61c68a6fa26ac16d450ddc1fba6be584e700c83c72e3aa186ae`).
- Added `tools/build/link_g2_sources.py` and `make -C g2 source-link`. The
  linker checks that the compiled inputs have not changed, fails on link
  errors, and writes ELF and binary hashes. Six payloads link without an
  external binary archive: `build/g2-source-only-six-20261110/link-report.json`
  (SHA-256 `2d5e46c4c89343a513d20e6e491a4800d0f00d987167fde6b0ddf293040b92de`).
- Apollo main still imports Nordic `nrf_fuel_gauge` from an untracked `.a`.
  The default strict all-payload link therefore fails at this dependency.
  With the explicit `--allow-binary-fuel-gauge` baseline flag, all seven
  link with zero undefined references. Receipt:
  `build/g2-source-images-with-nordic-20261110/link-report.json` (SHA-256
  `9c099355ad6b46632a86c6bf457818685c5da46dc237a78c707159410b96652a`).
  Its seven binaries are byte-for-byte identical to the prior ad hoc final-link
  outputs made from this same build. A compact durable summary is in
  `g2/evidence/g2-source-link-20261110.json`.
- This is compilation and linkage evidence only. Ten manifest units are
  assembly; inline architecture instructions remain in C, source coverage
  is not frozen, and the physical Apollo-main boot failure remains unresolved.
  No new image was installed or marked hardware-ready.
- The freshly linked Apollo-main binary ran for 2 virtual seconds in the
  existing lenient Renode profile and emitted 56 HCI host packets, including
  advertising enable `010A200101`. The simulator has known gaps in real
  peripheral responses and timing; this result does not resolve the hardware
  boot failure. Log hash and run parameters are in the durable evidence record.

## 2026-11-10 — bootloader init-record table moved from assembly to C

- Replaced `startup/init_records.S` with read-only C descriptors in
  `startup/record_dispatch.c`. The dispatcher calls the same zero and expand
  adapters with the four stock descriptors in their original order. The table
  resides in ROM, so it is available before writable memory is initialized.
- `sources-check` passes: 4,866 registered units. The bootloader-only build
  compiled 224/224 units, composed without duplicate strong symbols, and
  linked a final ELF with zero undefined symbols.
- A Unicorn comparison of the old and new linked dispatcher functions
  captured identical adapter call kinds and descriptor words for all four
  records. The adapter bodies were intercepted, so this comparison does not
  itself verify downstream memory writes. Unicorn cannot run the M55 `LE`
  instruction in the zero adapter; a full memory comparison was not claimed.
  In Renode, both linked bootloaders ran for 2 virtual seconds through the
  same application and emitted an identical sequence of 56 HCI host packets,
  including advertising enable. These are simulator fixtures, not a physical
  boot proof. Evidence:
  `g2/evidence/boot-init-records-c-review-20261110.json`.
- The removed file was data-only assembly. Architecture entry and context
  assembly remain; this change does not establish an all-C bootloader.
