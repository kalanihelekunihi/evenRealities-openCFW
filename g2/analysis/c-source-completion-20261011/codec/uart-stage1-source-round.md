# UART stage-1 source round

The authenticated UART stage-1 image is `g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/uart_stage1.bin`, loaded at `0x10000000`, 10,240 bytes, SHA-256 `cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f`. Its Ghidra 12.1.4 retained census has 32 decompiled functions and 3,142 bytes of recognized function bodies.

Two new C units reconstruct eight bodies from native disassembly and decompilation:

| C source | Stock functions | Contract |
| --- | --- | --- |
| `uart_stage1_io.c` | `0x10000584` put, `0x100005a0` put_sync, `0x10000620` try_get, `0x10000640` get_char | Repeated stock literal `0x20002014` holds UART base; status is register word 5, TX/RX word 0. Product initializer for this SRAM pointer is still unowned. |
| `uart_stage1_pmu_bits.c` | `0x10000374`, `0x1000038c`, `0x100003a4`, `0x100003b0` | PMU register `0xa0010030`; setters preserve stock's two distinct volatile writes, clearing then setting their bit. |

Four additional bodies were reconstructed in the next pass: `uart_stage1_bringup.c` at `0x100005c4`, `uart_stage1_xip.c` at `0x100018c0` and `0x10001940`, and `uart_stage1_handshake.c` at `0x100006d8`. Bringup now owns the **runtime** write to SRAM UART base word `0x20002014`, selecting `0xa0100000` or `0xa0200000` from mode word `0x2000200c`; its preceding product-mode initializer remains unowned. The XIP bodies preserve byte transfer width and the ordered writes to `0xa2000000` registers and `0xa20000f4`, corroborated by native instructions. Handshake owns stock literal `"OK\0"` from `0x10001e5c`, sends `GET`, and reads UART response; its rail and delay lowers remain separately required.

`uart_stage1_rail.c` adds two further bodies at `0x1000046c` and `0x100004a4`: the clock-control sequence uses the stock signed `DIVS` by one million and an explicit typed lower for the unseeded `0x10000ea0` clock-rate getter; block-clear retains the otherwise-unused volatile reads of both peripheral blocks.

The experimental codec builder compiles these as a **separate loaded-stage candidate** under `uart_stage1_candidate`; it does not put them in the image-A application object. Fresh receipt: `g2/build/c-firmware/20261011/codec-stage1-rail-round/receipt.json`, candidate compilation PASS for six C units. The stage-1 coverage is 14 of 32 decompiled bodies. The other 18 decompiled stage-1 bodies, including reset `0x10000100`, PMU dispatch, UART configuration, beacon, and postamble remain. The reset pseudocode has incomplete `stub()` calls; direct disassembly resolves the CPU entry and dispatcher in the later pass below, while the call at `0x10002900` enters the distinct authenticated UART stage-2 image. The 10,240-byte stage image also contains literals, initialized data, and alignment outside the 3,142 recognized body bytes; no final source linker map exists.

This receipt proves target compilation of eight C bodies, not native execution equality or complete source for the loaded stage or full codec image.

## Direct native recovery after the initial census

`uart_stage1_delay.c` reconstructs the previously unseeded `0x100003bc` 64-bit timer-to-milliseconds body and seeded delay `0x100003fc`. It uses source-owned unsigned division instead of an opaque helper at `0x100065e4`. `uart_stage1_startup_dispatch.c` reconstructs unseeded `0x100001bc` and seeded stored-ID read `0x100002bc`, retaining typed lower calls for the hardware, initialized-data, runtime and application continuations. `uart_stage1_reset.c` reconstructs the `0x10000100` CPU control-register and stack setup as a naked C function with C-SKY assembly. Its compiled instruction listing contains the same control-register operations and linked call relocations; instruction bytes/layout are not claimed equal.

Fresh builder receipt: `g2/build/c-firmware/20261011/codec-stage1-reset-round/receipt.json`, stage-1 candidate compile PASS. It covers **17/32 retained seeded bodies plus two directly recovered unseeded bodies**. The raw reset call at `0x10002900` lies beyond the stage-1 image (`0x10000000..0x100027ff`) but inside the authenticated UART stage-2 image (`0x10002800` base, 27,964 bytes); native instructions identify its reset entry, whose source is a distinct stage-2 obligation. The hardware/data/runtime initializers called by `0x100001bc` still need separate source bodies. The clock-rate getter at `0x10000ea0` and PMU dispatch rely on the `0x20002018` product descriptor table; the table's source initializer and relocation map are not yet attributable.

## Subsequent C bodies

`uart_stage1_pmu_desc.c` reconstructs the 26-entry descriptor lookup `0x10000780` with typed six-word output; the backing table at `0x20002018` is still a product data requirement. `uart_stage1_config.c` reconstructs UART register configuration `0x10000c9c` from a caller-provided configuration and MMIO bases `0xa0005000/5080`. `uart_stage1_postamble.c` reconstructs `0x10001d9c`, retaining its volatile peripheral polling and zero-valued PMU dispatch call. `uart_stage1_pmu_bit_modify.c` reconstructs `0x10000840`. `uart_stage1_division.c` translates the two stock software shift/subtract bodies `0x1000013c` and `0x10000180`; exceptional divisor behavior still needs native execution qualification. `uart_stage1_beacon.c` reconstructs baud setup `0x100004d0`, correcting the decompiler's invalid null comparison to native `uart_base == 0xa0100000`; clock-rate getter remains a typed lower. `uart_stage1_announce.c` reconstructs `0x1000065c`, including the native `ready` output and typed transfer lower at `0x10001bf8`.

