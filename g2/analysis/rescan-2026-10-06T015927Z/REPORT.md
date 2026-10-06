# Checkout rescan

Compared with 2026-10-06T01:19:04.229791+00:00, foundation C/header files increased from 85 to 89 (+4). Prior source changed: 0; removed: 0. HEAD remains 4ab13514dfcfd96f835784118cf580c48715c2d3.

New source:

- `g2/components/foundation/audio_pcm_consumer/consumer.c`
- `g2/components/foundation/audio_pcm_consumer/consumer.h`
- `g2/components/foundation/audio_pcm_registration/registration.c`
- `g2/components/foundation/audio_pcm_registration/registration.h`

The notification/consumer batch connects the 12-byte tick-stamped audio event to bounded queue insertion/reception, stale-event filtering (unsigned age 0–40), cache-maintained borrowed PCM lookup, and callback dispatch. The registration batch reconstructs the two-slot owner/mode/callback registry, replacement, and owner-matched removal. Stock unregister has no two-slot range guard; synthetic mode-2 tests demonstrate unchecked indexing, not observed hardware misuse. Replacement changes which callback consumes already queued metadata. Neither batch copies PCM or establishes DMA buffer lifetime. Diagnostic codec/file callbacks are distinct from normal BLE streaming.

Saved comparisons: notification/consumer PASS 328 calls; registration PASS 103 calls. Registration additionally records ten-call no-memory-hook/scoped-hook observer agreement and independent spot checks. Cumulative distinct executed payload/address bytes increased from 7,426 to 8,418 (+992); touch 234, Apollo 8,184. This is bounded execution evidence, not total firmware coverage.

This rescan checked 111 saved hash bindings; mismatches: 1. The one mismatch is the older notification batch’s `g2/Makefile` binding: the subsequent registration target extended that shared file. The latest registration Makefile binding matches, and both batches’ source/ELF/result bindings match. It did not rerun builds, emulation, or tests. Latest saved aggregate: 44 modules, 228 tests, 222 passes, six method skips plus one setup skip, no failures/errors; affected checks: eight passes.

Source Git views: {'tracked': 85, 'untracked': 4, 'ignored': 0}. Four new C/header files are untracked and visible to Git. `.gitignore:15:build/` hides simulator ELF/results, not those source files. No new commit or additional worktree appeared. Packer, manifest and workflow-state identities remain unchanged: True. Existing index preserved: True.

Limits remain: synthetic scheduling/MMIO does not prove hardware concurrency, cache coherence, or PCM ownership. Full task wake/routing and actual callback/DSP execution are not established by these prefix comparisons. Resident ROM timing input and optimized tick-emulator divergence remain unresolved. No fully source-complete payload or source-built byte-identical firmware bundle is established.
