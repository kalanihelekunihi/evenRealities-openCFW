# Packed negation and extreme complex accumulation ISA cross-check

## Conclusion

The documented PNEG.S16.S operation agrees with pinned QEMU and explains the inverse-split distinction from scalar32-bit negation. The documented MULACA.S16.S/MULACAX.S16.S operation disagrees with QEMU for the all-minimum-halfword product pair at accumulator zero: the manual requires positive saturation7fffffff, while the helper's wrapped intermediate produces80000000. This is a documented-operation/model discrepancy, not hardware execution proof. No source patch was made.

## Manual and source evidence

Existing manufacturer E804 manual2.0 (2024) Chinese original and Google translation were deduplicated, hashed and extracted; no new download needed. They are retained in registered ghidra-csky pin0daaa056e8c570ba514fc0d0226384ecf9f9df05. Provenance and PDF hashes are in PROVENANCE.json; selected page extracts in original-cn-extract.json and manual-extract.json. Chinese text extraction is partially garbled, but the original ASCII equations, constants and mnemonic names survive and agree with the translated pages. No new claim that the community mirror is an official manufacturer distribution endpoint is made.

- PDF503, printed486, section15.79: each signed16 lane independently undergoes saturating negation;8000 becomes7fff. QEMU op_dspv2.c:1071–1085 implements that operation.
- PDF570–571, printed553–554, sections15.125/126: MULCA/MULCAX explicitly special-case x=y=80008000 to7fffffff. QEMU:1565–1595 agrees.
- PDF575–577, printed558–560, sections15.130/131: MULACA/MULACAX saturate the entire accumulator plus both signed16 products. Both original equations place the whole three-term expression inside Saturate; there is no documented32-bit wrap before addition. QEMU:1597–1620 instead computes the dual-product sum in int32_t then passes it to signed saturating add. The independent audit establishes -fwrapv in this QEMU build.

## Directed arithmetic deductions

For cross1fffc000, high lane8191 and low lane-16384 independently negate to e0014000. Scalar32-bit negate instead gives e0004000. Adding1fffc000 leaves00010000 for the packed operation, and zero for scalar negation. Owner's endpoint-valid constant32767 spectrum probe therefore agrees with documented packed arithmetic; that mismatch is not explained by the complex all-minimum corner.

For x=y=80008000 each product equals1073741824 and their mathematical sum is2147483648. At z=0 the full documented saturation yields2147483647 (7fffffff). QEMU's narrowed/wrapped sum is-2147483648 and saturating add with zero returns80000000. At z=-1, documented result is2147483647; at z=-2147483648, documented result is0. Those are useful differentiators from pre-saturating the product sum as well as from wrapping it. They are analytical expected results, not newly executed fixtures. MULCA/MULCAX’s standalone special case must not be copied into accumulate semantics without testing cancellation: the full accumulator expression matters.

## Remaining limit

These equations resolve the stated semantic question against the E804 documentation and pinned simulator source. CK804EF's alias to E804DF in QEMU is model attribution; no physical GX8002 feature/revision or execution is certified. Reachability of x=y=80008000 in stock twiddle-table/caller domains remains separate. No simulator/code patch, numerical rerun, index change, firmware implementation or device access occurred.
