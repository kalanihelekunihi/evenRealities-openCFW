# HAL control request 30 transaction

This isolated source provider covers request 30 (`0x1e`) from the pinned `0x4251c0` dispatcher in `ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. Source is in `nor_mspi_init/control_request_transactions.c/.h` and the small shared leaves `control_request_helpers.c/.h`.

The handler reproduces config validation, state clear/doorbell behavior, optional single-block post, the three-block follow-up descriptor, mode-state flag composition, producer/rollback handling, and first-pending CQ enable. It also provides the callback stored in the first descriptor slot at stock address `0x424978`; the source fixture rebinds that pointer to compiled code and compares callback effects independently. Callback pointer values are address-relocated, so the request-state comparison masks only those specific callback values.

The original/source comparison passes 33 cases and covers all four module IDs, null and malformed config, mode guard, both first-stage branches, CQ clock failure, and callback effects; 1,172 original instruction bytes were exercised. The full traces and source/object hashes are in `result.json`.

Queue allocation/post/release, queue enable, descriptor flag helper, block-post helper, and callback execute compiled source. Clock request is an intercepted status provider; all RAM and MSPI MMIO are synthetic. Therefore this validates request-side state and descriptor construction, not asynchronous command completion or physical peripheral progress. This request-30 provider remains isolated and has not been routed through the shared control switch. Request 34 remains a separate unresolved transaction path.
