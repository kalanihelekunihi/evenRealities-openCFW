# Independent offline scan watchdog and MMIO poller

ARM32 recovered interfaces in watchdog.h. [Original-instruction comparisons and limits](../../../analysis/touch-scan-watchdog-closure-2026-10-08/REPORT.md).

This source operates on recovered configuration and volatile MMIO. Tests supply synthetic completion events; physical acquisition and IRQ concurrency remain unverified. No production integration.
