# Bounded timer callback receive/dispatch

Ordinary source defines zero-block-time queue receive, pinned MIT FreeRTOS V10.5.1 copy-out helper (static visibility removed), reconstructed task-port critical helpers and negative-command callback draining. Blocking receive and positive timer commands are explicit external boundaries. This is not a complete unchanged kernel daemon/API implementation.

Build: `make -C g2 timer-daemon-wsf-simulator`. Verify with installed native OpenCFW Python via `simulator/verify.py --elf ... --output <fresh path>`, or use `timer-daemon-wsf-simulator-test` with SCB_SIM_PYTHON set. The linked target includes existing queue/EventGroup/WSF/radio/GPIO source. Daemon activation, scheduler state/ready transitions and object lifecycle remain fixtures or missing providers.

Commands are copied from queue-owned storage into the daemon stack before callback execution. Event-group pointers remain borrowed; FIFO drain does not authorize destruction. Task critical outer exit clears BASEPRI to zero, separately from ISR BASEPRI restoration, WSF's PRIMASK enable and Ambiq's PRIMASK restoration.

See ../../../analysis/timer-daemon-wsf-2026-10-05/REPORT.md for original addresses, ownership/layout, comparison cases and remaining boundaries. SOURCE_PROVENANCE.json identifies precise source reuse versus bounded reconstruction. No firmware flash/byte-equal/source-complete claim.
