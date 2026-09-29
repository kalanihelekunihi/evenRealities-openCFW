
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0045be6c(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  iVar3 = FUN_0045a568();
  piVar1 = DAT_0045bff0;
  if (iVar3 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x2e4;
      param_3 = PTR_s_slave_role_don_t_need_to_cancel_b_0045c03c;
      FUN_0043d574(3,PTR_s_sync_module_framework_0045c010,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                   PTR_s_DispStartBlockingCancel_0045c040,0x2e4,
                   PTR_s_slave_role_don_t_need_to_cancel_b_0045c03c,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__sync_module_framework_slave_rol_0045c044,
                          PTR_s__sync_module_framework_slave_rol_0045c044);
    }
  }
  else if (*DAT_0045bff0 == 0) {
    *DAT_0045bff4 = 0;
  }
  else {
    iVar3 = osMutexAcquire(*DAT_0045bff0,0xffffffff);
    piVar2 = _DAT_0045c018;
    if (iVar3 == 0) {
      if ((*_DAT_0045c018 != 0) && (iVar3 = osTimerIsRunning(*_DAT_0045c018), iVar3 != 0)) {
        osTimerStop(*piVar2);
      }
      *DAT_0045bff4 = 0;
      osMutexRelease(*piVar1);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x2f7;
        param_3 = PTR_s_DispStartBlockingCancel__flag_cl_0045c050;
        FUN_0043d574(4,PTR_s_sync_module_framework_0045c010,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                     PTR_s_DispStartBlockingCancel_0045c040);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__sync_module_framework_DispStart_0045c054,
                            PTR_s__sync_module_framework_DispStart_0045c054);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x2ec;
        param_3 = PTR_s_DispStartBlockingCancel__mutex_a_0045c048;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045c010,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                     PTR_s_DispStartBlockingCancel_0045c040,0x2ec,
                     PTR_s_DispStartBlockingCancel__mutex_a_0045c048,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_DispStart_0045c04c,
                            PTR_s__sync_module_framework_DispStart_0045c04c);
      }
      *DAT_0045bff4 = 0;
    }
  }
  return CONCAT44(param_3,param_2);
}

