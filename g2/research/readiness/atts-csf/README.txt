OpenCFW G2 Cordio coverage ranking and atts_csf.c readiness probe

Outcome
-------
* atts_csf.c is the highest-ranked remaining public-upstream candidate: 8 retained-path anchors and 4,798 anchored body bytes. Two additional 8-byte unanchored functions bring the defensible linked total to 4,814 bytes across 10 functions.
* The public Packetcraft r20.05 source is preferred over the older AmbiqSuite 2.5.1 copy. In particular, stock AttsCsfWriteFeatures follows the r20.05-or-later feature-update semantics.
* The r20.05 translation unit contains 11 source functions. Ten have standalone stock bodies. AttsCsfInit has no standalone body; bytes 0x52D4E8..0x52D507 are a literal/data pool, so Init was dead-stripped or inlined and must not be assigned a synthetic stock span.
* Isolated Os and O1 ARM-GCC builds completed in 0.204 s and 0.173 s. The four external seams are WsfTrace, attsCheckPendDbHashReadRsp, memcpy, and memset. The closure probe resolves all four and links with zero undefined symbols.
* GCC section totals for the ten linked functions are 564 bytes (Os) and 648 bytes (O1), versus 4814 stock bytes. No function has equal candidate/stock size, so no raw match is possible in this probe. A normalized comparison was intentionally not run.

Interpretation
--------------
The large stock bodies contain retained source-path/line instrumentation and likely IAR whole-program inlining around trace/assert/logger seams. A broad 13-profile GCC matrix would be low-value until that instrumentation ABI and the surrounding literal-pool boundaries are modeled. The source/version identification is nevertheless strong because the path anchors, line markers, function order, constants, control-block layout (DM_CONN_MAX=3), and r20.05 WriteFeatures behavior agree.

Recommended next step
---------------------
Model the stock IAR trace/assert/logger expansion as an externalized seam, preserve the ten proven spans, and compare normalized control flow/call topology against r20.05. Only then expand compiler profiles or LTO variants. Keep AttsCsfInit in source inventory but exclude it from stock function comparisons.

Evidence and packaging
----------------------
* Retained path: third_party\cordio\ble-host\sources\stack\att\atts_csf.c at 0x006DC934; pointer cells 0x0052D088 and 0x0052DA2C.
* The archive contains identities, ledgers, timings, and independently authored closure shims only. It excludes firmware/source bytes, decompilation text, objects, ELF files, and build caches.
* Stock ranges use an exclusive end address. Their SHA-256 values authenticate slices without redistributing them.
