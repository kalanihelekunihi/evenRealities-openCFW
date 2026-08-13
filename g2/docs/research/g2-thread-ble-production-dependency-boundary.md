# G2 BLE production-thread dependency boundary

Status: complete fail-closed object and dependency boundary. Authenticated
against G2 2.2.6.10.

The retained `platform\threads\thread_ble_production.c` view has six anchors /
1,854 bytes. Source order, a stored task-entry pointer, and complete control-flow
recovery restore eight non-anchor functions. The final object is 14 functions /
2,140 body bytes in `[0x005382E4,0x00538C24)`, 2,368 physical bytes. It begins
after the preceding Cordio SMP object and ends exactly at the admitted Cordio
WSF queue object.

This correction matters: literal `0x00538B64` is `0x005382E5`, proving the
hidden task body at `0x005382E4`. That body owns six lifecycle calls previously
liable to be mistaken for BL-shaped data. Two more hidden bodies at
`0x005383BE` and `0x005383EA` create and terminate the CMSIS thread. The 145
direct calls comprise ten internal and 135 external edges:

- 106 EasyLogger calls, including one admitted `elog_hexdump`.
- 15 exact CMSIS-FreeRTOS v10.5.1 calls covering thread creation/termination,
  flags set/wait, delay, message queue construction/put/get/delete, and memory
  pool construction/alloc/free.
- three assertion calls to the exact FreeRTOS V10.5.1 `ulSetInterruptMask`
  entry at `0x005FA0A4`.
- five bounded compiler/runtime calls for memcpy, memset, strncmp, and a
  fail-stop wait seam.
- six calls to already closed first-party NUS, audio callback, AT parser, and
  BLE-production providers.

The thread attributes are pinned at `[0x0075B910,0x0075B934)`: name
`ble_production`, task entry `0x005382E5`, 112-byte CMSIS control block at
`0x200723E0`, 4,096-byte stack at `0x2036DE40`, and priority `0x21`. The resource
initializer creates a three-entry queue and a three-block pool with 0x104-byte
blocks. The protocol boundary checks header `5A A5 7F`, then an additive byte
checksum, before invoking the private `pt_protocol_procsr.c` provider.

Whole-image ingress is closed: 11 real direct BL sites, one aligned stored task
pointer, no indirect calls, no strict-interior ingress, and no wide-branch entry
targets. Raw value scans also find two explicitly rejected unaligned instruction
windows (`0x00644A27 -> 0x00538900` and `0x007940D3 -> 0x005383BF`); neither is a
stored pointer. Twenty-one references to literal cell `0x00538B50` authenticate
the retained path. The body, physical interval, uncovered 228-byte literal/data
pool, adjacent boundaries, call graph, instruction graph, and provider graph are
all hash-pinned by `tools/analyze_g2_thread_ble_production.py`.

No Cordio implementation body is embedded and no new Cordio release
discriminator appears. The object instead provides a concentrated consumer
cross-check of exact CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, FreeRTOS-Kernel commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, and EasyLogger commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. The product thread itself remains
private G2 code, so no historical generating commit can honestly be assigned.

The object is dependency-closed but intentionally not routed into production;
OpenCFW still needs a clean-room first-party implementation of its task and
product-test policy.
