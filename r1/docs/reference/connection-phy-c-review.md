# R1 connection PHY update in C

`r1/src/application/board/native_connection_phy.c` implements stock `0x4d2f4` using the pinned Nordic `sd_ble_gap_phy_update` declaration and its S140 SVC gateway. REA readback of the stock envelope matches the authenticated application bytes. No new assembly or mutable state is introduced.

Exact full-word handle `0xffff` or a nonconnected SDK state returns 8. Valid calls retain full input words for diagnostics, capture byte-sized TX/RX settings before those diagnostics, pass a uint16 connection key through SVC `0x8f`, and return its full status. Nonzero status is logged. The repeated mode reads and log order match stock.

The replay executes native and compiled C policies, including the actual SVC instruction. It compares 55,440 combinations of handles, connected states, PHY settings, SDK results, logging modes and interrupt masks; five targeted boundary replays also pass. All six compiled defect controls fail the replay. Callee-saved integer/FP registers, stack guards, masks, scalar results and provider traces are checked. Connection-state, log and radio service backends are modeled; physical radio behavior is unverified.

The normal R1 build compiles 846 units (764 application, 82 bootloader). All 835 prior nongenerated objects are unchanged; two generated objects differ. Application imports remain 71 and bootloader linker imports remain 22. This lower dependency prepares the larger GAP event handler, which remains open. Composition does not establish a final firmware link or boot. Byte identity and paid compiler availability are not requirements.

The exact hashes, REA read, replay and defect receipts are in [connection-phy-c-review.json](connection-phy-c-review.json). `python3 tools/build/sources.py check --device r1` passes. The repository-wide manifest check still reports the unrelated unlisted G2 `resident_rom_thumb_set.S` source.
