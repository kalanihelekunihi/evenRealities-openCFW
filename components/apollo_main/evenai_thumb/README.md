# Even AI lease trampoline: restore the Thumb bit

`g2flash-evenai-thumb.patch` fixes a HardFault in the shipped `SybilSight CFW
(2.2.6.11)`. It applies to the `g2flash` CFW patch set at commit
`6d5c58598e047ca5980065a9ee7570ce2d172ca7`, the same base
[`../canvas480`](../canvas480) pins. It changes one immediate and nothing else:
no capability marker, no wire contract, no geometry, no new code.

## The defect

`patch_compress.py` replaces the first four bytes of the stock
`even_ai_display_ctrl` at `0x004E1FD2` with a `B.W` into
`faceclaw_evenai_display_entry`, so the Faceclaw wake lease can suppress a
native Even AI start. That trampoline reproduces the overwritten prologue and,
when it does not suppress, returns to the stock body at `0x004E1FD6`:

    movw r12, #0x1fd6
    movt r12, #0x004e
    bx   r12

`BX` selects the instruction set from bit 0 of its destination. `0x004E1FD6` is
even, so this requests ARM state. The Apollo510 (Cortex-M55) implements no ARM
state, so the core raises a UsageFault with `INVSTATE` set. The stock vector
table installs no MemManage, BusFault or UsageFault handler — all three vectors
are zero — so it escalates to HardFault. The HardFault handler at `0x005B0114`
captures `/log/hardfault.txt` and then spins at `0x005B011C` (`b .`) until the
external watchdog resets the temple, which drops the BLE link and re-advertises.

Every path through the trampoline reaches that `bx` except one: `op == START`
while a valid lease is held, which returns early via `pop {r0-r6, pc}`. That
single path is the one SybilSight itself exercises, which is why the defect
survived review — and why it reproduces most reliably when SybilSight is *not*
connected.

The destination is spelled as a bare immediate inside inline assembly, so
neither the compiler nor `build.py`'s mini-linker ever sees a symbol whose Thumb
bit it could set. The same translation unit materializes eight other
interworking destinations — including `FW_SIDE_ID` (`0x0045A569`) and `FW_SEND`
(`0x00475B15`) — as odd constants in C, and all eight are correct.

## Why one immediate is the whole fix

`0x1fd6 | 1` makes the destination `0x004E1FD7`: the same instruction at
`0x004E1FD6`, entered in Thumb state. The stock body is unchanged, the resume
point is unchanged, and the suppression path never used this branch. The rest of
the trampoline is already correct — the `ldmia sp, {r0-r3}` restore matches the
push order, `lr` is preserved on the stack across the `bl`, and the suppression
path's `pop {r0-r6, pc}` takes its own Thumb bit from the stacked `lr`.

Compiled with `build.py`'s flags, the fix moves exactly one byte in the emitted
trampoline, `0xD6` to `0xD7` at blob offset 24.

## Verification available without hardware

[`../../../tools/thumb_branch_audit.py`](../../../tools/thumb_branch_audit.py)
scans a Thumb-2 blob for `movw/movt -> bx|blx` triples whose destination has bit
0 clear. Against the shipped image it reports nine constant interworking
branches and exactly one defect:

```sh
python3 openCFW/tools/thumb_branch_audit.py <cfw-blob.bin> --base 0x00794324
```

[`../../../tests/test_thumb_branch_audit.py`](../../../tests/test_thumb_branch_audit.py)
pins the shipped trampoline bytes, asserts the audit detects the defect, and
asserts a one-byte edit clears it. Its whole-image assertions run when
`SYBILSIGHT_G2_CFW_IMAGE` points at the reviewed bundle:

```sh
SYBILSIGHT_G2_CFW_IMAGE=/path/to/g2-2.2.6.11.bin \
  python3 -m unittest tests.test_thumb_branch_audit -v
```

## Reproducible local build

There is no builder here. The change is a single immediate in a source file that
[`../canvas480/build_stock_canvas480.py`](../canvas480/build_stock_canvas480.py)
already knows how to compile and replay, so apply this patch to the same
`g2flash` checkout before invoking that builder rather than duplicating it:

```sh
git -C /path/to/g2flash checkout 6d5c58598e047ca5980065a9ee7570ce2d172ca7
git -C /path/to/g2flash apply /path/to/openCFW/components/apollo_main/evenai_thumb/g2flash-evenai-thumb.patch
```

Then build against the pinned stock image and re-run the audit on the result. A
fixed build must report zero findings and must differ from the reviewed
`2.2.6.11` blob in exactly the one immediate byte.

## Validation gate

This component has not been compiled into a full image, flashed, or observed on
hardware. Before any image built from it reaches a customer:

1. rebuild against the pinned stock `2.2.6.10` and confirm the audit is clean
   and the blob delta is the single expected byte;
2. flash sacrificial hardware and confirm that native "Hey Even" and the Even
   app's Even AI button no longer reset the temple, with and without SybilSight
   connected;
3. confirm the Faceclaw lease still suppresses a native Even AI start while
   held, and that the idle double-tap takeover and its fail-open dashboard
   fallback are unchanged; and
4. confirm no new `/log/hardfault.txt` entries across the session.

## Provenance and license

See [`NOTICE.md`](./NOTICE.md).
