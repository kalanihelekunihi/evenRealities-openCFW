# Audio receive buffer/cache handoff

`handoff.c` reconstructs the selected-buffer query at 0x590b6c and full audio getter at 0x57a7e0 from the locked Apollo artifact. The getter invalidates3200 bytes through the existing cache source, then publishes a borrowed address/length; observed R0 contains the address. It performs no PCM copy, lock, refcount or release. The mutable selected slot is also used by the DMA rearm service; exclusive ownership is not proven.

`handoff.h` exposes the two reconstructed entry points and two separately named **new checked-policy** helpers. The checked helpers require caller-supplied aligned/nonwrapping bounds; their status 0/6 ABI and rejected inputs are not stock replacements or proof of storage lifetime. Huge legitimate raw ranges remain bounded-prefix-only evidence, rather than completed-path passes.

Build: `make -C g2 audio-cache-handoff-simulator`. Verification: installed OpenCFW Python `verify.py --help` lists the ELF/output options; native Unicorn execution requires the host's permitted JIT environment. 282 original/source cases and 1,157 new policy cases pass; 13 independent representative native cases pass. No production firmware link, physical cache/DMA coherence, safe scheduling or byte equality is claimed.

See `g2/analysis/audio-cache-handoff-2026-10-06/REPORT.md`, `pseudocode.md`, `validation-summary.json` and `review/`. These sources are MIT instruction reconstructions, not copied or attributed Ambiq SDK functions.
