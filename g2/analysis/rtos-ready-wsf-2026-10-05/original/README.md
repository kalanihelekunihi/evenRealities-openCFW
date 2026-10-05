# FreeRTOS ready-transition evidence

This packet authenticates the locked-image ready-transition helper and its next-unblock-time helper, then maps their callers and global references to the pinned FreeRTOS source. It is static evidence only; it does not run a scheduler or ISR.

Run `~/.local/share/opencfw/venv/bin/python g2/analysis/rtos-ready-wsf-2026-10-05/original/verify.py`. The verifier checks the OTA/image and Ghidra corpus identity, six function bodies, the direct call sites, nine PC-relative globals, and the cached `tasks.c`/`list.c` source blob identities. `results.json` contains the hashes, decoded instruction traces, literal resolutions, caller map and source line anchors; `disassembly.txt` preserves readable assembly.

`0x455370` (246 bytes, SHA256 `1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4`) has the behavior of `xTaskRemoveFromEventList`. It takes the owner TCB from the highest-priority event-list item, removes that TCB’s event item at `+0x18`, then branches on `uxSchedulerSuspended` at `0x20074a58`.

When the scheduler is running, it also removes the state-list item at TCB `+0x04`, inserts the task into the priority-indexed ready list at array base `0x2006a49c`, and updates `uxTopReadyPriority` at `0x20074a38` as needed. Priority is at TCB `+0x2c` (44 decimal); the helper compares it with the current TCB’s priority through `pxCurrentTCB` cell `0x20074a20`. If the unblocked task has higher priority, it returns 1 and sets `xYieldPending` at `0x20074a44`.

When `uxSchedulerSuspended` is nonzero, the branch at `0x4553b4` goes to `0x455426` and appends only the event-list item to `xPendingReadyList` at `0x20073d24`. It does not remove the state item or add the task to a ready list in this branch. Scheduler-resume processing owns that deferred transition. The priority comparison and pending-yield flag are still reached afterward.

The original callers establish the critical context: normal queue receive/send bodies call the helper at `0x441c10`/`0x441d56` after task critical-section entry; ISR queue send/receive bodies call it at `0x4419f4`/`0x441e18` after the BASEPRI mask helper sets `0x30`. The caller traces also show the corresponding normal exits or saved-mask restores. These are representative real call sites, not an exhaustive caller inventory.

`0x455876` (38 bytes, SHA256 `a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598`) matches `prvResetNextTaskUnblockTime`. Its literal at `0x456050` points to the current delayed-list pointer cell `0x20074a24`. If that list is empty, it stores `0xffffffff` (`portMAX_DELAY`) in next-unblock cell `0x20074a50`; otherwise it reads the head delayed-list item’s value and stores it in that same cell. `0x455370` calls this helper on the normal ready transition in this build.

The source files match FreeRTOS/FreeRTOS-Kernel tree commit `def7d2df2b0506d3d249334974f51e427c17a41c`, V10.5.1, MIT license. Their SHA256 and Git blob identities are recorded in `results.json`. Source-to-binary correspondence is semantic and version-pinned, not a compiler-byte match. The exact build configuration is not in this source subset, and no task switch, delayed-list contents, or runtime ISR behavior is claimed.
