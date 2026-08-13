# G2 notification-thread recovery

The three path-anchored `platform\threads\thread_notification.c` bodies /
374 bytes expand to eleven functions / 702 body bytes plus 114 bytes in two
literal/pointer pools, for 816 physical bytes at `[0x0048E154,0x0048E484)`.
Two baseline-missed
bodies restore the stored thread entry and packed thread-creation callback.
Nine direct entries, both stored pointers, 56 body calls, six path references,
both boundaries, and zero indirect or strict-interior targets are pinned.

The object creates a 50-entry/four-byte queue, creates its thread, waits on
thread flags, drains two known record types, reloads whitelist state, deletes
the queue on exit, and then blocks forever in `osDelay`. Its seven RTOS edges
land on exact, production-source-owned CMSIS-FreeRTOS v10.5.1 wrappers:
`osThreadNew`, flags set/wait, `osDelay`, and message-queue new/get/delete, all
at selected commit `d213f261…`. This composes already admitted wrapper and
kernel chains without adding a new version discriminator.

The remaining external calls are 30 admitted EasyLogger diagnostics and 11
first-party state/record/whitelist/fail-stop providers. No opaque utility body
is embedded. Product notification policy remains first-party and is not yet
production-routed.
