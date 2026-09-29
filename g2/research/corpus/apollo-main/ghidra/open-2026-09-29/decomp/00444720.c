
undefined4 FUN_00444720(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  undefined1 auStack_48 [24];
  undefined1 auStack_30 [36];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  uVar2 = FUN_0047394c();
  *DAT_004448c4 = uVar2;
  FUN_00444694();
  FUN_004446b4();
  FUN_00439c04(auStack_48,PTR_DAT_004448c8,0x18);
  piVar1 = DAT_004448a4;
  iVar3 = osMessageQueueNew(0x60,0xc,auStack_48);
  *piVar1 = iVar3;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0044489c,DAT_00444898,PTR_s_ui_display_thread_startup_004448d0,0x43e,
                   PTR_s_dispThread_xQueue1_create_failed_004448cc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__display_thread_dispThread_xQueu_004448d4,
                          PTR_s__display_thread_dispThread_xQueu_004448d4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar3 = FUN_0046d8a0(DAT_004448b0,DAT_004448d8,0xa000);
    piVar1 = DAT_004448a0;
    if (iVar3 == 1) {
      iVar3 = osMutexNew(0);
      *piVar1 = iVar3;
      if (*piVar1 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0044489c,DAT_00444898,PTR_s_ui_display_thread_startup_004448d0,0x44a,
                       PTR_s_Failed_to_create_uart_sender_mut_004448e4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__display_thread_Failed_to_create_004448e8,
                              PTR_s__display_thread_Failed_to_create_004448e8);
        }
        uVar2 = 0xffffffff;
      }
      else {
        FUN_00439c04(auStack_30,PTR_DAT_004448ec,0x24);
        osThreadNew(PTR_FUN_004437e0_1_004448f0,0,auStack_30);
        uVar2 = 0;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0044489c,DAT_00444898,PTR_s_ui_display_thread_startup_004448d0,0x444,
                     PTR_s_lwrb_init_failed_004448dc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__display_thread_lwrb_init_failed_004448e0,
                            PTR_s__display_thread_lwrb_init_failed_004448e0);
      }
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

