
int tracepoint_delete_all_files(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  undefined4 uStack_64;
  undefined1 auStack_60 [80];
  undefined4 uStack_10;
  
  uVar1 = DAT_005ee884;
  uStack_10 = in_r3;
  iVar2 = file_opendir(DAT_005ee884);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005ee79c,DAT_005ee798,PTR_s_tracepoint_delete_all_files_005eefe0,0x17b,
                   PTR_s_open_tracepoint_dir_failed_for_d_005eefdc,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__tp_setting_open_tracepoint_dir_f_005eefe4,
                          PTR_s__tp_setting_open_tracepoint_dir_f_005eefe4,uVar1);
    }
    iVar3 = -1;
  }
  else {
    FUN_0047e088();
    iVar3 = 0;
    while (iVar4 = file_readdir(iVar2), iVar4 != 0) {
      uStack_64 = 0;
      if ((*(char *)(iVar4 + 0x100) == '\b') &&
         (iVar4 = tracepoint_parse_file_sequence(iVar4,&uStack_64), iVar4 != 0)) {
        tracepoint_format_file_path(auStack_60,0x50,uStack_64);
        iVar4 = file_remove(auStack_60);
        if (iVar4 == 0) {
          iVar3 = iVar3 + 1;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,PTR_s_tracepoint_delete_all_files_005eefe0,399,
                         PTR_s_tracepoint_delete_all_removed____005eefe8,auStack_60);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__tp_setting_tracepoint_delete_al_005eefec,
                                PTR_s__tp_setting_tracepoint_delete_al_005eefec,auStack_60);
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(2,DAT_005ee79c,DAT_005ee798,PTR_s_tracepoint_delete_all_files_005eefe0,
                         0x191,PTR_s_tracepoint_delete_failed___s_005eeff0,auStack_60);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__tp_setting_tracepoint_delete_fa_005eeff4,
                                PTR_s__tp_setting_tracepoint_delete_fa_005eeff4,auStack_60);
          }
        }
      }
    }
    file_closedir(iVar2);
  }
  return iVar3;
}

