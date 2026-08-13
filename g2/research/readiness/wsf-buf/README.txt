OpenCFW Lorelei Cordio wsf_buf.c readiness and structural matrix

Scope
-----
Scratch-only comparison against authenticated stock. Proprietary source and generated objects/disassembly are excluded. The artifact carries hashes, exact flags, clean-room shim/stub text, full comparison/build ledgers, closure, timing, and source-API section sizes.

Source and bounds
-----------------
Official AmbiqSuite R2.5.1 archive SHA-256 87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133; wsf_buf.c is 13241 bytes, SHA-256 e13de1419b29d0d82eee31ce1fe7d4c776eba98bf83b04001842f8cba7027a08, Git blob 550bcf45275be013547cf49587606b591b1ee5d6. AmbiqSuite 2.4.2 is byte-identical, so this module does not discriminate those releases by itself.
Three functions are independently bounded: WsfBufInit [0x530364,0x530446) 226 bytes; WsfBufAlloc [0x530446,0x5304D4) 142; WsfBufFree [0x5304D4,0x530512) 62. The 430-byte cluster SHA-256 is 01bc4ff2164b21f29f84a393ac4865a7175d1bb569f30b21d578fa6b2919906f. Evidence includes exact source semantics/order, globals and 12-byte pool layout, one/24/28 BL callers, retained FreeRTOS-port path and line 321 for Alloc, and free magic for Free. Four other source APIs compile but remain stock-unbounded/dead-stripped.

Variants and closure
--------------------
The recovered configuration fixes free-check on, statistics/histogram/OS diagnostics off, and a 12-byte pool descriptor. Archive-notrace exposes WsfCsEnter/Exit only. The stock-warning lane additionally externalizes a seven-argument line-321 warning metadata provider while retaining the direct CS seams. Both variants link to zero undefined symbols in every profile. With diagnostics off, the archive deliberately leaves WsfBufDiagRegister's callback unused, requiring the documented -Wno-unused-parameter exception under otherwise strict -Werror.

Results
-------
Two source/config variants x 13 GCC profiles x 3 bounded functions = 78 rows; 26 source objects and closure links completed in 3463485594 ns. Compile total 1784389215 ns; link total 285754090 ns. Zero raw and zero strict-normalized matches occurred. Best common lane is stock_warn_seam__O3: aggregate absolute size delta 34 bytes, 0/3 exact-size. Per-function best gaps are Init 10 bytes, Alloc 10, Free 2. The warning seam improves the best aggregate from 78 bytes (archive-notrace O1) to 34 bytes (stock-warning O3), strongly supporting the missing local trace-backend seam without claiming compiler identity.

Recommendation
--------------
Use stock-warning O3/O3-noinline for Init+Alloc and Os/Oz-no-sibling for Free. Next recover the exact local warning/logger macro and IAR assertion/trace flag interactions; inspect the two-byte Free epilogue gap; and map the four dead-stripped source APIs only if caller/pointer evidence appears. A licensed IAR lane remains decisive for output identity.
