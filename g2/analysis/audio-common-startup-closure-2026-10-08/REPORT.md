# Common startup suffix and PCM2.2 reset

[Readable C](../../components/audio/common_startup_offline/startup.c) and [interfaces](../../components/audio/common_startup_offline/startup.h) pass **3,784 comparisons against the final exact ELF**: 3,584 startup/dispatch fixtures and 200 reset fixtures. [Exact validation](exact-build-validation.json), [build](build_offline.py), [stock addresses/hashes](function-bindings.json), [source/lead matrix](closure-matrix.json).

## Startup composition

The prior sealed one-time capture helper is reused unchanged. Two bounded helpers extend it through retention selection (continuation0x47FDD4) and through the TON critical section (continuation0x47FDF0). A third composes the entire suffix **0x47FC14..0x47FE12** through LP initialization, actual clock-mux helper and return. Original suffix execution receives the parent frame and R4=0x4002000C; the native helper returns normally. Scratch-register/frame layout is outside comparison scope. This does not reconstruct the earlier initializer prefix at0x47FAE8..0x47FC14.

Retention sets0x4002037C bit30, then0x40020380 bit16 and bit12 in order. The TON section saves/disables IRQs using real0x473940, calls slot8 initialization, requests TON update(0,cached GPU byte0x20074F60), and restores PRIMASK. NULL slot8 returns0; registered slot8 invokes earlier TON initialization. The helper0x4803AC is **TON initialization dispatch**, correcting the previous lead's LP-initialization label. LP initialization is0x4803F2/slot12; enable0x480408/slot13; disable0x48041E/slot14. All four wrappers are native and tested with NULL or native callbacks corresponding to the original registered addresses.

The suffix then invokes LP initialization, original clock-mux helper0x44B158, and, for major>=0x22, ORs0x400211C8 with6. Pinned source identifies this final register as MRAM auto-wakeup control; the stock instruction operation remains the authoritative layout. All tests compare ordered meaningful RAM/MMIO writes, cached TON fields and final PRIMASK. Registered TON/LP callbacks are native on the reconstruction side, original on the stock side. IRQ-save, generic TON dispatch, delay and buck-register providers remain original, with no successful-return stubs.

## PCM2.2 default reset

Native0x5A4E0C..0x5A4E5C separately validates the later reset body. It requires device/audio status words0x40021008/10 zero, enables peripheral29 (OTP), requests temperature-40 through actual wrapper0x480028, and waits through actual0x4807FC for0x400083E0 bit0 clear with argument2500. It returns1 for prerequisite/enable/temperature failure,4 for wait failure,0 for success. The2500 argument belongs to the shared delay-status API; these fixtures do not measure elapsed time.

Both sides register **actual PCM2.2 control0x5A490D**, unlike the preceding PCM2.1 suite. Thus this proves the new reset body with its correct control dependency, not native closure of every newer transition. OTP-ready response and timer release on read1/3 are explicitly synthetic; never-release fixtures run the actual timeout loop. NULL callback behavior is preserved. No device scheduling or physical timeout claim follows.

## Clock-mux boundary and continued leads

The composed suffix executes the real clock-mux helper, but fixtures use absent retained signature, so its active recovery branch is gated out. Pinned source `hal/mcu/am_hal_sysctrl.c:791` and signature header map it to `am_hal_sysctrl_clkmuxrst_low_power_init`: recovery requires !POASTAT and signature0x5AF0 in retained state0x40008858 high16. This is a concrete available-source lead, not missing tooling. Source describes HFRC/HFRC2/XTAL/external/PLL recovery and bus flush/delay dependencies; those need separate stock matching and readiness fixtures before native implementation claims.

The common initializer prefix has actual calls to trace-disable/peripheral disable, revision/INFO1 reads, callback registration, memory configuration and clock-gate configuration. Those source-backed leads remain open. Public SDK must not be copied wholesale: stock variant initialization and calibration paths already differ. No new download was needed; this is not source-search exhaustion.

## Preservation and limits

All1,342 current prior sealed entries (including requested1,328),110 audit inputs,four checkpoints and root index were checked before additive sealing. Existing source/tests were reused without edits. No commits, staging, firmware/device writes or production changes. Calibration/revision/MMIO are synthetic; startup SRAM and ITCM are authenticated. Full M55 exception behavior, physical rails/clocks and live task/IRQ quiescence remain unverified. No whole-initializer, full source-built subsystem or byte-identical OTA claim is made.
