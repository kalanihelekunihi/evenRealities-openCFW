# G2 notification-thread recovery

The three path-anchored `platform\threads\thread_notification.c` bodies /
374 bytes expand to twelve functions / 730 body bytes plus 86 bytes in one
literal/pointer pool, for 816 physical bytes at `[0x0048E154,0x0048E484)`.
Three baseline-missed bodies restore the stored thread entry, packed
thread-creation callback, and a contiguous thread-destruction routine. The
last routine had previously been misclassified as a literal pool; executable
Thumb recovery corrects that inventory error. Nine direct entries, both
stored pointers, 58 body calls, six path references, both boundaries, and
zero indirect or strict-interior targets are pinned.

The object creates a 50-entry/four-byte queue, creates or destroys its thread, waits on
thread flags, drains two known record types, reloads whitelist state, deletes
the queue on exit, and then blocks forever in `osDelay`. Its eight RTOS edges
land on exact, production-source-owned CMSIS-FreeRTOS v10.5.1 wrappers:
`osThreadNew`, `osThreadTerminate`, flags set/wait, `osDelay`, and message-queue
new/get/delete, all at selected commit `d213f261…`. This composes already
admitted wrapper and kernel chains without adding a new version discriminator.

The remaining external calls are 30 admitted EasyLogger diagnostics and 12
first-party state/record/whitelist/fail-stop providers. No opaque utility body
is embedded.

The clean-room production implementation covers all twelve routines in
compilable C: initialization ordering, the 24-bit wait mask, valid-flag
filtering, queue record IDs `4` and `0x101`, low-16-bit payload lengths,
free-after-dispatch behavior, whitelist and exit event bits, thread
create/destroy registration, queue teardown, and the terminal delay loop.
Host execution covers normal lifecycle, unknown records, allocation failures,
valid/error wait results, and exit behavior. Physical-device scheduling and
peer notification behavior remain blocked by unavailable authorized G2
hardware evidence; this is a validation blocker, not an unimplemented
software path.