Fresh receipt `g2/build/c-firmware/20261011/codec-stage1-announce-round/receipt.json` passes compilation. Coverage is **25/32 retained seeded bodies plus two directly recovered unseeded bodies**. Seven seeded labels remain, but `0x10000eb8` is a false Ghidra split inside the unseeded `0x10000ea0` clock-rate function. Six actual seeded bodies remain: trap loops `0x10000130`, stock empty clear-BSS `0x10000138`, three substantial PMU rail bodies `0x10000860`, `0x10000a30`, `0x10000b90`, PMU dispatch `0x10000d98`. PMU dispatch and the clock-rate body depend on jump tables and the unowned product descriptor data at `0x20002018`; they cannot be accurately replaced by generic register writes. This candidate has no C-SKY runtime equality receipt, complete initialized data, or final stage image link.

## Transfer, minimal startup, rail-C, and PMU data continuation

Native stage-1 instructions support `uart_stage1_transfer.c` at `0x10001bf8`, including the 4095-byte chunk descriptor split, and `uart_stage1_minimal_stock.c` at `0x10000130` and `0x10000138`. The latter compiles the stock trap loop and the stock empty clear-BSS return, respectively; it does not claim to initialize absent memory. `uart_stage1_railc.c` reconstructs the third rail body at `0x10000b90`. The stage-2 reset entry called at stage-1 address `0x1000011e` is separately compiled from authenticated UART stage-2 instructions as `uart_stage2_reset.c`; stage 2 begins at `0x10002800`, so `0x10002900` is its reset entry.

The initialized image contains a 26-entry PMU descriptor table at file offset `0x2018`, referenced at SRAM address `0x20002018`, plus 72 bytes of auxiliary fields at file offset `0x2228`, referenced at `0x20002228`. `uart_stage1_pmu_data.c` expresses all entries and pointer relationships as typed C initializers. The isolated linker script `uart_stage1_pmu_data.ld` fixes those two runtime addresses. A pinned C-SKY compile, link, and section extraction reproduced all **416 table bytes and 72 auxiliary bytes exactly** against the authenticated stage-1 image; SHA-256 of the extracted sections is `1f02d1a4648bb86242a84241d19a8ee959a2d8e66284bcb87ed8d7f80158dcc4` and `83491e2e7694b70e2ca5b0b46961758b63c801a50ab33b8f152b7a34c71dc293`. This proves these two data sections at the selected addresses, not the loader's complete ROM-to-SRAM copy scheme.

Fresh isolated builder receipt: `g2/build/c-firmware/20261011/codec-stage1-pmu-data-round/receipt.json`, with **20 stage-1 C units compiled**, covering **28/32 seeded labels plus three direct unseeded bodies**. Seed `0x10000eb8` is a false split within the still missing `0x10000ea0` clock-rate body. The three actual seeded bodies still absent are PMU rail-A `0x10000860`, rail-B `0x10000a30`, and dispatch `0x10000d98`. Remaining whole-stage obligations include that clock-rate body, other initialized data and its load map, final startup/linker composition, and native behavioral qualification. The selected image-A stage-2 application graph and the stage-1 candidate remain separate; neither is a complete codec image source.

`uart_stage1_railb.c` adds the retained `0x10000a30` field-programming control flow, including the auxiliary register's field width, power/gate sequencing, and ordered latch writes. Fresh `g2/build/c-firmware/20261011/codec-stage1-railb-round/receipt.json` passes target compilation for **21 stage-1 C units**, **29/32 seeded labels plus three direct unseeded bodies**. Rail-B remains a C candidate pending a native behavioral oracle; it does not inherit the PMU table's exact-byte proof. The two actual seeded bodies still without C are rail-A `0x10000860` and PMU dispatch `0x10000d98`. The unseeded `0x10000ea0` clock-rate function remains, with `0x10000eb8` a false split inside it.

## Rail-A and PMU dispatch body pass

`uart_stage1_raila.c` expresses the `0x10000860` selector validation, descriptor gate writes, and the special peer test for selectors 7/8. Native offsets `0x25/26`, `0x75/76`, and `0x85/86` resolve to status/gate fields of descriptor entries 2, 7, and 8 in the exact-byte PMU table. `uart_stage1_pmu_dispatch.c` expresses the two authenticated native jump tables at `0x10001e60` and `0x10001ea8` as explicit switch cases, retaining the first power-gate write and second selector-dependent status-bit write. Fresh `g2/build/c-firmware/20261011/codec-stage1-raila-dispatch-round/receipt.json` passes target compilation for **23 C units** and **31/32 Ghidra seeded labels plus three direct unseeded bodies**. The one remaining seed `0x10000eb8` is a false split within the actual unseeded `0x10000ea0` clock-rate function. Rail-A and dispatch remain compiled C candidates, without native execution equivalence evidence.

The clock-rate body spans native `0x10000ea0..0x1000107f`. It uses a third jump table at `0x10001ef4`, selector-specific auxiliary fields, PMU status, UART PLL register words at `0xa0005000`, range checks, and a 64-bit calibration multiply. Its complete arithmetic and branch behavior remains the single stage-1 code-body reduction gap. Separately, no final stage-1 load map or complete initialized-data ownership is yet proven.

