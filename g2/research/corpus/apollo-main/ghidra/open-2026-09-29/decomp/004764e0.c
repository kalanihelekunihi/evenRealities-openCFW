
undefined8
fw_event_loop_initialize
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_00476bf0;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_00476bf0 == 0) {
    iVar2 = osMessageQueueNew(0xf,8,PTR_DAT_00476bf4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_s__fw_evt_loop_init_osMessageQueue_00476bf8;
        local_10 = 0x58;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,PTR_s_fw_evt_loop_init_00476bfc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00476c08);
      }
    }
  }
  piVar1 = DAT_00476c0c;
  if (*DAT_00476c0c == 0) {
    iVar2 = osTimerNew(0x4767a9,0,0,PTR_DAT_00476c10);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_s__fw_evt_loop_init_osTimerNew__fa_00476c14;
        local_10 = 0x61;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,PTR_s_fw_evt_loop_init_00476bfc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evtloop__fw_evt_loop_init_osTim_00476c18,
                            PTR_s__evtloop__fw_evt_loop_init_osTim_00476c18);
      }
    }
  }
  piVar1 = DAT_00476c1c;
  if (*DAT_00476c1c == 0) {
    iVar2 = osMutexNew(PTR_DAT_00476c20);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_s_Warning__failed_to_Create_fw_evt_00476c24;
        local_10 = 0x6a;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,PTR_s_fw_evt_loop_init_00476bfc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evtloop_Warning__failed_to_Crea_00476c28,
                            PTR_s__evtloop_Warning__failed_to_Crea_00476c28);
      }
    }
  }
  piVar1 = DAT_00476c2c;
  if (*DAT_00476c2c != 0) {
    osThreadTerminate(*DAT_00476c2c);
    *piVar1 = 0;
  }
  if (*piVar1 == 0) {
    iVar2 = osThreadNew(0x476681,0,PTR_DAT_00476c30);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_s__fw_evt_loop_init_osThreadNew__f_00476c34;
        local_10 = 0x79;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,PTR_s_fw_evt_loop_init_00476bfc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evtloop__fw_evt_loop_init_osThr_00476c38,
                            PTR_s__evtloop__fw_evt_loop_init_osThr_00476c38);
      }
    }
  }
  return CONCAT44(local_c,local_10);
}

