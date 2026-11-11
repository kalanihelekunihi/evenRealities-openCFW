# C BLE connection event consumer

`native_ble_connection_control.c` supplies stock `0x45184`, using the existing
queue, connection and parameter owners. It adds no mutable global state. The
native callback at `0x4e1e2` is exactly BX LR; its shared exported C body is checked against
those two bytes, with no invented timeout policy. Its canonical symbol preserves
the scheduler key for other modules.

The queue drain preserves null-success termination, per-message free, live queue
reloads and the complete event routing. Phone-role security requests remain
Nordic `pm_conn_secure(connection,false)` calls, with the stock busy handling and
follow-up scheduling. Glasses role, target matching and advertising preserve
provider order and captured/live handle distinctions. Target storage still runs
after a skipped or failed address query; event 0x4000 supplies the same target
pointer twice. The native second-target diagnostic read is retained despite its
right-target label. Delays remain raw units.

The [review receipt](connection-consumer-c-review.json) records 3,993 direct
stock/C comparisons, 3,993 with actual C parameter helpers and 144 through the
existing C encoder, memory movement, prepared FIFO, consumer and SDK parameter
gateways. All seventeen compiled behavior defects are detected, followed by the
unmodified full reruns. Coverage includes event/role/log combinations, occupancy,
security and query statuses, target matches and lengths, every forwarded byte,
queue-null/failure/free behavior, live provider mutations and multi-message drains.
The encoder integration also checks allocation and queue-insertion failures.

Replay inputs have fully readable route-specific payload spans. Comparing a short
header length in a backed buffer does not establish safety for a short allocation.
The actual RTOS allocator/queue kernel, scheduler, radio, log sinks, security,
target/state storage and advertising backends are outside these replays. Standard
memory and comparison routines execute; private stack addresses and incidental
caller-clobbered results are excluded.

The normal build compiles 843 units (761 application, 82 bootloader), with
79 application imports and 22 bootloader linker imports. Replacing the broad
consumer import exposes eight real lower dependencies: peer address query/store
and matching, charge-state refresh, glasses transmit power, ear-worn notification,
delayed disconnect policy and the op8 sender. No success stubs are added. All
832 prior nongenerated objects remain identical. The R1 manifest check passes;
the global check retains the pre-existing unlisted G2 `resident_rom_thumb_set.S`.
The [subsequent peer/power/report closure](peer-address-c-review.md) now supplies
those eight lower providers and their checked disconnect/validity helpers.
Final linking, runtime placement, physical timing and device boot remain
unverified. Byte identity and a paid compiler are not required.
