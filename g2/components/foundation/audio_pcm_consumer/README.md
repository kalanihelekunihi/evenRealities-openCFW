# Bounded audio notification and PCM consumer source

`consumer.c` reconstructs the notification message, timestamp acceptance, RAM/context tick wrappers and PCM registration dispatch through explicit provider cuts. It links the existing real FreeRTOS ISR queue producer, zero-wait receive/copy/critical helpers, DMA rearm, selected-buffer getter and cache source. It is an isolated offline foundation module, not a flashable firmware image.

Build: `make -C g2 audio-notification-pcm-simulator`.

Verify with the installed OpenCFW Python:

```
/Users/kalani/.local/share/opencfw/venv/bin/python g2/components/foundation/audio_pcm_consumer/verify.py --elf g2/build/foundation/audio-notification-pcm-simulator/consumer.elf --output /tmp/audio-pcm-comparison.json
```

The JIT requires authorized execution outside this host's restricted sandbox. Source compiles atO2, Cortex-M4 compatible Thumb/soft float. Apollo510 hardware is Cortex-M55; execution compatibility does not establish hardware/NVIC/security fidelity.

`opencfw_audio_cut_t` is a NEW observation interface. `AUDIO_WAKE` means queue accepted and stock would enter449238 with flag400000; it does not mean a thread woke. `AUDIO_CALLBACK` stops before the callback, `AUDIO_DSP` before57ae56 fallback setup, stale and queue-error dispositions before43d0ce logging. Source prefixes return to the test caller; stock provider cuts retain live stack frames. Stock return-value equivalence is not claimed for these prefixes. The faithful raw path adds no ownership, allocation or age policy. Existing separately labeled checked cache/handoff policy is unchanged and does not solve lifetime.

The ISR queue adapter represents only timeout0 ISR submission; task receive represents only timeout0 task context. Fixture queue state is coherent12-byte data items, cTxLock=-1, empty sender/receiver waitlists, valid mapped storage. Linker references to455370 task removal and45596e disinherit are explicit external boundaries, never executed in accepted cases; the source assertion boundary08002000 is also never executed. No executable fake provider returns or retained firmware instructions appear in the C implementation.

Queue payload ownership and PCM ownership differ: queue storage owns a12-byte snapshot containing tick, with no PCM address. The consumer fetches the selected buffer later, invalidates cache, increments activity then passes the borrowed pointer/3200 length. Repeated rearms can change that selection before receive. The callback/DSP provider, producer concurrency and hardware coherence still need evidence before an ownership-safe patch can be designed.

See [pseudocode](../../../analysis/audio-notification-pcm-2026-10-06/pseudocode.md) and [report](../../../analysis/audio-notification-pcm-2026-10-06/REPORT.md) for addresses, test scope and remaining boundaries.
