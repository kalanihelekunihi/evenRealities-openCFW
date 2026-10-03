# Independent review 6373

Disposition: **PASS_SCOPED**; `accepted:false`.

The hashes match for 0x42DFCA–0x42E048. GNU Thumb decoding confirms continuation from the established 88-byte frame. It stages the fresh word at buffer+0x14, a literal, and tag 542, calls 0x4176CE(4, R7, R6, R5), and ignores the result. A fresh word at buffer is reduced to bit 26. If clear, it proceeds to 0x42E00E; if set, it calls 0x42D890(global output pointer, buffer), truncates the result to a byte, and routes zero through 0x42DE0E or nonzero through 0x42DAE8. Those child results are ignored.

At 0x42E00E it loads the global record and freshly reads offset 20. If this value differs from 0x00438000, it stages that constant, the fresh value, a literal and tag 553 for 0x4176CE(1, R7, R6, R5), ignores the result, and stores 0x00438000 at record+20. It then freshly dereferences that field, shifts the pointed word left by two, and tests the original bit 29; clear branches to the request loop at 0x42DE9E, set continues beyond the packet. This is a write to the runtime-addressed record field; it does not rewrite the locked image.

No semantic purpose, hardware/runtime, C-equivalence, or admission claim is made. No canonical files or gates changed.
