OpenCFW Lorelei Cordio WSF OS/queue stock-ABI matrix

Scope
-----
Scratch-only, read-only comparison against authenticated stock firmware. Proprietary AmbiqSuite source and generated object/disassembly bytes are deliberately excluded from this compact artifact. Source identities, stock/candidate body hashes, strict-normalized hashes, sizes, complete flags, closure, and timings remain reproducible metadata.

Inputs
------
Official AmbiqSuite R2.5.1 S3 archive: 200161418 bytes, SHA-256 87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133.
wsf_os.c: SHA-256 892a7ae0283ba9274f80e48e6a2507cf49d3075fad7c3298656afc98a1a56e4a, Git blob 8a466f57d90e402502cdfcfda96e616736487021.
wsf_queue.c: SHA-256 7dd109b4509d31c3222827b73f7ed5587e46a2c9d2de54ed8f30c599d418cf86, Git blob 7eab0ae7d02486a9e8af9419cc8f25235a2a1200.
Stock firmware: 3523396 bytes, SHA-256 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863.
Pinned compiler image: sha256:4bf18d22a8e9e1dffa4c21ea1ba44decf7a88a4a2e9c766e47c523f4bef26db0; ARM GCC 13.2.1 / binutils 2.42.

Recovered bounds
----------------
All 12 wsf_os functions occupy [0x0052B8A4,0x0052BAB8), 532 bytes. Six linked queue functions occupy [0x00538C24,0x00538D16), 242 bytes. WsfQueueEmpty is present in the archive source/object but no seventh stock body follows: 0x00538D16 is padding and 0x00538D18 begins an unrelated function, so QueueEmpty remains intentionally unbounded and excluded from comparisons.
Stock data layout independently fixes WSF_MAX_HANDLERS=10 and a 0x40-byte wsfOs structure.

Stock-ABI shim
--------------
The scratch shim preserves direct xPortIsInsideInterrupt, xEventGroupSetBitsFromISR, xEventGroupSetBits, xEventGroupWaitBits, and vPortYield provider seams; ISR yield retains the stock ICSR PendSV write. It removes the known archive-GCC inline/macro distortion while leaving Cordio source unchanged. Three shim hashes and full text are included.

Results
-------
Thirteen profiles, 26 source objects, 13 closure links, and 234 function rows completed in 3521196588 ns. Compile total was 1523577926 ns and link total 244945553 ns. Every source/stub compile passed -Werror. OS exposes 11 providers, queue exposes WsfCsEnter/WsfCsExit, the combined pair exposes 11 providers, and all linked closures contain zero undefined symbols.
No raw or strict-normalized exact match occurred.
Best combined profile: Os_nosibling (4/18 exact-size, aggregate absolute delta 74).
Best OS profile: Os_nosibling (3/12 exact-size, delta 52).
Best queue profile: Og (2/6 exact-size, delta 14).
Bounded per-function selection reaches stock size for 3/12 OS functions and 3/6 queue functions. Remaining queue size gaps are exactly two bytes each for Enq, Push, and Insert. Exact size is compiler-shape evidence, never a source or byte match.

Recommendation
--------------
Keep Os/Oz-no-sibling as the common OS lane and Og as the queue lane. Next prioritize the two-byte critical-section bodies and IAR epilogue/literal selection, then qualify the exact local FreeRTOS/IAR headers and logging/assert configuration. WsfQueueEmpty requires independent caller/pointer discovery before any stock mapping. A licensed IAR comparison remains the decisive compiler-provenance lane.
