# I2S two-stage DMA rearm source

`rearm.c/h` reconstruct the actual service 0x5908a0 and its DMA-error/IPB/status/clear helpers. First-party upstream confirms names and two-stage NEXT register semantics; the implementation is from authenticated stock instructions, not copied SDK C. Its selected slot is the next-job address returned by the previous audio getter; exclusivity and safe consumption duration remain unproven.

`opencfw_audio_i2s_irq_prefix()` is a separate bounded seam: captures enabled status, clears, services, returns captured status. Bit4 marks where stock calls the actual notifier even after service9. It does not notify or implement a complete ISR/queue/scheduler.

Build `make -C g2 audio-dma-rearm-simulator` links the unchanged audio/cache source into a separate ELF. Native original/source comparison passes 899 scenarios/1,019 calls; the old 282 stock handoff+1157 checked policy cases also pass. Hardware cache/DMA effects and context timing are outside synthetic register fixtures. See the batch REPORT, pseudocode, validation-summary and review under `g2/analysis/audio-dma-rearm-2026-10-06/`.
