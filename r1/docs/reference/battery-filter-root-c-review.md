# Direct C five-sample battery filter

Current implementation: [ordinary C battery ADC workspace](battery-filter-pure-c-review.md). Fixed-register/frame contracts below are historical.

`board/native_battery_filter.c` now supplies stock `0x91184` directly in C.
The naked assembly bridge and separately framed `r1_battery_five_sample_body`
are removed. Empty constraints retain the native live registers and incoming
scratch words; the unit has no executed inline assembly instructions.

REA verified the 182-byte stock code and its padding/context/divisor literals.
The C root keeps the 48-byte provider frame and first sixteen scratch bytes:
four incoming words are stored in order, only incoming R0's low halfword is
cleared, then the following three words are zeroed. Each unsigned sample is
retained in the halfword array, added to the running sum and cleared from the
temporary low halfword. The delay-mode byte and ADC handle are reloaded around
callbacks. Close runs before the array is re-read for its two minima, preserving
duplicate minima and retained-pointer mutations. Unsigned subtraction and
32-bit product wrap, integer division and sixteen-bit narrowing are retained.

The final normal product object passes 4,620 paired stock/C cases (9,240
executions), including 4,096 deterministic random/partial-write cases. The
independent oracle checks every scratch read/write width, order and value,
provider arguments and mode selection, callback mutations, all live R4-R11,
returns, final scratch/context bytes, saved registers, SP and masks. The battery
runtime remains at `0x20006890`, distinct from guarded YHM storage at
`0x2000687c`. Every tested provider is entered at caller SP minus 48 bytes.

Four compiled negative controls fail: whole-word scratch clearing, excluding
duplicate minima, fixing the delay path and changing the scaling factor. The
previous bridge also fails the stricter provider-depth check at its first open:
80 bytes instead of stock's 48. The C replacement removes that extra call frame.

Existing alias-safe halfword helpers avoid a GCC strict-aliasing warning without
suppressing warnings. GCC now compiles strictly and reaches the observed result,
but writes the four initial incoming words twice. Its retained first-case trace
matches after those extra stores are removed; the strict trace check remains
failed and GCC behavior is not fully qualified. The normal Clang object passes
the original access oracle without relaxing it.

All 579 R1 units compile and compose without failures or duplicate strong
symbols. The 578 unrelated objects and imports (164 application / 34 bootloader)
are unchanged. The manifest is unchanged; the superseded helper is the only
removed strong symbol. Scoped qualification compiles the unit but selects no
exact region. Source completeness and byte equality remain separate from this
frame and behavior proof.

The canonical hybrid retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Selected counts include assembly and data elsewhere. The normal report
is `build/sources-goal-r1-filter-root-c-final/report.json`.

[Machine-readable evidence](battery-filter-root-c-review.json) records hashes,
REA observations, audits and counterexamples. Probes are under ignored
`build/goal-r1-filter-root-c/`. Registry/ADC, scheduler and delay providers are
modeled. Physical timing and voltage accuracy, APSR, other caller-clobbered
registers, private-frame aliases, faults and concurrency remain unproven.
Original Arm Compiler 5 is unavailable. Complete source-only, byte-identical
firmware remains incomplete.
