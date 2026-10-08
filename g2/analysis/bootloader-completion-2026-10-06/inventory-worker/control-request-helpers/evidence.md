# Control-transaction helper leaves

This fixture provides readable source for stock `0x423e14`, `0x427c12`, and `0x4279be`, directly used by HAL control requests 30 and 34. The pinned stock image is `ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

`opencfw_bl_control_stage_two_flags` reconstructs the three state branches: state 1 ORs `0x40a0` and advances the state to 2; state 2 returns exactly `0x4000`; other states OR `0x4080`. `opencfw_provider_427c12` validates the queue signature and available descriptor space, writes the four words from the queue's visible operation table and queue state, advances the producer by 16 bytes, mirrors the producer pointer, and writes the low sequence byte to the queue doorbell. `opencfw_provider_4279be` validates a pending reservation, rolls the queue producer back to its prior write pointer, and decrements the reservation count. The 16-byte stride and rollback direction are confirmed by original/source comparison; initial drafts were corrected when differential fixtures found divergence.

The original/source fixture passed 37 cases and exercised 200 stock instruction bytes. It covers all mode-helper state branches, flags, queue null/signature/full outcomes, both queue visibility classes, zero/nonzero command kinds, sequence truncation, and queue rollback success/error. See `result.json` for the exact traces and hashes.

All queue storage and registers are synthetic. This validates the leaf transitions, not DMA execution, actual device visibility, timing, or requests 30/34 end-to-end. The two helpers are available as source dependencies for those larger control paths; no shared request routing has been added here.