`uart_stage1_clock_rate.c` now expresses that entire native span as a C candidate: selector remapping, PMU gates, PLL mode/divider/range paths, calibration multiply, and auxiliary divider. It retains the target `divu` instruction for undefined zero-divisor hardware behavior. Fresh `g2/build/c-firmware/20261011/codec-stage1-clock-fullbody-round/receipt.json` passes compilation for **24 stage-1 C units**, all **31 actual Ghidra-seeded bodies** plus **four directly recovered unseeded bodies**. The nominal 32nd seed `0x10000eb8` is internal to the clock-rate body and is not a separate function. This is C body census closure only. Rail-A, rail-B, dispatch, and clock-rate still need native runtime or instruction-level qualification; the register source, arithmetic mode choices, and 64-bit rounding of clock-rate are material risks. Stage-1 final source/data/layout ownership and whole codec image coverage remain incomplete.

## Stage-2 reset bridge

`uart_stage2_reset_children.c` now supplies the two direct stage-2 reset callees at `0x100052b0` and `0x100054e0`, plus the latter's short child at `0x100054ec`. Their calls to native `0x10002a3c`, `0x10004408`, `0x10004428`, `0x1000547c`, and `0x10005a4c` are explicit typed imports and are not silently substituted. Together with `uart_stage2_reset.c` at `0x10002900`, these form a separate loaded-stage reset bridge. Fresh `g2/build/c-firmware/20261011/codec-stage2-reset-bridge-round/receipt.json` compiles both stage-2 C units and all 24 stage-1 units. The retained stage-2 Ghidra census contains 96 function labels and 11,498 recognized body bytes; these three newly reduced unseeded children do not close that larger application. The first child `0x10005100` remains a substantial boot-control body with CPU control registers, a readiness call at `0x10004fb0`, NVIC programming, and continuation to `0x100029a0`. Final stage-2 source/data/layout and native runtime qualification remain open.

`uart_stage2_init_clock.c` now reduces native `0x10005100` and its direct BSS clear child `0x1000292c` to C with target CPU-control instructions, four ordered NVIC pairs, and typed lower calls at `0x100052c4`, `0x10004fb0`, and `0x100029a0`. `uart_stage2_small.c` reduces seeded `0x10002a3c` to four analog-register writes and seeded `0x100029c0` to its address mask rule. Fresh `g2/build/c-firmware/20261011/codec-stage2-small-bss-round/receipt.json` compiles **four stage-2 C units** alongside the 24 stage-1 C units. Stage-2 currently has **2 of 96 seeded functions** represented by source in this candidate, plus **six direct unseeded reset-path bodies** (`0x10002900`, `0x1000292c`, `0x10005100`, `0x100052b0`, `0x100054e0`, `0x100054ec`). At least 94 seeded functions remain unreduced; other unseeded functions also exist. Direct reset descendants still missing include `0x100052c4`, `0x10004fb0`, `0x100029a0`, seeded `0x10004408`, `0x10004428`, `0x1000547c`, and `0x10005a4c`. This is a quantified source checkpoint, not a complete stage-2 image.

The next direct pass adds unseeded `0x100029a0` interrupt setup and seeded `0x10004408` analog voltage setter to `uart_stage2_small.c`. The interrupt path retains typed lower contracts for `0x10003174`, `0x100031b4`, and `0x10003194`; the setter preserves its native `0xffffffff` sentinel and byte truncation. Fresh `g2/build/c-firmware/20261011/codec-stage2-interrupt-ldo-round/receipt.json` passes target compilation. Stage-2 source coverage is now **3/96 seeded bodies plus seven direct unseeded bodies**. The direct child `0x10004428` reads an uninitialized stack byte before modifying bits 0..4; its ambient high-bit contract requires native ABI qualification and is not synthesized as a deterministic C variable.

Native callsite inspection finds `0x10004428` is called by `0x100052b0` with `r0=0`; its new four-byte stack slot is not initialized before the first byte load. Its downstream case-8 call at `0x10004db8` reads the full word from that slot. `uart_stage2_small.c` therefore preserves the exact stack-byte read, bit insertion, call, and return sequence as a naked C function with inline C-SKY assembly; the ambient other bytes remain a genuine runtime input, not synthesized zeros. The same source adds unseeded revision getter `0x10004f6c` and readiness gate `0x10004fb0`. `uart_stage2_app_setup.c` reconstructs unseeded `0x1000547c` from direct native branch/call instructions, retaining lower calls by address and product config at SRAM `0x20009084` as an input. Fresh `g2/build/c-firmware/20261011/codec-stage2-setup-round/receipt.json` compiles **five stage-2 C units**, covering **3/96 seeded bodies plus eleven direct unseeded bodies**. The `0x100052c4` clock subinitializer and `0x10005a4c` main application remain substantial reset descendants, with further lowers still open.

`uart_stage2_clock_subinit.c` now covers the full outer `0x100052c4..0x1000542b` native sequence: revision-selected 10-entry SRAM table (`0x2000949c` or `0x200094ec`), ordered rail/gate/field calls, and final 26-selector dispatch loop. It retains the table contents as product input, with no synthetic values. The same unit reduces `0x10004fd0` to its dispatch and PMU bit read. `uart_stage2_app_setup.c` reduces `0x10005a4c` to its SRAM mode branch, optional report, two preparation calls, and launch call. Fresh `g2/build/c-firmware/20261011/codec-stage2-reset-descendants-round/receipt.json` compiles **six stage-2 C units** and all 24 stage-1 units. Stage-2 source coverage is **3/96 seeded bodies plus fourteen directly recovered unseeded bodies**. The 93 still-unreduced seeded labels include the `0x10004428` child's `0x10004db8` dispatcher and the stage-2 application's helpers; other unseeded bodies remain. The two 80-byte SRAM clock tables, other product data, final load/link layout, and runtime qualification remain open.

