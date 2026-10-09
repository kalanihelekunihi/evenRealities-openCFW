# Predeclared SCB GNU14.2.1 holdouts

All three holdouts selected in
`touch-compiler14-successor-2026-10-09/HOLDOUT-PLAN.md` before compilation match
complete original sections with unchanged flags and no relocation entries:

| Function | Address | Bytes | Exact |
| --- | --- | --- | --- |
| Cy_SCB_ReadArrayNoCheck | 0x9218 | 56 | yes |
| Cy_SCB_WriteArrayNoCheck | 0x926E | 56 | yes |
| Cy_SCB_WriteDefaultArrayNoCheck | 0x92D6 | 16 | yes |

No target was added/dropped after compilation and no flag was fitted. This
tests the separate unchanged `cy_scb_common.c` translation unit, source SHA-256
`e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1`,
against original target hashes recorded in the predeclared plan. The selected
read function already matches10.3–13.3 and is a generalization control, not a
14.2-only discriminator.

Compiler: authenticated Arm GNU14.2.Rel1 buildarm-14.52, GCC14.2.1 20241119.
Flags and includes are identical to the previous MSCLP comparison:
Cortex-M0+, Thumb, -Og, freestanding/no-builtin, CY8C4046FNI_T412 and function
sections. No source or header change was made. All source/header and output
hashes, section sizes/hash/equality and absence of relocations are recorded in
`results.json`; object, assembly, preprocessed input and dependency files are
retained in isolated ignored outputs.

These are previously known source-attribution candidates predeclared as new
compiler generalization controls, not newly discovered functions or a random
unseen sample. Absolute authenticated payload offsets include the32-byte
wrapper: ReadArrayNoCheck0x5F38, WriteArrayNoCheck0x5F8E and
WriteDefaultArrayNoCheck0x5FF6. Historical symbol offsets omit that wrapper.
The original comparisons use wrapper-stripped bytes and flash base0x3300;
`coordinate-receipt.json` makes both coordinate systems explicit without
rewriting historical records.

The previously audited MSCLP trio plus these128 holdout bytes establish exact
comparators for six selected functions across two PDL translation units. They
do not establish a unique compiler or producing source revision, generated
configuration completeness, all PDL function attribution or full touch-payload
equality. This is compiler execution, not original firmware instruction or
device execution. No new recovered-function coverage count is implied.

Docker ran with the approved escalation route, digest-pinned Ubuntu amd64,
network disabled, capabilities dropped and no-new-privileges; tool/source/header
mounts were read-only and the task output was the only writable mount. No
production, device, Git index, campaign ownership/state or gate was changed.
Independent holdout receipt review remains pending.
