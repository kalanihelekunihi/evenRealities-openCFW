# RX receiver and UART3 ring offline source

Selected unchanged FreeRTOS10.5.1 receiver bodies retain original license; ring.c is reconstructed UART3 logic. [Evidence, call flow and limits](../../../analysis/audio-uart-rx-consumer-2026-10-09/REPORT.md). Task providers are explicit scheduler stubs/cuts, blocking waits unclosed. No production driver, concurrency or physical loss claim.
