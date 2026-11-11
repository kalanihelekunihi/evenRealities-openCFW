# C hardware variant detector

`r1/src/application/board/native_hardware_variant.c` implements stock entry
`0x6a244` in ordinary C. It replaces the variant import in the IQS model/count
path. The product BSN storage accessor at `0x7ba40` is now an explicit unresolved
`r1_product_bsn_get` dependency; no storage success is fabricated.

Any nonzero checked byte skips the accessor and returns the cached byte
unchanged. On a cache miss, the detector passes 30 initialized bytes (`ff` then
29 zeros), checks `B210` at offsets 0..3 and `A` at offset 9, stores cached=1
only on a match, publishes checked=1, then returns the live cached value.
A mismatch preserves the cache, including changes made during the accessor.
The independent byte owners at `0x2000775c` and `0x2000775d` match authenticated
cold RW and the compiled data sections. This does not establish final placement.

The [machine-readable review](hardware-variant-c-review.json) records 2,421
stock/C comparisons, each with two successive entries: all 256 values in each
checked BSN position, all cached byte values with checked 0/1/2/255, every
accessor write length 0..30, and cache mutations during the accessor. Integer
callee saves, stack guards, PRIMASK and BASEPRI are checked. Six compiled defects
are rejected, followed by an unmodified production-object rerun.

Another 612 stock/C comparisons and 12 private-buffer fallback checks execute
the actual C IRQ worker, detector, model/count/average/event helpers, IQS ports,
touch transport and registry. The prepared device callbacks and BSN storage
accessor are modeled. The [REA byte receipt](hardware-variant-rea-bytes.json)
identifies the stock ELF and matches the raw application's 82-byte entry body;
this is a byte check, not a decompiler equivalence claim.

The normal build compiles 835 units (753 application and 82 bootloader), with
77 application imports and 22 bootloader linker imports. All 832 prior
nongenerated objects remain identical; the two generated objects change as
expected for the new manifest. The relocatable composition is not a final
application link or physical boot proof. Byte identity is not required.

The native BSN accessor reads a persisted length without a caller capacity
argument. Its behavior for oversized lengths remains to be analyzed; these
probes deliberately do not claim that malformed storage is safe.
