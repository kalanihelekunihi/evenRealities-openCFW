# PCM callback registration foundation

Manual stock instruction reconstruction of57ab78 registration and57acd0 unregistration. `registration.c` links unchanged queue/DMA/cache/consumer source in an isolated ELF. Build: `make -C g2 audio-registration-simulator`.

Register accepts low-byte mode0 or1 and nonzero callback, replacing an occupied row. Unregister has no mode-range guard; it converts mode to uint8, tests callback presence and checks the owner word before clearing. These raw semantics are intentionally preserved. Supply mapped storage and a mapped observation output disjoint from the registry, provider state and input buffers; this is not a safe public app API or a firmware patch.

`opencfw_pcm_registration_cut_t` is NEW observation ABI. Provider0 means a completed stock-like result in `status`. Nonzero provider means stop before logger43d574 or43ce9e; stage identifies the exact decision point. The actual6-byte logging-flags getter reads20004543, not a synthetic logger return. Logging-disabled branches execute complete original functions in the verifier. Logger-enabled branches never execute or replace the logger provider.

A12-byte record at20073c20+12*mode contains owner+0, mode byte+4 and callback+8. On replacement, the stock12-byte zero fill writes words+4,+8 then+0; registration then writes owner, mode byte, callback. Empty registration does not clear bytes+5..7. Source preserves these word/byte orders but does not reproduce or claim the atomicity of the original multiword store instruction. No critical section, barrier, exclusivity/refcount, PCM copy or DMA ownership is added.

Verify:

```
/Users/kalani/.local/share/opencfw/venv/bin/python g2/components/foundation/audio_pcm_registration/verify.py --elf g2/build/foundation/audio-registration-simulator/registration.elf --output /tmp/pcm-registration-comparison.json
```

Native Unicorn JIT needs authorized execution outside this host sandbox. Normative registration comparisons use no memory hooks. A Capstone code observer derives ordered store bytes from executed instructions and pre-instruction registers, then compares full nonstack/non-observation RAM and full modeled I2S/SCB state. Ten queued/DMA/consumer calls are repeated with the prior scoped-memory observer and must agree with no-memory-hook results. This audits the tested paths; it does not establish all-input equivalence, physical MMIO behavior or concurrency. The observer depends on the installed Unicorn2.1.4 callback-handle layout.

Prior consumer source remains unchanged: notifications carry12-byte type/tick metadata without PCM pointers; ages0..40 ticks pass; selected PCM remains borrowed; callback is reread. This cycle changes registrations between top-level calls, not through a proven hardware interrupt interleaving.

[Analysis report](../../../analysis/audio-registration-2026-10-06/REPORT.md) and [pseudocode](../../../analysis/audio-registration-2026-10-06/pseudocode.md) include actual production registration targets and remaining routing/provider limits.
