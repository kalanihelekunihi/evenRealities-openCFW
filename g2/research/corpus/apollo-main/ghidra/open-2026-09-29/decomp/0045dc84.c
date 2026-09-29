
undefined8 FUN_0045dc84(undefined4 param_1,code *param_2,undefined *param_3,undefined *param_4)

{
  int iVar1;
  code *pcVar2;
  
  pcVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    pcVar2 = (code *)0x519;
    param_3 = PTR_s__s__timeout_running_0045e004;
    param_4 = PTR_s__SlaveScheduleModuleDataCmd_Time_0045e65c;
    FUN_0043d574(4,PTR_s_sync_module_framework_0045e014,
                 PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                 PTR_s__SlaveScheduleModuleDataCmd_Time_0045e65c,0x519,
                 PTR_s__s__timeout_running_0045e004,PTR_s__SlaveScheduleModuleDataCmd_Time_0045e65c)
    ;
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__sync_module_framework__s__timeo_0045e008,
                        PTR_s__sync_module_framework__s__timeo_0045e008,
                        PTR_s__SlaveScheduleModuleDataCmd_Time_0045e65c,pcVar2,param_3,param_4);
  }
  if (param_2 != (code *)0x0) {
    pcVar2 = (code *)0x0;
    iVar1 = FUN_00491184(PTR_FUN_0045ade8_1_0045dff4,0,param_2,0xfffffffe);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        pcVar2 = (code *)0x51c;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045e014,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                     PTR_s__SlaveScheduleModuleDataCmd_Time_0045e65c,0x51c,
                     PTR_s_submit_work_failed__0045dff8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                            PTR_s__sync_module_framework_submit_wo_0045e654);
      }
      (*param_2)(0xfffffffe);
    }
  }
  return CONCAT44(pcVar2,3);
}

