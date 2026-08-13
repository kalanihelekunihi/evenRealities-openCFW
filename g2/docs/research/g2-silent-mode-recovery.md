# G2 silent-mode recovery

The four-anchor / 622-byte census view expands to ten functions / 2,488 body
bytes plus two data regions, for 2,696 physical bytes at
`[0x0046916C,0x00469BF4)`. Raw source order restores the remote-status handler,
return-only and refresh callbacks, and the 1,378-byte UI lifecycle handler.
Three stored callbacks, 19 direct entries, 178 direct calls, all 957
instructions, both boundaries, and zero indirect or strict-interior ingress are
pinned.

The object owns a normalized settings status, a showing-UI flag, one-byte
common-data record `0x10A`, role-aware remote/local transitions, and the
silent-mode page lifecycle. Its reusable graph is 70 admitted LVGL calls at
selected commit `344c7c318…`, 70 admitted EasyLogger calls at `a596b264…`, one
exact source-owned FreeRTOS V10.5.1 `vTaskDelay`, and one bounded IAR `memset`.
The other 26 external calls are first-party display/settings/resource policy.
No third-party definition is embedded and no new version discriminator or
private generating commit is recoverable. The object is not production-routed.
