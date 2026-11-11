# R1 accelerometer crossing-period estimator in C

The stock estimator at `0x56f94` and unsigned-byte comparator at `0x58a7e` now have shared native-ABI C providers in `native_gomore_accel_period.c`. The checked vendor utility delegates to this implementation, replacing its approximate duplicate. The new unit contains no inline assembly or executable byte arrays. Machine-readable results and hashes are in [the receipt](gomore-accel-period-c-review.json).

REA instruction analysis, rather than its incomplete pseudocode, establishes the reachable normalization blocks at `0x570dc`, `0x5711e` and `0x571e2`, and the final rate calculation. The root covers 1,544 executable bytes across `0x56f94..0x573ff` and `0x57418..0x575b3`; the intervening literal pool is not code. The comparator is a complete 28-byte callback identified by its stock literal and instruction bytes; it was not a defined function in the Ghidra inventory.

The implementation preserves wrapped signed RMS accumulation over 200 halfwords, signed normalization, integer IIR history order, mirrored rolling windows, strict extrema decisions, transition argument order, raw interval-pair updates, interval bounds, initialization, 70% trimming, quartiles, median/interquartile selection and unfused rate scaling. Mode 1 selects the longer windows and doubles the final rate. Other raw mode values follow the stock alternative. The seed is unused; raw R0 returns zero. The comparator returns precisely -1, 0 or 1, using unsigned byte reads in native order.

The estimator retains the 368-byte frame and published scratch offsets, including filter histories, transition references and the interval list. Helper-entry depths and all data pointers compare directly against stock. Only the comparator code pointer is mapped to its corresponding stock identity in the qsort trace. Private argument homes differ; this is not a claim of private frame byte identity.

Verification passed:

- 396 paired root cases with native lower providers, and the same 396 with entirely C-linked lower providers; reference digests agree. Each backend includes 12 logical-fault cases, 78,000 IIR entries, 1,635 transition entries and 224 root qsort entries.
- 65,796 comparator pairs, including exhaustive byte pairs, identical pointers and four bad-pointer cases.
- 216 actual stock-classifier replay cases using the C period provider and existing C preprocessing dependencies; 432 C period calls, 86,400 IIR calls and 2,520 transition calls. The classifier root and autocorrelation remain stock.
- 100 checked-wrapper pairs and six guard cases.
- All 17 compiled deliberate defects rejected. Stock-only searches added two trim-removal examples from 117 attempts and two spread-decision examples from 18 attempts, supplementing four earlier initialization examples from 19 attempts. These distinguish 70% from 75% trimming and the 0.3 spread threshold from 0.5.

Replay checks external memory, ordered writes, caller bytes, RAM-end guards, fault effects, public scratch references, raw R0, FPSCR, SP, masks and callee-preserved registers. Native branch hits include 18 trim entries, six actual removals, 184 interquartile-mean selections and 22 median selections. It does not establish complete private stack bytes, arbitrary callee-private input aliases, caller-clobbered registers, APSR, full exception frames, concurrent mutation, device timing or stack safety on hardware. C lower-provider frame layouts can differ.

An independent estimator-subset link uses normal production objects, no native-address bindings or placeholders, and has no unresolved symbols. Its root, comparator, IIR, transition, qsort, memory clear, memset and sqrtf are C text symbols. Unused division adapters and double-square-root code are discarded. This is subset closure, not a complete source firmware link.

The normal R1 build passes with 718 units (644 application and 74 bootloader), no failures or duplicate strong symbols, and 178 application / 34 bootloader imports. It removes exactly the crossing-period import. Both source manifests pass `make sources-check`. Neither new function qualifies for instruction identity. The fresh hybrid retains 4,381 source-built executable bytes, 641,779 stock executable bytes and 248 resource bytes. Compilation, replay and hybrid success do not establish complete C firmware, device operation or byte-identical reconstruction.

Next unresolved accelerometer dependencies include classifier `0x67e4c` and autocorrelation wrapper/kernel `0x56d78` / `0x5c5f0`. No firmware was flashed and no source-plan selection was manually added.
