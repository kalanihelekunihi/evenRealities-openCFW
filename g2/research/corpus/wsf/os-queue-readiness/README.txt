OpenCFW Cordio FreeRTOS WSF OS/queue build-readiness probe

Scope and provenance
--------------------
Read-only/scratch-only inventory of the official AmbiqSuite R2.5.1 S3 archive.
The proprietary source itself is intentionally excluded from this artifact.
Archive: 200161418 bytes; SHA-256 87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133.

Authenticated sources
---------------------
wsf_os.c: 11665 bytes, SHA-256 892a7ae0283ba9274f80e48e6a2507cf49d3075fad7c3298656afc98a1a56e4, Git blob 8a466f57d90e402502cdfcfda96e616736487021.
wsf_queue.c: 8650 bytes, SHA-256 7dd109b4509d31c3222827b73f7ed5587e46a2c9d2de54ed8f30c599d418cf86, Git blob 7eab0ae7d02486a9e8af9419cc8f25235a2a1200.

Closure
-------
wsf_os.c has 25 unique probe dependencies including the C file: 22 files from the archive, GCC stddef/stdint, and one seven-line string.h prototype shim because the pinned compiler image deliberately omits newlib headers. A native SDK build replaces only that shim with libc string.h. Excluding the translation unit itself, the archive header closure is 21 files.
wsf_queue.c has 8 unique dependencies including the C file: 7 archive files plus GCC stdint. Excluding the translation unit itself, the archive header closure is 6 files. It requires no FreeRTOS header and its only undefined providers are WsfCsEnter/WsfCsExit.

Recovered stock OS cluster
--------------------------
The coherent range [0x0052B8A4,0x0052BAB8) is 532 bytes and contains 12 functions. Stock layout proves WSF_MAX_HANDLERS=10: handlerEventMask begins at +0x28, msgQueue at +0x34, taskEventMask at +0x3C, numHandler at +0x3D, and memset clears 0x40 bytes. Other recovered globals are csNesting 0x20075045, xRadioTaskEventObject 0x20074EF0, and wsfOs 0x20073230.

Probe build
-----------
Pinned ARM GCC 13.2.1 container sha256:4bf18d22a8e9e1dffa4c21ea1ba44decf7a88a4a2e9c766e47c523f4bef26db0, Cortex-M55 Thumb, WSF_MAX_HANDLERS=10. Four OS configurations and two queue configurations compile with zero diagnostics. O0/Os OS times were 35.938/60.821 ms; queue times were 25.756/39.629 ms. Og and Os-no-sibling OS times were 42.070/55.485 ms.

Comparison
----------
Per-function ELF sections, raw bytes, and strict normalized disassembly are structurally comparable. No raw or strict-normalized match occurred in 48 probe rows. Os-no-sibling is best: aggregate absolute size delta 64 bytes and 3/12 exact-size functions. Plain Os has delta 76 and 1/12 exact-size. The main expected distortion is compiler/port configuration: archive GCC ARM_CM4F inlines xPortIsInsideInterrupt, while stock calls the IAR-style provider at 0x00442228. Exact-size is therefore only source-shape evidence.

Recommended bounded matrix
--------------------------
Use the established 13 GCC configurations with WSF_MAX_HANDLERS fixed at 10. For the 12 OS functions this is 13 objects and 156 comparison rows. Adding all 7 queue functions gives 26 objects and 247 rows. Expected sequential compile/comparison time is under two seconds on Lorelei based on this probe; parallelism is unnecessary but safe by translation unit/config. Prioritize Og and Os -fno-optimize-sibling-calls first. Add a stock-ABI FreeRTOS shim lane (external xPortIsInsideInterrupt and recovered event/yield seams) before expanding all 13 profiles. Treat a licensed IAR lane as a separate later compiler-provenance experiment.

Queue stock mapping is not claimed by this probe; identify its separate cluster around the recovered WsfQueueInsert/WsfQueueRemove callees near 0x00538C8C before byte comparisons.
