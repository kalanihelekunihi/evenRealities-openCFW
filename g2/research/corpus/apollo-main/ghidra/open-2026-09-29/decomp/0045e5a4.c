
undefined8 FUN_0045e5a4(undefined4 param_1,code *param_2,undefined *param_3,undefined *param_4)

{
  int iVar1;
  code *pcVar2;
  
  pcVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    pcVar2 = (code *)0x5d3;
    param_3 = PTR_s__s__timeout_running_0045ebb4;
    param_4 = PTR_s__MasterDisplayCmd_TimeoutListene_0045ebb0;
    FUN_0043d574(3,PTR_s_sync_module_framework_0045e8c0,
                 PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                 PTR_s__MasterDisplayCmd_TimeoutListene_0045ebb0,0x5d3,
                 PTR_s__s__timeout_running_0045ebb4,PTR_s__MasterDisplayCmd_TimeoutListene_0045ebb0)
    ;
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__sync_module_framework__s__timeo_0045ebb8,
                        PTR_s__sync_module_framework__s__timeo_0045ebb8,
                        PTR_s__MasterDisplayCmd_TimeoutListene_0045ebb0,pcVar2,param_3,param_4);
  }
  if (param_2 != (code *)0x0) {
    pcVar2 = (code *)0x0;
    iVar1 = FUN_00491184(PTR_FUN_0045ade8_1_0045eb88,0,param_2,0xfffffffe);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        pcVar2 = (code *)0x5d6;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045e8c0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                     PTR_s__MasterDisplayCmd_TimeoutListene_0045ebb0,0x5d6,
                     PTR_s_submit_work_failed__0045eb8c);
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