`uart_stage2_request_dispatch.c` reduces seeded `0x10004db8` across all ten authenticated jump-table targets at `0x1000820c`, including its analog MMIO, PMU, and SRAM writes. Case 8 consumes the ambient four-byte stack word passed by `0x10004428`; no value is fabricated. `uart_stage2_app_setup.c` also supplies direct native wrappers `0x10005c64`, `0x10005c6c`, and `0x10005c74`. Seeded `0x100061a4` is represented by `uart_stage2_console.c` as a C varargs buffer/formatter/output loop, with the formatter `0x10006fa4` and character sink `0x10002a84` retained as typed lower contracts. Fresh `g2/build/c-firmware/20261011/codec-stage2-console-round/receipt.json` passes target compilation for **eight stage-2 C units**, **5/96 seeded bodies plus seventeen direct unseeded bodies**. Native ABI/behavioral equality is still open for the dispatcher and varargs path. At least 91 seeded bodies and further unseeded bodies remain; source-owned product tables, initialized memory, and final layout remain open.

`uart_stage2_uart.c` reduces four seeded console descendants: `0x10002a74`, `0x10002a84`, `0x10002ec8`, and `0x10002ee8`. The UART descriptor array at SRAM `0x2000908c` and active port at `0x20009840` remain actual input data; the two byte primitives preserve native status polling and LF-to-CRLF sequencing. `uart_stage2_console.c` also reduces seeded `0x10006fa4`, an eight-byte call-through wrapper to formatter engine `0x10006b40`. Fresh `g2/build/c-firmware/20261011/codec-stage2-format-wrapper-round/receipt.json` passes target compilation for **nine stage-2 C units**, **10/96 seeded bodies plus seventeen direct unseeded bodies**. The formatter engine is a distinct 456-byte retained body with multiple native jump tables and is not replaced by an unqualified libc formatter. At least 86 seeded bodies remain, including that engine; varargs ABI equality, product data, source linker composition, and runtime behavior are still open.

`uart_stage2_format_engine.c` now expresses the outer 456-byte formatter engine `0x10006b40` as a C candidate. Its native jump tables at `0x10008b88`, `0x10008d1c`, `0x10008bcc`, and `0x10008e6c` resolve the five flag characters and conversion set `% c d i n o p s u x X`; width, precision, length, string/character padding, numeric argument loading, and invalid-specifier fallback are expressed in C. The same unit supplies the 40-byte seeded `0x10006350` bounded string length body. `uart_stage2_format_number.c` supplies seeded `0x1000691c` numeric output control flow, including sign, alternate prefixes, digit order, precision, and padding; its arithmetic is source-owned bounded bitwise division instead of an opaque 64-bit runtime import. A host bounded smoke check produced expected strings for decimal, width/zero pad, signed `-1`, lowercase hex, prefixed hex, and alternate octal zero. Fresh `g2/build/c-firmware/20261011/codec-stage2-format-number-round/receipt.json` passes target compilation for **eleven stage-2 C units**, **13/96 seeded bodies plus seventeen direct unseeded bodies**. These are C candidates: varargs layout, all formatter branch cases, numeric native equality, and original decimal helper `0x10006774` still need qualification/source ownership. At least 83 seeded bodies and other unseeded bodies remain, as do product data and final image layout.

`uart_stage2_format_number.c` now also supplies seeded decimal reverse-digit helper `0x10006774` and calls it on the decimal path, preserving the original call graph. It uses the same source-owned bitwise quotient/remainder core, so the emitted decimal digits and pointer advancement are defined without opaque library division. Fresh `g2/build/c-firmware/20261011/codec-stage2-decimal-round/receipt.json` passes the target compilation of **eleven stage-2 C units** and raises the census to **14/96 seeded bodies plus seventeen direct unseeded bodies**. Numerical equivalence to the optimized stock divider remains unproven by target execution; at least 82 seeded bodies and further unseeded functions remain.

The numeric source now also owns seeded `0x100065e4`, the 64-by-32 quotient/remainder helper, with a bounded bitwise division path and target `divu` for the architectural zero-divisor case. The decimal helper calls it; fresh `g2/build/c-firmware/20261011/codec-stage2-divide-round/receipt.json` passes the target build. `uart_stage2_cache.c` reduces two seeded reset descendants, `0x10003194` and `0x100031b4`, and direct unseeded `0x10003174`, retaining volatile cache-control reads and four `sync` instructions in each seeded body. Fresh `g2/build/c-firmware/20261011/codec-stage2-cache-round/receipt.json` passes compilation for **twelve stage-2 C units**, **17/96 seeded bodies plus eighteen direct unseeded bodies**. At least 79 seeded bodies remain; the stage-2 reset path still has product configuration, other hardware children, and full initialized-data/link ownership open.

`uart_stage2_small.c` adds direct unseeded reset descendants `0x100029d4` (PMU boot state to SRAM configuration), `0x10002a1c` (revision-selected baud input), and `0x10002a50` (active port write plus configuration call). `uart_stage2_clock_subinit.c` adds their direct `0x10004fe8` alternate revision bit getter. `uart_stage2_uart.c` now also reduces seeded `0x10002e28` UART configuration: port validation, clock/rail call, native one-million rounding threshold, and writes to the actual SRAM port descriptor, with native `0x10004b50` rate and `0x10002c38` apply bodies as typed lowers. Fresh `g2/build/c-firmware/20261011/codec-stage2-uart-config-round/receipt.json` passes target compilation for **twelve stage-2 C units**, **18/96 seeded bodies plus twenty-two direct unseeded bodies**. At least 78 seeded bodies and additional unseeded functions remain; product SRAM contents and final source layout are not inferred from these consumers.
# Stage-2 PMU data and command lookup continuation (2026-10-11)

