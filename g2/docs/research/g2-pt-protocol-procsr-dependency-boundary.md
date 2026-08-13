# G2 product-test protocol processor dependency boundary

Status: complete fail-closed linked-object and dependency boundary. Authenticated
against G2 2.2.6.10; no hardware or flash operation was performed.

The largest remaining retained first-party path,
`platform\product_test\pt_protocol_procsr.c`, is now closed as 73 functions /
32,866 body bytes in physical interval `[0x0056F178,0x00577C3C)`, 35,524 bytes.
The interval begins after Cordio `smp_act.c` and ends before the already closed
`service_codec_dfu.c` object. Sixty-nine retained anchors are supplemented by
three Ghidra-discovered pathless helpers and a newly restored 692-byte handler
at `0x0056F92C`, reached by a real external BL at `0x0053A356`.

The main dispatcher at `0x0056F4A0` validates its four arguments, selects one
of 66 aligned Thumb handler pointers for supported command IDs, synthesizes a
five-byte unsupported-command response otherwise, prepends a bounded response
prefix, and appends its checksum. The one indirect call at `0x0056F838` is
therefore a closed internal dispatch, not an opaque provider. The exact handler
table pointers and their target digest are pinned.

The 1,526 external direct calls terminate at:

- 1,280 admitted EasyLogger calls;
- seven exact CMSIS-FreeRTOS v10.5.1 thread-ID, priority, and delay calls;
- one exact FreeRTOS V10.5.1 `xTaskGetTickCount` call;
- 41 bounded/source-recreated IAR DLIB and fail-stop runtime calls;
- one admitted mpaland formatter call; and
- 196 first-party hardware, persistence, audio, display, sensor, and
  production-policy calls, many already object-closed.

There is no embedded third-party implementation and no new version or commit
discriminator. The relevant reusable baselines remain EasyLogger commit
`a596b264…`, CMSIS-FreeRTOS commit `d213f261…`, FreeRTOS-Kernel commit
`def7d2df…`, and mpaland/printf commit `d3b98468…`. The product-test command
implementation is private G2 code; its historical generating commit is not
recoverable from the binary.

Whole-image closure finds 30 real BL entry sites and 66 real aligned stored
Thumb entries. Four apparent BL targets are second-halfword decodes inside real
UDIV/MUL instructions, one aligned raw interior value at `0x004C7450` is itself
an LVGL instruction window, and the other raw matches are likewise instruction
accidents. One `B.W` at `0x00571490` is an ordinary internal branch within a
single handler. The object, uncovered data/literal pool, adjacent boundaries,
instruction graph, call graph, provider graph, 14 retained-path cells, and 256
path references are hash-pinned by `tools/analyze_g2_pt_protocol.py`.

This closes the reusable utility question for the production protocol but does
not make the private product-test hardware policy production-ready. OpenCFW
must clean-room that policy and validate it on hardware before routing it.
