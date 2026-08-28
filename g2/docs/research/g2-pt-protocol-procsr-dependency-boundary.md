# G2 product-test protocol processor dependency boundary

Status: fail-closed top-level implementation with an explicitly retained
second-order board ABI. Authenticated against G2 2.2.6.10; no hardware or flash
operation was performed.

## Current clean-room backend status

The current source tree implements and host-exercises all 56 typed board
operations, including invalid arguments, an unsupported operation, a null
context, and a missing required provider. All fourteen product-test translation
units link with zero undefined symbols for both Apollo510/Cortex-M55 and
Cortex-M0+. The production call table is borrowed rather than copied; its public
contract requires the caller to keep it valid and immutable for the lifetime of
the board and derived platform backend. The production initializer satisfies
that contract with static storage.

The top-level production table is fail-closed at field granularity: all 83
field/address/function-ABI associations are pinned, with 43 classified as
admitted source-overlay routes and 40 routed through semantic-C board leaves. A
further 53 field/address/type/minimum-extent associations deliberately support
the authenticated stock data ABI: 17 immutable-flash constants and 36
runtime-SRAM state/buffer bindings. Their address space, field, type, and extent
partition is fail-closed, and no stock machine code or retained vendor data byte
is embedded in the MIT source.

The 40 semantic-C leaves cover 3,402 authenticated stock body bytes:
display-state/staging/identifier/brightness/offset, codec-identifier,
audio-status/path and four microphone lifecycle leaves, both bounded
hardware-identifier providers, charger-test enable/disable, UART, buzzer,
audio-route, time configuration/capture, input-message-ID-3, screen show/hide,
lens synchronization, and seven ambient-sensor
initialize/configure/sample/reset leaves. Their host behavior and both target
links are gated, and the canonical provider routes the top-level leaf table.

That top-level routing is not complete source ownership. The leaves themselves
contain 57 fixed callable bindings at 55 unique entries. Eighteen are redirected
to admitted source-overlay providers; 39 bindings at 37 unique entries remain
supported retained callable boundaries. The leaves also contain 33 separately
classified fixed data/address dependencies: 23 runtime-SRAM bindings, two
immutable-flash values, two retained callback entries, two external-XIP data
bases, two XIP range bounds, and two peripheral-MMIO registers. None is hidden
inside the 53 top-level data count. The analyzer pins every macro name, cast ABI,
address, ownership class, and category, and reports source completeness false
while these second-order retained boundaries remain. Physical policy, sensor,
display, audio, persistence, and timing qualification is deferred by project
direction.

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

This closes the reusable utility question for the historical production
protocol object. The current clean-room policy and 56-operation backend are
described above; its remaining source-completeness blockers are the explicitly
retained second-order callable and data boundaries. Physical qualification is
deferred by project direction and does not change those software ownership
gates.
