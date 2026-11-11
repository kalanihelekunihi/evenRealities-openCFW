# R1 packed-status propagation in C

`native_gomore_propagate.c` supplies the 90-byte native propagation routine at
`0x7266a` and the 16-byte exact-one flag-clear helper at `0x5d360`. Both use
ordinary C, with no new RAM or assembly. The [receipt](gomore-propagate-c-review.json)
binds REA bytes/instructions, production hashes, paired replay artifacts,
negative controls, qualification and build results.

Propagation ignores its second argument and returns zero on every completed
call. It first reads the pending byte at context+1000. Zero skips all work,
including output access. Otherwise it reads the unsigned word at context+720,
divides by 30, subtracts two with unsigned wrap and reduces modulo 2880 before
calling the existing packed reader. It captures the low byte of that result,
reloads the time word, subtracts one after division and reduces modulo 2880
for the existing packed writer. Lower return statuses do not control cleanup.
After the writer returns it stores the captured byte to the output, then
clears the pending byte only if its current value is exactly one. Other
nonzero values are preserved. The helper returns the incoming context in R0.

This order matters when a provider changes the timestamp or flag, or when
output aliases the flag, timestamp or packed samples. At small timestamps,
unsigned subtraction wraps before the remainder; replacing it with signed
arithmetic or a previous-day clamp changes the native slot. A null output
faults after the packed write on an active path; a null context faults on the
initial flag read. No additional pointer or length guards are introduced.

Validation passed 1,890 direct stock/C pairs with modeled packed providers
and another 1,890 pairs executing the existing C packed reader/writer. Each
corpus includes 206 matching faults and covers every pending-byte value,
unsigned time boundaries, low-byte capture of unusual provider returns,
output aliases and provider changes. Each contains 432 mutation configurations,
288 actually reached. A further 258 standalone helper comparisons include all
256 flags and two matching invalid-context faults, preserving R0 and the
other registers that stock leaves unchanged.

Another 2,328 stock/C pairs execute the actual C interval-update caller,
propagation, packed accessors, EABI memory-clear wrapper and upstream musl
memset; only the interval engine is modeled. These include 400 matching
faults, context reloads, partial engine records and output/context aliases.
The total is 6,366 paired cases, including 814 faults and 5,552 completed
returns. Comparisons include provider arguments/order, guarded RAM, ordered
stores and widths, preserved registers, SP, masks and FPSCR on completed
returns. Caller-clobbered state and private stack identity are excluded;
clear-internal store widths are excluded in the caller integration.

Ten compiled defects are rejected: cached time, requiring flag one to start,
unconditional flag clear, wide output store, early clear, omitted clear,
null-output guard, wrong source slot, untruncated provider value and wrong
return status.

All 666 units compile and both relocatable compositions pass without duplicate
strong symbols. All 665 previous source objects are unchanged. Resolving
propagation adds no imports, leaving 164 application and 34 bootloader imports.
The existing native interval engine at `0x7244e` remains a dependency.

Neither body qualifies as instruction-exact: the compiler emits different
bytes, including an IT block in place of the native clear helper's branch.
The canonical plan remains 4,369 source-built bytes, 641,791 executable
pull-through bytes and 248 resource bytes. The fresh hybrid application
matches the locked artifact through that pull-through. Complete source-only
linking, byte-identical reconstruction, context initialization and physical
or concurrent hardware behavior remain unfinished.