The authenticated UART stage-2 image has a 26-entry PMU descriptor table at
file offset `0x6ab4`, loaded at RAM `0x200092b4`, and 72 bytes of auxiliary
register fields at file offset `0x6c54`, loaded at `0x20009454`. The source
initializer `uart_stage2_pmu_data.c` expresses IDs, rails, gates, typed
auxiliary fields, and pointer relocations. Isolated linking with
`uart_stage2_pmu_data.ld` produces exact stock bytes: 416/416 table bytes
(SHA-256 `305efbc2fb402190de582cd11a561e0f9b689a6a3ed8f68ac999e4ec754ed659`)
and 72/72 auxiliary bytes (SHA-256
`83491e2e7694b70e2ca5b0b46961758b63c801a50ab33b8f152b7a34c71dc293`).
This is initialized semantic data and relocation proof for two sections,
not final stage-2 layout or reset-copy proof.

The typed C unit `uart_stage2_command_lookup.c` reduces four retained seeded
stage-2 bodies: `0x10006294` bounded comparison, `0x100062e0` character
search, `0x100062fc` string length, and `0x10005e74` exact or unique-prefix
lookup over five-word command descriptors. The retained pseudocode provides
the descriptor stride, dot truncation, and ambiguity behavior. This raises
the stage-2 source candidate to 24/96 seeded functions plus 22 direct
unseeded bodies. Target execution equality and varargs formatter behavior
remain unqualified; C compilation is a separate receipt.

The next UART/shell/callback candidate units reduce 11 more seeded bodies:
`0x10002ea4`, `0x10002f20`, `0x10006170`, `0x10006184`,
`0x10006270`, `0x1000627a`, `0x10003418`, `0x1000342c`,
`0x10003444`, `0x10002fb4`, and `0x10005a7c`, plus the direct
unseeded `0x10002a98` shell RX-ready wrapper. The UART descriptor base
`0x2000908c`, active-port word `0x20009840`, and interrupt-poll state
`0x2000997c` are original data references. The interrupt state address
comes from the stock literal at `0x10005aa4`. Callback offsets and
missing-result values are retained; containing descriptor initialization
and native execution equality remain open. Candidate source coverage is
35/96 seeded functions plus 23 direct unseeded bodies. The fresh
`codec-stage2-control-round/receipt.json` reports all 19 stage-2 units
compiled, and the whole codec candidate compilation passed; source-complete
remains false.

The next native block adds cache-line command bodies `0x100031d8`,
`0x10003274`, and `0x10003310`. Their three retained literal words at
`0x10003270`, `0x1000330c`, and `0x100033a8` all resolve to
`0xe000f000`; each body writes 16-byte line commands to `0xe000f004`
with mode 2, 8, or 10. `0x10003458` owns optional address adjustment
and signed callback status. `0x10005ef0` owns command help dispatch,
sorting, unique-prefix lookup, interruption, and output. Its exact stock
format strings are at `0x100085a8`, `0x1000859c`, and `0x10008590`.
These five seeded bodies bring the candidate to 40/96 seeded plus 23
direct unseeded functions. Native MMIO traces, callback execution, target
varargs formatting, complete command descriptor data, and final linker
layout remain separate qualification tasks.

The fresh `codec-stage2-command-help-round/receipt.json` compiled all 21
stage-2 source units with the pinned C-SKY compiler. A relocatable link of
all stage-2 objects succeeded, proving no duplicate global definitions.
It retains 16 typed lower imports: `apply_table_entry_45ec`,
`clock_rate_4b50`, `configure_61e4`, `field_493c`, `gate_47dc`,
`prepare_lower_5bf8`, `prepare_lower_618c`, `rail_460c`,
`report_lower_5b28`, `runtime_step_4408`, `runtime_step_4428`,
`setup_30b4`, `setup_4388`, `setup_4db0`, `setup_5434`, and
`uart_apply_2c38`. These are source gaps or bound hardware/product
contracts, not evidence of a complete linked firmware image.

The next stage-2 IRQ/PMU round traced native instructions and exact copies
from the stage-1 image. `0x10003110` reads CPU control then clears IE;
`0x1000311c` restores it. Source now owns VIC operations `0x100030cc`
and `0x100030e8`, UART start `0x10002f34`, UART apply `0x10002c38`,
and clock rate `0x10004b50`. The UART fractional divider is represented
as the native binary64 sequence `(remainder / divisor) * 16.0 + 0.5`
followed by unsigned conversion. Compiler and target numeric behavior
still require a bounded runtime oracle. The clock-rate native jump table
at `0x100081c0` confirms 19 selectors, including selector 25 remapped
to descriptor 10.

Stage-2 rail-A `0x1000460c` shares 462 of 464 code bytes with stage-1
`0x10000860`; the only two changed bytes are the relocated PMU table
address. Rail-B `0x100047dc` shares all 352 bytes with stage-1
`0x10000a30`; rail-C `0x1000493c` shares all 268 code bytes with
stage-1 `0x10000b90`. Their source-reduced stage-1 C algorithms were
adapted to the exact stage-2 table and descriptor helper. Native direct
`0x100045ec` modifies the bit at `0xa001008c`.

