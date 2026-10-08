# Saturated scan with actual mode source

**720 complete comparisons passed**, replacing the previous `0x6ac0` entry stub. Original instructions and independent native source execute mode guards, CPU setup, MRSS waits/delay, saturation configuration, frame loading, scan watchdog/polling and maximum-count correction. There are **no function-entry stubs**. FIFO, MRSS and interrupt completion remain synthetic peripherals.

Cases cover prior modes 0–8 and 255, FIFO values 0/1/100/65535, immediate/delayed/expired scan completion, widget types 2/6 and immediate/delayed/expired MRSS startup. Ordered MMIO accesses, internal state, output/status and MRSS read counts match.

A 315-step MRSS startup timeout is discarded by CPU setup and mode 5 still installs successfully. Later scan completion/status is determined separately. This proves software handling of a synthetic timeout, not the behavior of physically unpowered hardware.

Reentering mode 5 skips CPU/saturation setup and retains repeat-scan enable. An invalid prior mode produces error 1 and clears repeat-scan enable; saturated scan still reads FIFO, disables hardware and writes the corrected output. A nonzero output therefore does not establish acquisition success.

Type 7 alternate frames remain excluded. The native ELF is `/tmp/opencfw-touch-scan-mode-composed/scan.elf`; results/provenance record its identity. No production, index, device, commit or shared-campaign changes. Analog response, physical timing and IRQ concurrency remain unverified.
