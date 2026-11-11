# R1 accelerometer reset and history helpers in C

`native_gomore_accel_history.c` provides three stock contracts for the next
accelerometer-processing dependency, stage `0x5ed14`:

- `0x710d4` clears 622 bytes through the existing EABI provider, writes state
  byte 8, then writes five `0xec78` (−5000) halfwords at offsets 612 through 620.
- `0x58480` writes fourteen zero words followed by six `0xff` bytes. Its store
  widths and order match the observed reset record.
- `0x484fc` clears nine halfword slots in the native order, reloading the live
  cursor at offset 82 before every store. It reloads again before incrementing,
  keeps values below eight, and otherwise writes zero. No cursor guard is added.

The earlier checked mode-8 utility omitted the sentinel halfwords. It now
validates its pointer/length and delegates to the native C reset. The checked
missing-window and slot utilities similarly delegate; slot keeps its cursor
range guard. All three checked names carry `_checked` so they are distinct
from the native ABI. There is one underlying implementation per stock function.

There are 2,073 passing direct native/C pairs, including all 256 cursor bytes,
four pointer alignments, both interrupt-mask states and nine logical fault
cases. Corrupt cursor values can alias the cursor byte itself, so caching or
masking it changes later stores. Six compiled defects are rejected: cached or
masked cursor, wrong wrap boundary, zero sentinels, shortened output reset and
byte-width sentinel stores.

Another 216 pairs execute the actual native accelerometer stage with these
three C providers substituted. Gap, reset, available/unavailable input, signed
warmup bytes and floating-point modes are covered. The other collection,
spectrum and math functions execute stock. Provider arguments and depths,
public writes, complete external state, R0, FPSCR, preserved registers and SP
match. Private stack residue and caller-clobbered registers/flags are excluded.
Eighty checked-interface pairs agree with the native helpers; 260 invalid
pointer/length/cursor cases retain their checked rejection behavior. The
monolithic utility object's unused imports bind to the stop sentinel in that
fixture; they are not executed.

The fresh normal build compiles 707 units (633 application and 74 bootloader)
without failures or duplicate strong symbols. Imports remain 178 application /
34 bootloader: stage `0x5ed14` itself is still unresolved. Manifest validation
passes. Exact qualification rejects all three bodies, leaving the canonical
plan at 4,381 source-built executable bytes, 641,779 stock executable bytes and
248 resource bytes. The fresh R1 hybrid remains stock-identical. Neither that
hybrid nor these bounded replays proves physical sensor behavior, a full-source
firmware link or byte identity of the new C implementations.

The [machine receipt](gomore-accel-history-c-review.json) records REA evidence,
production source/object hashes, build reports and validation results.
