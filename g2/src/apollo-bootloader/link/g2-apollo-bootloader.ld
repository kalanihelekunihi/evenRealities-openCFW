/*
 * openCFW G2 apollo-bootloader GNU linker script (g2c wave 6).
 * Stock bootloader linked at 0x00410000 (firmware-formats.md);
 * image ends ~0x00434477; free headroom to 0x00438000.
 */
ENTRY(opencfw_boot_reset_entry)

MEMORY
{
  /* Wave 12: region is 0x410000..0x438000 (LENGTH 0x28000). Evidence: apollo-main image base is
   * 0x438000 (stock main.bin base, g2-apollo-main.ld ORIGIN); stock bootloader f89a4c46 is 148599
   * bytes (corpus RUN.json image_size) = ends 0x434477. Overlap with apollo-main now fails the link. */
  MRAM  (rx)  : ORIGIN = 0x00410000, LENGTH = 0x00028000
  /* Stock RAM map (IAR init records at 0x415326/0x431e38, mirrored in
   * startup/init_records.S): initialized cells 0x20000000..0x2000055c, zeroed
   * cells 0x2000055c..0x200271c8, stack limit 0x2007d000 (reset.S), MSP top
   * 0x2007fb00, SSRAM records at 0x20080000 and 0x20081000..0x200f5100.
   * Sources address those cells by number, so the linker may only place
   * objects there at their stock address (pinned sections below). DTCM_FREE
   * is the gap stock leaves between its zeroed cells and the stack. */
  DTCM_STOCK (rw) : ORIGIN = 0x20000000, LENGTH = 0x000271c8
  DTCM_FREE  (rw) : ORIGIN = 0x200271c8, LENGTH = 0x2007d000 - 0x200271c8
}

