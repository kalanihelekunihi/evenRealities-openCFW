
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e8008(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  uStack_18 = param_3;
  puStack_14 = param_4;
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    uVar3 = osKernelGetTickCount();
    puVar1 = _DAT_005e8124;
    iVar2 = FUN_005e7ea4(_DAT_005e8124,uVar3);
    if (iVar2 != 0) {
      *puVar1 = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_14 = PTR_s_voice_recording_60s_timeout_005e8160;
        uStack_18 = 0x62;
        FUN_0043d574(3,PTR_s_terminal_timer_005e8134,PTR_s_D__01_workspace_s200_ap510b_iar__005e8130
                     ,PTR_s_terminal_timer_process_auto_refl_005e8164);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_timer_voice_recording_6_005e8168,
                            PTR_s__terminal_timer_voice_recording_6_005e8168);
      }
      FUN_0043c0e4(&uStack_18,1,0);
      uStack_18 = CONCAT31(uStack_18._1_3_,3);
      APP_PbTerminalTxEncodeVoiceInput(&uStack_18);
      terminal_request_display(9,1);
    }
    iVar2 = FUN_005e7ea4(puVar1 + 8,uVar3);
    if (iVar2 != 0) {
      puVar1[8] = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_14 = PTR_s_asr_result_wait_20s_timeout__bac_005e816c;
        uStack_18 = 0x6d;
        FUN_0043d574(2,PTR_s_terminal_timer_005e8134,PTR_s_D__01_workspace_s200_ap510b_iar__005e8130
                     ,PTR_s_terminal_timer_process_auto_refl_005e8164);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__terminal_timer_asr_result_wait_2_005e8170,
                            PTR_s__terminal_timer_asr_result_wait_2_005e8170);
      }
      terminal_request_display(0xc,0);
    }
    if (*(char *)(_DAT_005e8174 + 0x275) == '\a') {
      iVar2 = td_counter_b_get();
      iVar4 = td_record_elapsed_get(iVar2,&puStack_14);
      if (iVar4 == 0) {
        *(undefined4 *)(puVar1 + 0x10) = 0;
        *(undefined4 *)(puVar1 + 0x14) = 0;
      }
      else if ((*(int *)(puVar1 + 0x10) != iVar2) || (*(undefined **)(puVar1 + 0x14) != puStack_14))
      {
        *(int *)(puVar1 + 0x10) = iVar2;
        *(undefined **)(puVar1 + 0x14) = puStack_14;
        terminal_request_display(0x14,puStack_14);
      }
    }
    else {
      *(undefined4 *)(puVar1 + 0x10) = 0;
      *(undefined4 *)(puVar1 + 0x14) = 0;
    }
  }
  return CONCAT44(puStack_14,uStack_18);
}