The UART IRQ chain now includes `0x100041b8` resource allocation,
`0x1000432c` callback table write, `0x10003024` mode-block setup,
`0x10002f98` completion callback, direct `0x100030b4` VIC restore,
`0x10004340` hardware setup, `0x10004020` descriptor programming, and
`0x10003f1c` chained six-word transfer descriptors. The raw call to
`0x10003024` preserves entry r1/r2 as buffer and transfer byte count.
The completion callback revealed that the word at descriptor `+0x58`
is a function pointer and `+0x5c` its argument. The C candidate now
covers 53/96 seeded bodies plus 29 direct unseeded bodies. Build and
runtime qualification remain separate.


Subsequent native reduction adds the IRQ release/service, timer setup,
pin boot/configuration, package-pool, console string, and shell helper
families. The pin boot table at `0x100082e0` is an exact 26/26 semantic
byte match and the default pin pairs at `0x1000825d` are exact 62/62;
these data matches do not establish runtime equivalence. The stock
stage-2 six-entry shell descriptor table at `0x1000900c` is now C data:
each name, argument limit, state mask, callback relocation, and usage
string was decoded from the authenticated image. Its dispatcher
`0x10006018`, reboot callback `0x10005a40`, and watchdog reset lower
`0x10004508` are C source, including the ordered MMIO writes and
infinite reset wait. Callback bodies for flash/help/serialdown/wdt
remain separate source obligations. The current body ledger is 53/96
retained seeded functions plus 51 direct unseeded functions; compiler
receipt and relocatable-link qualification for the newest units follow
in their named `g2/build/c-firmware/20261011/codec-stage2-*` rounds.
This is a partial source candidate, not a full codec image.

The next native command pass adds the stock help callback adapter
`0x100054f8`, watchdog command `0x10005978` (`init`, `ping`, `write`,
`read`), and watchdog interrupt callback `0x10005958`; the one-store
watchdog reload `0x100044fc` is also C. The watchdog command retains
real typed lower contracts for numeric parsing at `0x1000654c` and
configuration at `0x10004478`. Callback data at RAM `0x20009978` and
MMIO `0xa001002c`/`0xa0010030` are explicit. With those bodies, the
candidate owns 53/96 seeded plus 52 direct unseeded stage-2 functions.
The direct unseeded count includes separately verified native function
starts outside the retained 96-function Ghidra seed census.

Watchdog configuration `0x10004478` and IRQ trampoline `0x10004454`
are now native-derived C as well. Configuration preserves the stock
16-iteration signed divider/unsigned comparator, 0xa070 control stores,
callback slot at RAM `0x20009960`, and IRQ 11 registration; the
trampoline reads status register `0xa0700014` after calling the saved
callback. This brings the direct unseeded stage-2 body ledger to 54;
no device-level watchdog behavior is claimed.

The fresh `codec-stage2-watchdog-chain-final/receipt.json` compiled
52 separate stage-2 C units with the pinned C-SKY compiler
(`candidate_compilation_passed: true`, `source_complete: false`). A
relocatable link of all 52 stage-2 objects passed with no duplicate
symbols. Its 12 unresolved lower symbols are five binary64 compiler
helpers (`__adddf3`, `__divdf3`, `__fixunsdfsi`, `__floatunsidf`,
`__muldf3`) and seven application bodies (`flash_552c`,
`irq_handler_2aa8`, `parse_unsigned_654c`, `pool_allocate_6fac`,
`prepare_lower_5bf8`, `report_lower_5b28`, `serialdown_5628`). This
link establishes source composition only. Stage-2 native runtime
behavior, DSP resident application coverage, initialized semantic data
and final image layout remain open.

The parser/pool/UART ISR round reduces three additional direct native
bodies: numeric parser `0x1000654c`, 20,884-byte package allocator
initializer `0x10006fac`, and UART ISR `0x10002aa8`. The parser source
tracks the stock character-class table at `0x10008a88`, its base-0
prefix decisions, unsigned wraparound, and end-pointer behavior. A
1,602-case bounded host-C versus instruction-derived native-table model
had zero mismatches for bases 0, 2, 8, 10, 16, and 36; receipt:
`stage2-parser-receipt.json`. It is not C-SKY runtime execution. The
allocator preserves native alignment, minimum size, 1,043 free-list
heads, bin index mapping, and sorted insertion. The UART ISR preserves
status bit branches, descriptor callback offsets, volatile RX/TX loops,
remaining-count updates, and completion callbacks. Hardware execution
and stock-byte equality remain unqualified.

`codec-stage2-uart-isr-round/receipt.json` compiled 55 stage-2 C units;
all units relocatably linked without duplicate definitions. The nine
remaining stage-2 imports are five binary64 compiler helpers and four
application bodies (`flash_552c`, `prepare_lower_5bf8`,
`report_lower_5b28`, `serialdown_5628`). Actual retained seeded body
coverage remains 53/96: **43 seeded bodies are uncovered**, regardless
of this import count. The direct native body count is 57. Resident DSP
application bodies, semantic initialized data, runtime behavior, and
final image layout remain open.

The shell/flash/download continuation converts native command-list
`0x10005b28`, REPL `0x10005bf8`, interactive line editor
`0x10005d1c`, backspace `0x10005c84`, bounded copy `0x100064dc`,
and read wrapper `0x10005e60` into C. The stock shell stack places
initialized status byte zero immediately before the text buffer, which
resolves the apparent ambient previous-byte read at the first quote.
The `mvcv` and `bhz` conditions in the REPL were checked against the
retained C-SKY QEMU decoder; the source uses `1 - compare` and signed
`> 0` respectively. Native flash command `0x1000552c`, serial flash
download `0x10005628`, completion flag callback `0x100055e0`, and
probe `0x100033ac` are source candidates. The download has alternating
L/R receive buffers, stock protocol tokens, checksum, flash callback
writes, and typed hardware/product contracts. Its runtime timing and
full native equality remain unqualified.

