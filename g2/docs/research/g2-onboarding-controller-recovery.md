# G2 onboarding controller recovery

The four-anchor / 2,518-byte census view expands to twelve functions / 4,136
body bytes plus four interleaved pools totaling 340 bytes. The complete physical
object is `[0x00467FF0,0x0046916C)`, 4,476 bytes. Five small helpers precede the
first path anchor; three callback bodies after the last Ghidra-discovered body
are recovered from source order, retained names, path references, and four
stored pointer cells. All 1,558 instructions, 263 calls, 17 direct entries, four
stored pointers, both boundaries, and zero indirect or strict-interior ingress
are pinned.

The controller owns recursive LVGL color darken/resume passes, common-data
protobuf dispatch, process/flag synchronization, BLE disconnect state save and
reconnect restore, and UI-lifecycle registration of the BLE-status callback.
Its reusable graph is fully classified:

- 165 EasyLogger calls use selected commit `a596b264…`;
- 32 LVGL color/style/tree/image calls use selected commit `344c7c318…`;
- one exact `osMutexNew` wrapper uses CMSIS-FreeRTOS v10.5.1 commit
  `d213f261…`, over FreeRTOS-Kernel `def7d2df…` and CMSIS_5 `2b7495b8…`;
- two bounded IAR DLIB `memset` calls remain compiler-runtime seams;
- five calls terminate at the now-closed onboarding data manager, four at the
  closed FlashDB-backed onboarding KVDB leaf, one at the closed nanopb-backed
  onboarding protobuf dispatcher, and two at the closed BLE callback facade;
- the remaining 41 calls are private role/display/UI/peer policy.

No reusable definition is embedded, no dependency interval is narrowed, and no
private G2 generating commit is observable. The object is not production
routed; remaining work is first-party implementation and integration behavior,
not another unidentified third-party utility.
