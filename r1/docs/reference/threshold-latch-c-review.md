# R1 factory aging threshold latch in C

`r1/src/application/runtime/native_threshold_latch.c` supplies native callback
`0x8156c` (72 instruction bytes, followed by 12 literal bytes). REA assembly and
readback were checked against the locked application. Source, object, replay,
startup and build receipts are retained in
[the machine-readable review](threshold-latch-c-review.json).

The callback reuses `r1_factory_mode_state.active` at native `0x20006c34`.
Its declaration now lives in `native_factory_mode.h`; the original mode source
still owns the sole state definition and its compiled object is unchanged.
The new unit owns only the twelve-byte sample cache at native `0x2001a1a4`,
represented by `r1_factory_threshold_samples`.

## Recovered behavior

An inactive mode returns before checking the input length. A length below twelve
also returns without reading the sample pointer. Otherwise all three 32-bit
sample words are captured before the cache is written. This preserves behavior
for overlapping input/cache pointers. The configuration-byte getter is called
after the stores; subsequent threshold decisions use the captured samples even
if that provider changes the input, cache or active state.

Each unsigned sample strictly below 8,000,000 (`0x007a1200`) latches its bit:
first word bit one, second bit two, third bit four. Equality does not latch.
The full getter result is preserved when ORing bits. A changed result is passed
to the configuration setter; an unchanged result produces no write. The handle
argument is unused. No null-input check is added: an active callback with at
least twelve bytes follows the native read fault for a null pointer.

## Verification

The direct fixture passes 10,620 paired stock/C replays, comparing ordered reads
and writes, configuration calls and arguments, final state/cache/input slabs,
guards, masks, return SP and callee-saved registers. Cases cover inactive and
noncanonical active bytes, short and full-word lengths, threshold boundaries,
unsigned extremes, high configuration bits, unaligned input, overlapping cache
input, getter mutations and gated null-input faults. The callback is declared
void, matching its existing consumer; R0 is treated as caller-clobbered and is
excluded. Private stack, APSR and physical exception behavior are also excluded.

Another 648 paired cases execute the actual native/C stream dispatcher and
threshold callback together. The list head/next, sensor read and configuration
getter/setter are modeled. These cases include short samples and actual
callback delivery. The dispatcher retains its prior 40-byte native versus
48-byte C frame, giving configuration-getter depths of 56 versus 64 bytes in
this chain. Direct callback getter depths match at sixteen bytes, with setter
tail entry at zero bytes. Full frame and instruction identity are not established.

Six compiled negative controls are rejected: signed comparison, inclusive
comparison, accepting an eleven-byte input, redundant configuration writes,
rereading input after the getter, and truncating the setter's full-word argument.
Configuration getter raw-stack behavior, persistent writes and physical sensor
delivery remain unproven by these modeled boundaries.

Native RW and ZI startup handlers were executed against poisoned regions with
guards; the independent RW decoder matched. The new cache's object data matches
the native twelve zero bytes at `0x2001a1a4`, with four-byte alignment and no
cache relocations. This proves the scoped initial contents, not final firmware
placement or complete startup integration.

## Build status

`make sources-check` passes. All 614 units compile (540 application and 74
bootloader); both relocatable compositions pass without failures or duplicate
strong symbols. All preceding 613 objects are identical, including the mode
owner after header extraction. The manifest adds only the latch unit. The latch
import resolves without exposing another, leaving 168 application and 34
bootloader imports. Only its existing frontier row changes.

Scoped qualification compiles the unit but admits zero bytes. The source plan
is unchanged. The fresh hybrid matches application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
with 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. A full source-only link, candidate byte identity and physical
hardware validation remain incomplete.

Reports: `build/sources-goal-r1-threshold-latch-c/report.json` and
`build/hybrid-goal-r1-threshold-latch-c/build-report.json`. Fixtures and audits
remain under `build/goal-r1-threshold-latch-c/`; durable results are in the JSON
review above.
