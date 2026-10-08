# HAL control request 34 transaction

This isolated provider reconstructs request 34 (`0x22`) from the pinned `0x4251c0` dispatcher in `ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. Its C provider is `nor_mspi_init/control_request34.c/.h`; queue mode flags and post/release leaves are shared in `control_request_helpers.c/.h`.

The handler checks the config and queue handle, enforces the `+0x20 == 0x100` limit, reserves `config[3]+3` queue blocks, constructs the leading command and variable tuple list, optional output pointer, and two trailing MSPI commands. It selects the stock default return-only callback when the state predicate matches, otherwise preserves the caller callback/context; successful posts update the pending/completion counters, restore interrupt mask, and enable CQ only on the first pending command. Post failure restores the mask, releases the reservation, and returns the queue status.

The original/source differential passes 19 cases and exercised 1,050 original instruction bytes. It spans all four module IDs, tuple counts 0–2, optional output pointer, default and explicit callback values, mode-state branches, null/invalid/full queue conditions, clock-request error, and the return-only callback body. Receipt traces and hashes are in `result.json`.

Queue allocation/post/release, mode flags, CQ enable, and the default callback are compiled source. Clock request is an intercepted status provider. RAM and MMIO are synthetic; the fixture does not establish DMA completion, physical peripheral progress, or timing. Shared request34 routing is left to the integrator.
