
int delete_all_files_in_dir(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 auStack_154 [80];
  
  iVar1 = file_opendir(param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0045927c,DAT_00459278,PTR_s_delete_all_files_in_dir_00459288,0x7a,
                   PTR_s_Failed_to_open_directory___s_00459284,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__logger_setting_Failed_to_open_d_0045928c,
                          PTR_s__logger_setting_Failed_to_open_d_0045928c,param_1);
    }
    iVar2 = -1;
  }
  else {
    iVar2 = 0;
    while (iVar3 = file_readdir(iVar1), iVar3 != 0) {
      iVar4 = FUN_0046cacc(iVar3,0x4591fc);
      if (((iVar4 != 0) && (iVar4 = FUN_0046cacc(iVar3,0x459200), iVar4 != 0)) &&
         (*(char *)(iVar3 + 0x100) == '\b')) {
        FUN_0044b728(auStack_154,0x140,PTR_s__s__s_00459290,param_1,iVar3);
        iVar3 = file_remove(auStack_154);
        if (iVar3 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0045927c,DAT_00459278,PTR_s_delete_all_files_in_dir_00459288,0x8f,
                         PTR_s_Deleted_file___s_00459294,auStack_154);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__logger_setting_Deleted_file___s_00459298,
                                PTR_s__logger_setting_Deleted_file___s_00459298,auStack_154);
          }
          iVar2 = iVar2 + 1;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0045927c,DAT_00459278,PTR_s_delete_all_files_in_dir_00459288,0x92,
                         PTR_s_Failed_to_delete_file___s_0045929c,auStack_154);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__logger_setting_Failed_to_delete_004592a0,
                                PTR_s__logger_setting_Failed_to_delete_004592a0,auStack_154);
          }
        }
      }
    }
    file_closedir(iVar1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      auStack_154[0] = param_1;
      FUN_0043d574(4,DAT_0045927c,DAT_00459278,PTR_s_delete_all_files_in_dir_00459288,0x98,
                   PTR_s_Deleted__d_files_from__s_004592a4,iVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__logger_setting_Deleted__d_files_004592a8,
                          PTR_s__logger_setting_Deleted__d_files_004592a8,iVar2,param_1);
    }
  }
  return iVar2;
}

