# Independent closure of delay arithmetic receipts

**PASS:175 independent checks validate all38 reported original-wrapper executions and their counts.** Fourteen selected input/mode pairs differ from SDK5.2 integer predictions. This closes the finite source-arithmetic comparison under the declared synthetic state; no physical delay or complete initialization claim follows. No guest rerun was needed.

Input packet: `../coverage-audit-parallel-2026-10-09/delay-sdk52-discriminator/LINUX-EXECUTION-REVIEW.md`, execution receipt, predictions, scripts and backend identities. All six listed execution-deliverable hashes match. Locked main payload SHA-256`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` was reauthenticated. Entire original80byte wrapper `[0x4807A0,0x4807F0)` matches hash`f95193c502160b469e1579e13223f1cdf488a2d8fab9ec07f686c9101fbed753`. Literal words at0x4807F0/F4/F8 independently decode binary32 250,96 and status register0x40021000. SDK am_hal_utils.c member hash`a4204e045b06d377eac4d2d1dec3adfc4c788ecf905bc002080eb5e769aad2b2` and its83us+(us+1)/3/adjustment25 statements agree with the authenticated ZIP.

Original instruction receipts separately bind unsigned integer→f32, fixed-point u32 conversion with5fractional bits, HP multiplication/division, truncation conversion, LP adjustment15 and HP adjustment24. Original BL at0x4807EA independently decodes ITCM0x40. Performance bits[4:3]==2 select HP; supplied register16 yields2, supplied0 yieldsLP. The uint32 loop-count threshold is raw>adjustment, otherwise return.

The independent oracle uses exact `fractions.Fraction` arithmetic and nearest-even binary32 rounding via rational spacing, not the owner's struct.pack/host-float derivation. It rounds input, re-converts fixed-point integer, rounds HP multiply and divide separately, then truncates to uint32. All intermediate/final uint32 conversions and SDK sums remain in range for the19 selected inputs. Both modes yield38unique fixtures with no duplicates or omissions. Every independently calculated count equals the receipt's predicted and observed r0 entry argument.

For every fixture, full reported instruction address order is independently reconstructed from the original control flow. Trace contains no ITCM0x40 instruction. Nonzero inputs stop with PC0x40 after original BL; zero inputs return to sentinel0x480. No loop execution is hidden in a later trace. Initial FPSCR is explicitly written/read as0 in the hash-authenticated execution script. All final FPSCR values are0 or0x10; rounding bits[23:22] remain0. This confirms consistency with nearest-even arithmetic and allowed cumulative inexact status under the supplied model, not arbitrary hardware FPSCR state.

| Fixture | Stock loop argument | SDK5.2 loop argument | Meaning |
|---|---|---|---|
| HP,us1 |59|58|Smallest adjustment/formula discriminator|
| HP,us2 |142|142|Equality control|
| LP,us16777217 |536870897|536870929|Input binary32 precision discriminator|
| HP,us16777217 |1398101352|1398101392|HP rounding/formula discriminator|
| Either,us0 |No loop call|No loop call|Threshold/return control|

Backend identity records Unicorn2.1.4 in the existing Linux environment, Cortex-M33 instruction profile. Stack, CPACR/FPSCR and performance register are explicit synthetic inputs. This is not a full Apollo510 M55 or physical FPU/peripheral model. The local macOS mapping fault was outside guest execution; its exact host cause remains unknown. The separately preserved Linux receipt is reviewed rather than replacing or deleting the failed native attempt.

Finite lineage conclusion: selected stock floating-point scaling/HP24 does not match unchanged SDK5.2 integer scaling/HP25 on14of38selected fixtures. Agreement with the earlier source arithmetic does not uniquely identify the producer SDK or imply all older-source wrappers are equivalent over all uint32 inputs. SDK behavior was calculated from authenticated source, not compiled/executed in this experiment. No compiler flags or source bytes were fitted to outcomes.

Limits: no ITCM loop/scatter initialization, real microseconds, clock calibration, cache/bus latency, physical exception/interrupt delivery or device operation. Review authenticates receipts and their internal consistency; it does not independently witness their original execution in real time. No source-completeness, coverage-counter or byte-identical-firmware claim. The touch72byte duplication remains explicitly corrected, with zero unique coverage.

No production, index, submodule-pin, commit/push, device or prior-seal mutation. Preservation.json records prior sealed-entry count,110protected inputs and four checkpoints. Outputs are isolated here. Reproduce the independent checks with `python3 g2/analysis/delay-sdk52-independent-receipt-review-20261009-implementation/review.py`; it does not import Unicorn or execute guest firmware. No remaining input blocks this finite arithmetic closure.
