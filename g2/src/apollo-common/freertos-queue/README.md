# FreeRTOS ISR data queue provider

Two unchanged pinned MIT FreeRTOS V10.5.1 function texts implement the ISR queue producer and copy helper. Ordinary reconstructed C/assembly adapters supply synchronous byte copying and BASEPRI save/set0x30/restore. Queue sets are disabled; scheduler receiver wake/taskcount/mutex disinherit remain external providers. The callable target integrates radio/GPIO -> WSF -> event-group -> timer command queue. It copies16-byte callback commands before the caller stack is reused; the group pointer remains borrowed.

Build: make -C g2 timer-queue-wsf-simulator. Verify with installed native OpenCFW Python using simulator/verify.py and a fresh output filename, or timer-queue-wsf-simulator-test with SCB_SIM_PYTHON set. Actual xQueueReceive/daemon scheduling and object lifecycle are not supplied; delivery is an explicit synthetic consumer invoking the real callback. Invalid WSF ID/mask/nesting tests preserve stock semantics, not a checked adapter.

See ../../../analysis/timer-queue-wsf-2026-10-05/REPORT.md for addresses, contracts, comparison results, ownership limits and next provider boundary. SOURCE_PROVENANCE.json pins exact public text and source identity. No source-complete/byte-equal/hardware execution claim.
