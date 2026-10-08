# Case polling consumer and frame command dispatch

**1,230 fresh PASS comparisons**:540 original/independent dispatcher cases,258 hex-helper cases and432 selected polling bit8-fragment cases. [dispatch.c](../../components/case/frame_dispatch_offline/dispatch.c) reconstructs085c/9b94 and6e86..6e9a; [interface](../../components/case/frame_dispatch_offline/dispatch.h). No old tests rerun merely for counts.

## Actual consumer behavior

Original task08006e1c samples osEventFlagsGet into R5, then processes multiple actions against that retained snapshot. Selected bit8 fragment clears event8 first, calls085c, then resets u16 count2000010a to0 after return. Native fragment uses actual original clear wrapper0800a7d2→0800c44c and critical providers. Event-word writes assert PRIMASK1; coherent critical depth0/1 restores mask0/1. Snapshot0/8 and current event bits0/8/48 are independent synthetic inputs: sample/action separation is real, **these combinations are not observed concurrency schedules**.

The complete task/startup/other action branches are excluded. Original execution starts at6e86 with seeded live registers and stops at6e9a before next branch. Command handlers08000928(legacy) and08000e1c(binary) stop **before first instruction** on both original/native paths. Their arguments and live frame/count state compare; no fake handler returns. Count reset is executed only when dispatch returns without reaching a command boundary. Reset after a valid command return is static call order, not full command-handler completion proof.

## Frame formats and buffer effects

Shared frame20000974, count2000010a, thresholded state byte20000893. Count<2 returns untouched. Otherwise state byte<30 resets0, even for rejected frames; its physical meaning/units are unestablished.

- First byteDE directly forwards frame+1,count-1 to legacy handler. This synthetic consumer fixture does not prove the earlier UART starter accepts direct binaryDE.
- ASCII D/d E/e decodes pairs **in place** at frame indices1..floor(count/2)-1, then forwards frame+1,length floor(count/2)-1. Odd trailing character is excluded. No newline or per-digit validity guard exists here. Hex helper accepts0-9/A-F/a-f and maps every other tested byte to0. Invalid hex characters therefore contribute zero nibbles rather than a decode error.
- Binary5A A5 type7F checks advertised byte at+3 ==count-5, forwards frame+4,length count-4,mode0. TypeCF checks little-endian u16 at+3/+4 ==count-6, forwards frame+5,length count-5,mode1. Forwarded length is **advertised length plus one**. The extra byte's checksum/trailer meaning is not established at this command-handler boundary.

All cases use allocated guarded1200-byte frame storage/count<=1200; decoder mutation and guards compare. Binary child payload parsing/destination validation, checksum meaning, actual timed bulk read and receive/task scheduling remain separate dependencies. No copy or ownership transfer is performed by dispatcher: child receives pointer into shared mutable frame, ASCII decoding mutates that same frame. Use strict hex encoding in app tooling; event8 is a notification, not an immutable payload or message counter.

## Source and lifetime limits

[Prior global/creator trace](../case-multiwaiter-closure-2026-10-08/REPORT.md) grounds dynamic32-byte event construction at200000f0 and observed Get/Clear polling. This batch executes the selected consumer action but does not establish stock close/delete or producer-quiesce/daemon-drain ordering. Synthetic waiter kernel tests are not actual blocked consumers of this group. No patch-safe or actual buffer-race claim follows.

Build/run using build_offline.py and verify.py with ArmGNU13.3/opencfw venv; source/tool/image/output hashes and limits retained. All851 prior seals,110 audit inputs and4 checkpoints preserved; no index,commit,production firmware/device changes. Next product target is binary handler08000e1c's length/destination/trailer-validation prefix or ASCII legacy command dispatch, rather than repeating these closed wrappers.