Five additional retained seeded utility bodies now have C candidates:
64-bit tick `0x10004da4`, pool search `0x100060b0`, aligned malloc
`0x10006134`, aligned free `0x10006154`, and free wrapper `0x10006168`.
The pool core at `0x100070ac` and coalescing free at `0x10007240`
are transcribed from retained pseudocode with native size/bin constants;
these are risky candidate algorithms pending execution oracle. The
stock CRC body `0x100066b8` uses a source-generated IEEE reflected
polynomial table. All 1,024 generated table bytes match the original
initializer at `0x10008688` (SHA-256
`12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86`),
and 172 bounded host-source cases match zlib CRC32. Receipt:
`stage2-crc-receipt.json`. This data/content proof does not prove final
placement or C-SKY runtime.

The fresh `codec-stage2-allocator-core-round/receipt.json` compiled
69 separate stage-2 C units with the pinned C-SKY compiler. A fresh
relocatable link of every stage-2 object passed with **zero application
imports**. Its only five undefined symbols are compiler binary64
helpers `__adddf3`, `__divdf3`, `__fixunsdfsi`, `__floatunsidf`, and
`__muldf3`. This is source composition, not full stage-2 or resident
coverage. The body ledger at this checkpoint is 65/96 retained seeded
stage-2 functions plus 66 separately native-derived unseeded bodies;
**31 retained seeded bodies remain uncovered**. The full codec image
also requires resident DSP application source, complete semantic data,
linker/startup layout, and native runtime qualification.

A later exact-address symbol crosswalk supersedes the preceding manual
65/96 estimate: the linked stage-2 object defines address-suffixed C
symbols for **70/96** retained seed entries, leaving **26 unmapped**.
The finite unmapped list and census hash are in
`stage2-seeded-crosswalk.json`. This is stronger source attribution
than the manual count but still does not establish native behavior,
resident application coverage, or final image layout.

The next pinned-target codec build at
`codec-stage2-spi-erase-shift-round/receipt.json` compiled **73 separate
stage-2 C units**. Linking every `uart_stage2_*.o` as a relocatable unit
succeeded; its only undefined names were the same five compiler binary64
helpers. An exact-address symbol recensus found **81/96** retained seed
entries represented, leaving 15 symbol gaps at that snapshot. The
`0x1000452c` PMU lookup is already implemented semantically under the
nonaddress `gx8002_uart_stage2_pmu_fill_desc` name and is therefore an
attribution binding, not a proved absent C body. Other gaps require
body/ABI checks, with the soft-FP chain a prominent remaining group.

Subsequent stage-2 C candidates add stock `0x100038fc` SPI page-bounded
programming through the source-declared descriptor callback at +0x18;
`0x10007d2c` binary64 unpacking into five software-FP words;
`0x10007e10` internal five-word comparison; and `0x10007a48` four-word
compare entry. All four pass pinned C-SKY target syntax compilation. The
native `zext r3,r3,14,4` instruction at `0x10007d36` confirms that the
unpacker extracts 11 exponent bits despite an ambiguous Ghidra mask
rendering. These software-FP candidates still need bounded native
execution equality. Page-programming still needs callback and hardware
qualification. Their full image build is tracked separately from the
81/96 linked snapshot, and full codec source/data/layout remains open.

The final `codec-stage2-fp-compare-round/receipt.json` compiles **77
stage-2 C units** with the pinned C-SKY target compiler. An independent
`ld -r` over all 77 objects passed; only the same five compiler binary64
helpers remain undefined. Its defined-symbol crosswalk is **85/96**
retained seeded entries, leaving 11 address-suffix gaps:
`0x10007400`, `0x10007730`, `0x10007b9c`, `0x10007930`,
`0x1000452c` (semantic body already present under another name),
`0x10007a88`, `0x10007af8`, `0x100042e8`, `0x100073c8`,
`0x100076f4`, and `0x100076c4`. The earlier **43 uncovered seeded**
count was superseded by this exact-symbol recensus; the remaining
unseeded attribution census, resident DSP application, initialized data, reset and
linker layout, and native behavioral qualification are independent
remaining work. This is a C candidate compilation receipt, not whole
codec image completion.

Direct native disassembly refined the SPI candidates after the
preceding compile receipts: `0x10003936` loads the **address**
`0x200091c4`, and `0x1000393e` calls through its +`0x18` callback;
`0x10003b50` likewise uses that SRAM descriptor as the direct base,
not a pointer stored at its first word. `0x10003b7a` extracts all low
16 address bits before the 64 KiB erase path, so the C alignment mask
is `0xffff`. The source now preserves those address and branch facts.
Prior compilation remains valid only as syntax evidence for the earlier
revision; the corrected source requires the later fresh receipt and
still has no native runtime equality claim.

Direct stock instructions resolve seeded `0x100042e8`'s misleading
zero-argument decompilation: it reads the fifth caller stack word,
saves r3 as slot, calls already-owned `0x10004020`, returns `-1` only
on that child result, flushes `state[slot+0xda]` for `0x1a0` bytes,
and writes `0x101 << slot` to controller root +`0x3a0`.
`uart_stage2_irq_hardware_alt.c` now supplies the actual five-argument
C body; pinned C-SKY syntax compilation passes. Native runtime equality
and its entry-caller ABI remain to qualify, but no value is fabricated.

