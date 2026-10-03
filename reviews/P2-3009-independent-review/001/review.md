# Independent review 3009

**Result:** PASS_SCOPED; `accepted: false`.

Candidate `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-command-queue-lifecycle-map-3008/001` pins the original flash image and three body extents. I verified its receipt artifact hashes and reran the static decode to `/tmp/review-3008-isolated`; 164 instructions tile the declared spans. Literal resolution matches the decoded words: state base `0x200262F0`, descriptor base `0x00430880`, signature `0x01CDCDCD`, and enable threshold `0x20080000`.

The ordered initialization stores, fresh config/descriptor rereads, index low-byte guard, and status paths match the original instructions. Enable and disable preserve the separate signature/already-state checks, descriptor bit update and handle state publication; DMB SY appears on the stated enable threshold branch. The code extents used are byte-derived and include full epilogues despite historically truncated symbol extents.

This is static evidence only. Child semantics, dynamic mutation/aliasing, exceptions, asynchronous effects, physical hardware behavior, and ownership remain outside scope; no canonical record is admitted.
