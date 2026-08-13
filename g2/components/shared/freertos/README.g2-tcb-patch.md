# G2 FreeRTOS V10.5.1 TCB compatibility patch

`g2-tcb-v10.5.1.patch` is the minimal reviewed source delta needed to make the
authenticated FreeRTOS-Kernel V10.5.1 task-control-block layout compatible
with the official G2 `s200_v2.2.6.10` image.

The upstream base is the official annotated `V10.5.1` tag, peeled commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. The patch applies to pristine
`tasks.c` and `include/FreeRTOS.h` from that snapshot with:

```sh
git apply --ignore-space-change components/shared/freertos/g2-tcb-v10.5.1.patch
```

The patch adds one 32-bit stack-depth field after `pcTaskName[32]`, mirrors
it in the public opaque `StaticTask_t`, and assigns the incoming creation
depth in `prvInitialiseNewTask`. Under the recovered G2 configuration this:

- changes both `TCB_t` and `StaticTask_t` from 108 to 112 bytes;
- places the new word at `+0x54`;
- shifts the two trace words to `+0x58/+0x5C`;
- shifts base priority and mutex count to `+0x60/+0x64`;
- shifts the notification value/state and allocation byte to
  `+0x68/+0x6C/+0x6D`.

This is a semantic reconstruction of a vendor delta, not recovered proprietary
source. The original vendor field name, comment, and patch commit are absent
from the binary and remain unknowable from the reviewed artifacts. Official
FreeRTOS V10.5.1 and the current upstream development branch do not contain
an equivalent TCB field. Keep this file outside the authenticated pristine
snapshot so upstream bytes and vendor-derived compatibility work remain
distinguishable.

The stock creators prove the delta independently: `xTaskCreateStatic` checks
and clears `0x70` bytes, `xTaskCreate` allocates and clears `0x70`, and
`prvInitialiseNewTask` stores its depth argument at `TCB+0x54` before copying
the 32-byte name. The focused verifier and tests are:

```sh
python3 tools/analyze_g2_freertos_tcb_patch.py
python3 -m unittest -v tests.test_g2_freertos_tcb_patch
```

The patch does not by itself authorize a wholesale `tasks.c` production link.
Apollo STIMER tick/tickless glue, application hooks, trace macros, fixed kernel
globals, and the remaining configuration switches stay separate integration
boundaries.
