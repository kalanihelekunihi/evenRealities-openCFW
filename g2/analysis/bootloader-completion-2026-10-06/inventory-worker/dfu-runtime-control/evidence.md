# DFU runtime-enable and error-transaction source closure

These bodies were already reconstructed in `g2/components/bootloader/platform_control/control.c`; `g2/components/bootloader/dfu_task/task.c` calls the same exported APIs through `task.h`. I kept that single implementation and did not create duplicate definitions in the DFU task directory.

Locked reference: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, base `0x410000`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

| Entry | Range | Size | Reference SHA-256 | Source API |
|---|---|---:|---|---|
| `0x42ddf2` | `[0x42ddf2,0x42de0e)` | 28 B | `2e690fb77d2d549104eaeb32851f8dfc94e079fb872890a5258604be9be8782c` | `opencfw_boot_dfu_runtime_enable(void)` |
| `0x42de0e` | `[0x42de0e,0x42de58)` | 74 B | `ac57a9b6547160c8259307f2400e572680d610c2d7d8913fe30f29b21c1e28f0` | `opencfw_boot_dfu_error_transaction(void)` |

The runtime-enable source preserves the ordered calls: critical-save/interrupt mask, mode-one argument 1, mode-two argument 1, then cleanup. Stock returns the caller's incoming `r7` as `r0`; production callers ignore that incidental return, and the source API is `void`.

The error transaction logs level 1/code `0x1f9`, saves critical state, submits four `0xffffffff` words to the guarded MRAM dispatcher using key `0x12344321`, destination `0x007fe000`, and count 4, restores the saved PRIMASK, then enters terminal mode 0. The dispatcher result is ignored. Terminal mode writes `0xd4` to `0x40000008` and loops. The register-write loop is observed on synthetic MMIO only.

I rebuilt the existing module and reran `platform_control/verify.py` against stock and compiled source. Its receipt, `platform-control-comparison.json`, passes 496 fixtures and 270 original instruction bytes. Among those are two runtime-enable saved-PRIMASK cases and six error-transaction combinations (saved mask 0/1 crossed with MRAM statuses 0/1/`0xffffffff`). The MRAM driver is intercepted, as are some critical-save/guard callbacks in this profile; the test proves arguments, state restoration, and flow to synthetic terminal-write observation, not physical MRAM behavior or reset.

Build used `make -C g2/components/bootloader/platform_control all`; verification used `/Users/kalani/.local/share/opencfw/venv/bin/python g2/components/bootloader/platform_control/verify.py --elf g2/build/bootloader-completion/platform-control/control.elf --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/dfu-runtime-control/platform-control-comparison.json`.