SECTIONS
{
  .text : {
    /* Wave 12: stock vector table (256 words) is at 0x410000; first function lfs_max at 0x410400
     * (corpus functions-000.jsonl). Previously .boot_vectors was an orphan placed at ~0x439964. */
    KEEP(*(.boot_vectors))
    KEEP(*(.isr_vector))
    *(.text .text.* .opencfw.*)
    *(.rodata .rodata.*)
    . = ALIGN(4);
    /* Stock-placed tables/strings (boot, event and cmdq named sections): kept under --gc-sections. */
    KEEP(*(.boot_* .event_* .cmdq_*))
    . = ALIGN(4);
  } > MRAM

  .ARM.exidx : { *(.ARM.exidx .ARM.exidx.*) } > MRAM

  /* Zero-init objects at their stock addresses. Each lies in the stock zero
   * record (0x2000055c..0x200271c8), which startup clears, and each address is
   * the literal stock code loads: IOM 0x42cdb4 (claim 0x42c4c6, 8 x 0x8a8),
   * UART g_am_hal_uart_states 0x4233e4 (4 x 0x11c), ADC 0x42f150 (0x48), SYSPLL 0x4275a4
   * (am_hal_syspll_initialize 0x4272ac, 1 x 8). Listed before .bss so the
   * generic pattern cannot claim them. */
  .boot_iom_context_pool 0x2001455c (NOLOAD) : {
    *(.bss.boot_iom_context_pool)
    ASSERT(ABSOLUTE(.) <= 0x20018a9c, "IOM contexts exceed the stock 8 x 0x8a8 pool");
  }
  .boot_uart_context_pool 0x20024400 (NOLOAD) : {
    *(.bss.g_am_hal_uart_states)
    ASSERT(ABSOLUTE(.) <= 0x20024870, "UART contexts exceed the stock 4 x 0x11c pool");
  }
  .boot_adc_context_pool 0x20026df0 (NOLOAD) : {
    *(.bss.boot_adc_context_pool)
    ASSERT(ABSOLUTE(.) <= 0x20026e38, "ADC context exceeds the stock 0x48 slot");
  }
  /* g_MSPIState (upstream am_hal_mspi.c, 4 x 0x8d0): stock
   * am_hal_mspi_initialize 0x424a5a loads 0x2001caa0. */
  .boot_mspi_state 0x2001caa0 (NOLOAD) : {
    *(.bss.g_MSPIState)
    ASSERT(ABSOLUTE(.) <= 0x2001ede0, "g_MSPIState exceeds the stock 4 x 0x8d0 table");
  }
  /* gAmHalCmdq (upstream am_hal_cmdq.c, 12 x 0x2c): stock am_hal_cmdq_init
   * 0x427794 loads 0x200262f0. */
  .boot_cmdq_state 0x200262f0 (NOLOAD) : {
    *(.bss.gAmHalCmdq)
    ASSERT(ABSOLUTE(.) <= 0x20026500, "gAmHalCmdq exceeds the stock 12 x 0x2c table");
  }
  .boot_syspll_state 0x20027010 (NOLOAD) : {
    *(.bss.g_SysPLLState)
    ASSERT(ABSOLUTE(.) <= 0x20027018, "g_SysPLLState exceeds the stock 8-byte slot");
  }

  /* Upstream SDK 5.0.0 am_hal_pwrctrl.c state at the cells stock code loads
   * (0x41b918 TrimVersionGet, 0x41b954 mcu_hp_lp_switch_sequence, 0x41bae8
   * gpu_mode_select, 0x41bbd0 mcu_memory_config, 0x41c320 INFO1_populate,
   * 0x41c4b4 low_power_init). The three initialized cells lie in the stock
   * initialized record (0x20000000..0x2000055c), whose recovered image already
   * holds the SDK initializers (0xffffffff, {0,7,0,3,0}, LOW_POWER = 1), so
   * they are NOLOAD here like the zeroed cells. */
  .boot_pwrctrl_trimver 0x20000098 (NOLOAD) : { *(.data.g_ui32TrimVer) }
  .boot_pwrctrl_memcfg 0x2000009c (NOLOAD) : { *(.data.g_DefaultMcuMemCfg) }
  .boot_pwrctrl_mcumode 0x20000552 (NOLOAD) : { *(.data.g_eCurMcuPwrMode) }
  .boot_pwrctrl_info1 0x200267f8 (NOLOAD) : {
    *(.bss.g_sINFO1regs)
    ASSERT(ABSOLUTE(.) <= 0x20026878, "g_sINFO1regs exceeds the stock 0x80-byte block");
  }
  /* g_orig_* trim snapshots, stock 0x2002704c..0x2002708c in declaration
   * order. Only the five external ones survive here: clang drops the eleven
   * write-only statics (g_orig_ACTTRIMVDDF..g_orig_VDDFACTHIGHTONTRIM, marked
   * "set but not used" in the SDK), whose stock cells 0x20027060..0x2002708c
   * nothing reads. */
  .boot_pwrctrl_trims 0x2002704c (NOLOAD) : {
    *(.bss.g_orig_TVRGCVREFTRIM) *(.bss.g_orig_TVRGFVREFTRIM)
    *(.bss.g_orig_VDDCLKGTRIM) *(.bss.g_orig_CORELDOTEMPCOTRIM)
    *(.bss.g_orig_CORELDOACTIVETRIM)
    ASSERT(ABSOLUTE(.) == 0x20027060, "g_orig_* trims do not fill stock 0x2002704c..0x20027060");
  }
  .boot_pwrctrl_modes 0x200271a5 (NOLOAD) : {
    *(.bss.g_eCurGpuPwrMode) *(.bss.g_ePreGpuPwrMode)
    *(.bss.g_eCurROMPwrMode) *(.bss.g_bOrigTrimsStored)
    ASSERT(ABSOLUTE(.) == 0x200271a9, "pwrctrl mode bytes do not fill stock 0x200271a5..0x200271a9");
  }
  /* am_hal_debug.c trace-enable count (hand debug code,
   * initializer-callbacks/startup_shutdown.c). */
  .boot_debug_trcena 0x200271a3 (NOLOAD) : { *(.bss.g_ui8TRCENAcount) }

  /* Upstream SPOTMGR (SDK 5.0.0 + AmbiqSuite patch 66185cb) state. Stock
   * (armlink) lays each kind of data out per object in file-name order:
   * am_hal_spotmgr.c, then _pcm0_7, _pcm2_0, _pcm2_1, _pcm2_2, then
   * am_hal_stimer.c and am_hal_sysctrl.c. Statics another SPOTMGR file also
   * declares carry a _pcmX_Y suffix in the generated copies. Clang keeps
   * g_ui32PwrStVdd{c,f}VoltLvl (stock 0x200000a4/0x200000f4) in flash because
   * nothing writes them; the recovered SRAM image still fills those cells. */
  .boot_spotmgr_info1 0x20026ba0 (NOLOAD) : {
    *(.bss.g_sSpotMgrINFO1regs)
    ASSERT(ABSOLUTE(.) == 0x20026c0c, "g_sSpotMgrINFO1regs does not fill stock 0x20026ba0..0x20026c0c");
  }
  .boot_spotmgr_state 0x20026e38 (NOLOAD) : {
    *(.bss.g_sSpotMgr)
    ASSERT(ABSOLUTE(.) == 0x20026e74, "g_sSpotMgr does not fill stock 0x20026e38..0x20026e74");
  }
  .boot_spotmgr_words 0x2002708c (NOLOAD) : {
    *(.bss.g_sSpotMgrProfile)
    *(.bss.g_ui32CurCORELDOTEMPCOTRIMLDO_pcm0_7) *(.bss.g_ui32CurMEMLDOACTIVETRIMLDO_pcm0_7)
    *(.bss.g_ui32CurCORELDOTEMPCOTRIMLDO_pcm2_0) *(.bss.g_ui32CurCORELDOTEMPCOTRIMBuck)
    *(.bss.g_ui32CurMEMLDOACTIVETRIMLDO_pcm2_0)
    *(.bss.g_i32CORELDODiff) *(.bss.g_ui32NewVddcTrim_pcm2_1) *(.bss.g_ui32NewVddfTrim_pcm2_1)
    *(.bss.g_ui32NewVddcTrim_pcm2_2) *(.bss.g_ui32NewVddfTrim_pcm2_2)
    *(.bss.g_ui32NewCoreldoActTrim) *(.bss.g_ui32NewCoreldoTempcoTrim)
    *(.bss.g_ui32TargetTonState) *(.bss.g_ui32TargetPowerState)
    ASSERT(ABSOLUTE(.) == 0x200270c8, "SPOTMGR words do not fill stock 0x2002708c..0x200270c8");
  }
  .boot_spotmgr_bytes 0x200271a9 (NOLOAD) : {
    *(.bss.g_bIsPCM2p1) *(.bss.g_bIsPCM1p0OrPCM1p1) *(.bss.g_bIsB0PCM1p1OrNewer)
    *(.bss.g_bIsPCM2p0) *(.bss.g_bIsPCM2p2OrNewer) *(.bss.g_bIsPCM2p1WoPatch)
    *(.bss.g_bVddcaorVddcpuOverride) *(.bss.g_bHpToDeepSleep) *(.bss.g_bVddfLpMinusForLp)
    *(.bss.g_bSwitchingToHp)
    *(.bss.g_bIsB0Pcm1p0) *(.bss.g_bIsPCM1p0Or1p1) . = 0x200271b6 - 0x200271a9;
    *(.bss.g_bPostponeTempco) *(.bss.g_bTempcoPending) *(.bss.bSimoLPAutoSwitch)
    *(.bss.g_eTempCoRange)
    *(.bss.am_hal_spotmgr_pcm2_1_power_state_update.eCurTempRangeStatic)
    *(.bss.am_hal_spotmgr_pcm2_1_power_state_update.eLastCpuStateStatic)
    *(.bss.g_bContinueSeq21b)
    *(.bss.am_hal_spotmgr_pcm2_2_power_state_update.eCurTempRangeStatic)
    *(.bss.am_hal_spotmgr_pcm2_2_power_state_update.eLastCpuStateStatic)
    ASSERT(ABSOLUTE(.) == 0x200271bf, "SPOTMGR bytes do not fill stock 0x200271a9..0x200271bf");
  }
  /* am_hal_sysctrl.c g_bFrcBuckAct (hand sleep code, thread-creation/idle_sleep/sysctrl_sleep.c). */
  .boot_sysctrl_frcbuck 0x200271c0 (NOLOAD) : { *(.bss.g_bFrcBuckAct) }
  /* Initialized SPOTMGR cells: the recovered SRAM image (startup/initialized_data.c)
   * already holds the SDK initializers 7, 7, 6, 7, 0xff, 6, true, the PCM0.7 TON
   * trims 0x0d 0x0d 0x0b 0x0b 0x12 0x19 and AM_HAL_SPOTMGR_TRANS_SEQ_INVALID. */
  .boot_spotmgr_pcm21_data 0x20000144 (NOLOAD) : {
    *(.data.g_ui32CurPowerStateStatic_pcm2_1)
    *(.data.spotmgr_power_trims_update.ui32BasePwrStateStatic)
    *(.data.am_hal_spotmgr_pcm2_1_power_state_update.ui32CurTonStateStatic)
    *(.data.g_ui32CurPowerStateStatic_pcm2_2) *(.data.g_ui32LastStateBfStartTimer)
    ASSERT(ABSOLUTE(.) == 0x20000158, "SPOTMGR words do not fill stock 0x20000144..0x20000158");
  }
  /* PCM2.2 transition table: its 27 pointers name upstream static functions, so
   * startup copies this section's load image (opencfw_boot_install_initialized_data). */
  .boot_spotmgr_seq 0x20000158 : {
    __boot_spotmgr_seq_start = ABSOLUTE(.);
    *(.data.powerStateTransitionSeq)
    __boot_spotmgr_seq_end = ABSOLUTE(.);
    ASSERT(ABSOLUTE(.) == 0x200001c4, "powerStateTransitionSeq does not fill stock 0x20000158..0x200001c4");
  } AT > MRAM
  __boot_spotmgr_seq_load = LOADADDR(.boot_spotmgr_seq);
  .boot_spotmgr_ton 0x200001c4 (NOLOAD) : {
    *(.data.am_hal_spotmgr_pcm2_2_power_state_update.ui32CurTonStateStatic)
  }
  .boot_spotmgr_data_bytes 0x20000553 (NOLOAD) : {
    *(.data.g_bTempLessThan50C)
    *(.data.g_ui8VddcActLowTonTrim) *(.data.g_ui8VddcActHighTonTrim)
    *(.data.g_ui8VddcLvActLowTonTrim) *(.data.g_ui8VddcLvActHighTonTrim)
    *(.data.g_ui8VddfActLowTonTrim) *(.data.g_ui8VddfActHighTonTrim)
    *(.data.eOngoingSeq)
    ASSERT(ABSOLUTE(.) == 0x2000055b, "SPOTMGR bytes do not fill stock 0x20000553..0x2000055b");
  }

  .data : ALIGN(4) {
    __data_start = .;
    *(.data .data.*)
    . = ALIGN(4);
    __data_end = .;
  } > DTCM_FREE AT > MRAM
  __data_load_start = LOADADDR(.data);

  .bss (NOLOAD) : ALIGN(4) {
    __bss_start = .;
    *(.bss .bss.* COMMON)
    . = ALIGN(4);
    __bss_end = .;
  } > DTCM_FREE

  /* Startup runs only the stock init records; nothing copies .data or clears
   * .bss here. A new object must get a pinned stock address above, or a
   * matching init record, before it can link. */
  ASSERT(__data_end == __data_start, "unpinned .data: startup never copies it")
  ASSERT(__bss_end == __bss_start, "unpinned .bss: startup never clears it")

/* Resident ROM Thumb ABS symbols come from resident_rom_thumb_set.c
 * at final link (.thumb_set → typed STT_FUNC). Compose may still
 * --defsym them for relocatable 0-undef checks.
 */
}