The `0x10007b9c` native packer returns a binary64 pair in r0/r1,
not the one-word return inferred by Ghidra. `uart_stage2_fp_pack.c`
expresses its five-word class/sign/exponent/limb format with nearest-even
rounding, subnormal shifting, overflow, zero, infinity, and NaN output.
A bounded 10,006 finite-value host unpack/pack roundtrip first exposed
three mismatches. Direct `0x10007db6..0x10007dbd` instructions show an
implicit `0x10000000` high-limb bit for normal inputs omitted by Ghidra;
the unpack C now includes it. Repeating the identical corpus gives **zero
mismatches**. This is an internal IEEE representation check, not
stock C-SKY execution equality; NaN payload behavior and other FP
arithmetic remain separately unqualified.

The reproducible bounded host check is
`verify_stage2_fp_roundtrip.py`, with result
`stage2-fp-roundtrip-receipt.json` (10,006 finite cases, zero mismatches).
It compiles only source-owned unpack/pack code in a temporary host
library and does not include stock executable bytes.

Seeded `0x10007af8` also now has a C candidate: its native
leading-zero normalization maps uint32 input to internal significand
bit 60, then calls `0x10007b9c`. Target syntax compilation passes.
The durable host receipt covers 10,007 deterministic uint32 values
against independently produced IEEE binary64 bit patterns with zero
mismatches, alongside the 10,006 finite unpack/pack roundtrips.
Stock C-SKY runtime equality remains open.

The 706-byte retained soft-FP add/sub body `0x10007400` now has a
source C candidate in `uart_stage2_fp_add_internal.c`. It returns the
selected five-word internal object, preserves NaN/infinity/zero class
selection, aligns with sticky bits, adds or subtracts signed limbs,
and normalizes before `0x10007b9c` packing. Native literal at
`0x1000772c` resolves to `0x10008ff8`, a 20-byte zero-class object;
the source expresses those five semantic zero words. Pinned C-SKY
target syntax compilation passes. The durable host corpus additionally
checks **19,976 finite binary64 operand pairs** through unpack, add,
and pack against independent host IEEE addition, with zero mismatches.
This does not establish native stock instruction equality or behavior
for NaN payloads and unusual internal input states.

The native binary64 entry wrappers `0x100076c4` and `0x100076f4`
are now represented by C four-word input/two-word return functions;
subtraction toggles the second operand's internal sign before the
source-owned `0x10007400` add. The host corpus checks each wrapper on
19,976 finite pairs against independent IEEE addition/subtraction,
with zero mismatches. Their target syntax compilation passes.

Direct `0x100073c8` instructions show a comparison against
`0x41e0000000000000` (2^31), a direct signed conversion below that
threshold, and a subtraction/conversion plus `0x80000000` on the high
path. `uart_stage2_fp_to_uint.c` implements that C control flow. Its
host roundtrip over 20,005 deterministic uint32 values through
`0x10007af8` and back has zero mismatches. The compiled-source and
host-representation checks are separate from stock target execution.

The two remaining substantive retained soft-FP seed bodies now have C
candidates in `uart_stage2_fp_mul_div.c`. `0x10007730` multiplies two
normalized significands with a source-owned 64-by-64-to-128 four-product
algorithm; `0x10007930` divides a 121-bit scaled numerator using a
source-owned bitwise long division. Both preserve class/sign/exponent
paths and pack a two-word binary64 return. Pinned C-SKY target syntax
passes. The durable host corpus checks **19,983 finite multiply** and
**19,983 finite divide** pairs against independent IEEE binary64
results, with zero mismatches. This establishes neither target runtime
equality nor special NaN/exceptional behavior; those remain admitted
candidate risks. The only retained stage-2 exact-address suffix gap after
these bodies is `0x1000452c`, whose PMU descriptor lookup is already
semantic C under a nonaddress symbol. Whole codec source coverage still
requires separate resident/application region crosswalk, product data,
reset/link layout, and runtime qualification.

The final address suffix, `0x1000452c`, was a binding gap rather than
absent source. Direct native writes at `0x1000457a..0x100045d2` confirm
the existing `gx8002_uart_stage2_pmu_fill_desc` source sets the table
pointer, MMIO base, status, set, clear, and enable fields in the
six-word output. The Ghidra pseudocode's apparent zero base was a
relocation-rendering error. A typed `_452c` wrapper now binds that
already-owned semantic body to the retained seed address. Target syntax
passes. A fresh link/symbol census is required before recording 96/96;
this says nothing about resident regions or whole-image layout.

**Fresh retained-seed closure checkpoint.** The stable
`codec-stage2-all-seeds-final-round/receipt.json` compiles **85
stage-2 C units** and the codec experimental candidate with the pinned
C-SKY target compiler; the codec relocatable link reports success and
`source_complete=false`. Independently relinking all 85 stage-2 objects
with `csky-abiv2-elf-ld -r` succeeds. Their undefined-symbol list is
exactly the five compiler binary64 helpers `__adddf3`, `__divdf3`,
`__fixunsdfsi`, `__floatunsidf`, and `__muldf3`; there are no remaining
stage-2 application imports. Comparing defined address-suffixed C
symbols against all 96 entries in the retained
`uart_boot_stage2/functions-000.jsonl` yields **96/96 present, zero
suffix gaps**. This closes that finite *seed list* as C candidate
bodies/bindings. It does not close unseeded native functions, image-A
XIP/SRAM or image-B SRAM resident sources, semantic product data,
startup/link layout, stock runtime equality, or full codec image
composition.
