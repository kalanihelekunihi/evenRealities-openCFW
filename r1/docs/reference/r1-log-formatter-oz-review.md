# R1 SDK log and formatter size profiles, 2026-11-10

The application manifest compiles the SDK `nrf_log_frontend.c` and
`nrf_fprintf_format.c` units with Clang `-Oz -mno-global-merge` in place of
their earlier `-Os` optimization. No source function or data was removed.
The disabled global merging preserves the SDK's named RAM sections.

An isolated probe and the full manifest rebuild show the same exported
symbol names, binding and kinds, and named `.data`/`.bss` section names and
sizes. Arm ABI attributes match except for the expected optimization goal
tag. The allocated raw object sizes fall by 686 and 434 bytes respectively.

The build at `build/sources-r1-log-formatter-oz-20261110/report.json` compiles
all 893 application and 82 bootloader units without failures or duplicate
strong symbols. `make sources-check` passes, and the strict bootloader link
is valid. The strict application receipt in its `app-link/report.json` shows
24 unresolved functions and 28,312 bytes of full flash-load overflow, down
1,152 bytes from the preceding 29,464-byte checkpoint. The application is
still not linked; physical logging timing and stock byte identity remain
unverified.
