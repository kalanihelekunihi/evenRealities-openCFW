# EM9305 QP/C queue initializer

The standalone `qequeue_init.c` candidate was removed in wave 27: `QEQueue_init` is now the unmodified upstream
`third-party/upstream/qpc/src/qf/qf_qeq.c` (QP/C v6.5.1, commit 416dcec8) compiled through
`../qpc-port/qf_qeq_unit.c`, and was verified equivalent to the stock body at `0x310f5c..0x310f74` on the
QEMU-ARC harness (300 random tests, `g2/docs/em9305-arc-harness.md`). The remaining `QEQueue_*` functions are not
in the stock image and are discarded by `g2/src/em9305/link/g2-em9305.ld`.
