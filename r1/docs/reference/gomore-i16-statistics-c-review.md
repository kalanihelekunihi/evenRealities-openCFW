# R1 signed-halfword statistics in C

`native_gomore_i16_statistics.c` supplies four dependencies of accelerometer
collector `0x4834a`: mean `0x722ec`, sample deviation `0x723b6`, capped range
`0x568f0` and mean absolute difference `0x8f4b4`. REA provides complete
instruction/pseudocode evidence for all four. The native entry points add no
pointer, size or count guards.

Mean and squared-deviation sums wrap at 32 bits. Division uses the wrapped
signed numerator and signed count, with the halfword results sign-extended.
Deviation subtracts an arbitrary raw 32-bit center before wrapping its square,
divides by count−1, converts the signed result under the live FPSCR rounding
mode, then tail-calls the existing square-root provider. Count one returns
zero variance after still reading its input. The sole signed division overflow
case is handled without C undefined behavior; zero-divisor cases are avoided
by the same native branches.

Range always loads element zero, even for zero/negative counts, and caps the
signed halfword range at 32,000. Mean difference reads current before next,
accumulates absolute differences modulo 32 bits, divides the wrapped sum as
signed and returns the low halfword sign-extended. Count subtraction wraps
before its signed loop comparison. These contracts differ from conventional
size_t-based statistics and from the earlier checked utilities.

The four generic utilities now have `_checked` names. They retain pointer/count
validation and delegate to the shared C arithmetic. The checked deviation
retains its injected square-root callback and shares the wrapped variance
provider; it no longer computes a potentially overflowing signed subtraction.
Counts above INT32_MAX are explicitly rejected by these checked interfaces.
The native range's mandatory first load remains distinct from the checked
range's empty/null fallback of 32,000.

Verification passes:

- 4,024 direct native/C pairs with stock square root, including 35 logical
  fault cases. Cases include signed-count boundaries used by the collector,
  odd pointers, arbitrary centers, seven FPSCR modes and 65,535–65,538-element
  buffers that wrap mean/difference accumulators.
- The same 4,024 pairs with the existing C square-root and errno providers.
- 216 actual native accelerometer-stage/collector pairs with these four C
  statistics and three C history/reset providers substituted together.
- 753 checked-wrapper comparisons and 18 invalid-input/callback guard cases.
  The actual monolithic utility object executes; unused imports bind to a stop
  sentinel and are not called.
- Nine rejected defects: unsigned division, unsigned difference division,
  unsigned count loops, unsigned variance conversion, population variance,
  skipped first range load, wrong cap, truncated center and reversed sample loads.

Tests compare full input hashes, errno guards and ordered public writes,
integer results or float S0, FPSCR, square-root input/depth, preserved registers,
SP and interrupt masks. The deviation tail-call retains the native square-root
entry depth. Caller-clobbered registers/APSR, private stack bytes and complete
fault exception frames are excluded. No physical or concurrent sensor proof is
claimed. The collector and higher accelerometer stage themselves remain stock
in these integration fixtures.

All 709 units (635 application, 74 bootloader) compile and compose without
failures or duplicate strong symbols; imports remain 178/34. Manifest validation
passes. Exact qualification rejects all four bodies, leaving the canonical plan
unchanged at 4,381 source-built executable bytes, 641,779 stock executable bytes
and 248 resource bytes. The fresh R1 hybrid matches stock. Complete source-only
linking, physical validation and C byte identity remain unfinished.

The [machine receipt](gomore-i16-statistics-c-review.json) binds source/object
hashes, REA evidence and every result above.
