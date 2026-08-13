# Ambiq GPU-patch VG shadow source-candidate audit

Status: bounded production-excluded clean-room candidate; not required by the
recovered Ambiq LVGL subtree.

The exact 324-byte section at source line 454 and its 15 relocations recover a
complete VG radial-mask command stream. It snapshots clip and texture-zero
state, binds and clears an A8 target, sets stops `{1 - sw / size, 1}`, applies
the exact two color vectors, draws a radial circle, then performs an exact
texture/context restore. The section SHA-256 is
`a600d42433a84fe56934d36b167177bf1c617ce3cb8fafcbfecb9ca1948b9974`.

Four tests pin the full command trace and context restore, exact section/DWARF
identity, relocation-free Cortex-M55 text, independent naming, and this audit.
Hardware rendering and production admission remain outside this candidate.
