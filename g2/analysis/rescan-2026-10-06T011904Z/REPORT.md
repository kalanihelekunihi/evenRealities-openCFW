# Checkout rescan

Compared with 2026-10-06T00:40:34.849720+00:00, foundation C/header files increased from 83 to 85 (+2). Prior source files changed: 0; removed: 0. HEAD remains 4ab13514d.

New source files:

- `g2/components/foundation/audio_dma_rearm/rearm.c`
- `g2/components/foundation/audio_dma_rearm/rearm.h`

The new audio DMA rearm implementation recovers RX/TX next-buffer programming, completion/busy/error handling, interrupt status/clear and IPB clearing. The selected-buffer getter still publishes a borrowed 3200-byte PCM buffer; rearming does not establish exclusive ownership. Successful RX progress can precede a TX busy result. The ISR comparison stops before the actual notification provider on notifying paths; queue delivery and task consumption are not yet validated.

Saved original/source comparison: PASS, 899 scenarios / 1,019 calls, 740 traced instruction bytes including 610 new distinct bytes. Cumulative inventory increased from 6,816 to 7,426 distinct payload/address bytes (touch 234; Apollo 7,192). These are bounded instruction execution evidence, not whole-firmware source completeness or byte equality. Handoff regression records 282 stock/source and 1,157 separately labeled checked-policy cases. Independent review records 13 native and 2 IRQ-boundary spot checks.

This scan checked 17 saved evidence/hash bindings; mismatches: 0. No builds, emulation or tests were rerun. Saved aggregate remains 44 modules, 228 tests, 222 passes, 6 method skips plus 1 setup skip, zero failures/errors. The previous audio handoff missing narrative/provenance closeout now exists.

Git source views: {'tracked': 85, 'untracked': 0, 'ignored': 0}. Unlike the prior scan, substantial work is now staged; the DMA C/header are staged, while its README/verifier/review and most analysis closeout remain untracked. Staging is not a commit. `.gitignore:15:build/` continues to hide ELF/comparison outputs, not new C/header source. No new commit or extra worktree appeared. Packer, manifest and workflow state hashes are unchanged. This scan preserves the index and all existing work.

Remaining limits: synthetic MMIO/interrupt fixtures do not prove hardware cache coherence, DMA/consumer scheduling or buffer lifetime. Notification-to-PCM-consumer reconstruction has no new source artifact yet. Authenticated resident ROM timing and the optimized tick emulator blocker remain outside this batch. No fully source-complete payload or source-built byte-identical bundle is established.
