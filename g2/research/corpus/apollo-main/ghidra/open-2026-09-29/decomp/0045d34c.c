
undefined8 FUN_0045d34c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_0045dd38;
  iVar3 = osSemaphoreNew(0xffff,0,0,param_4,param_3,param_4);
  *piVar1 = iVar3;
  piVar2 = DAT_0045dd48;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x459;
      FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                   PTR_s_SyncTimeoutDetectionThreadStartu_0045dd40,0x459,
                   PTR_s_create_timeout_detection_semapho_0045dd3c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sync_module_framework_create_ti_0045dd44);
    }
    uVar4 = 0xffffffff;
  }
  else {
    iVar3 = osTimerNew(PTR_FUN_0045d302_1_0045dd4c,1,0,0);
    *piVar2 = iVar3;
    if (*piVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x45f;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                     PTR_s_SyncTimeoutDetectionThreadStartu_0045dd40,0x45f,
                     PTR_s_create_timeout_detection_timer_f_0045dd50);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_create_ti_0045dd54,
                            PTR_s__sync_module_framework_create_ti_0045dd54);
      }
      uVar4 = 0xffffffff;
    }
    else {
      iVar3 = osTimerStart(*piVar2,100);
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_3 = 0x468;
          FUN_0043d574(4,PTR_s_sync_module_framework_0045d7d0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                       PTR_s_SyncTimeoutDetectionThreadStartu_0045dd40,0x468,
                       PTR_s_sync_timeout_detection_task_init_0045dd60);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_sync_time_0045dfcc,
                              PTR_s__sync_module_framework_sync_time_0045dfcc);
        }
        uVar4 = 0;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_3 = 0x465;
          FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                       PTR_s_SyncTimeoutDetectionThreadStartu_0045dd40,0x465,
                       PTR_s_start_timeout_detection_timer_fa_0045dd58);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__sync_module_framework_start_tim_0045dd5c,
                              PTR_s__sync_module_framework_start_tim_0045dd5c);
        }
        uVar4 = 0xffffffff;
      }
    }
  }
  return CONCAT44(param_3,uVar4);
}

