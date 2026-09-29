
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 scan_log_files(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 uStack_158;
  undefined *puStack_154;
  int iStack_150;
  undefined4 uStack_14c;
  uint uStack_148;
  
  iVar2 = _DAT_00459d58;
  FUN_0043c0e4(_DAT_00459d58,0x328,0);
  iVar1 = file_opendir(PTR_DAT_004592ac);
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_154 = PTR_s_Failed_to_open__log_directory_004592b0;
      uStack_158 = 0xa8;
      FUN_0043d574(1,DAT_0045927c,DAT_00459278,PTR_s_scan_log_files_004592b4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__logger_setting_Failed_to_open___004592b8,
                          PTR_s__logger_setting_Failed_to_open___004592b8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar6 = 0;
    while ((iVar4 = file_readdir(iVar1), iVar4 != 0 && (uVar6 < 0x14))) {
      iVar5 = FUN_0046cacc(iVar4,0x4591fc);
      if ((iVar5 != 0) && (iVar5 = FUN_0046cacc(iVar4,0x459200), iVar5 != 0)) {
        iVar5 = FUN_0046cacc(iVar4,PTR_s_compress_manager_bin_004592bc);
        if (iVar5 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            puStack_154 = PTR_s_compress_manager_log_not_to_send_004592c0;
            uStack_158 = 0xb7;
            FUN_0043d574(4,DAT_0045927c,DAT_00459278,PTR_s_scan_log_files_004592b4);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__logger_setting_compress_manager_004592c4);
          }
        }
        else {
          FUN_0044b5a0(uVar6 * 0x28 + iVar2,iVar4,0x1f);
          *(undefined1 *)(uVar6 * 0x28 + iVar2 + 0x1f) = 0;
          *(undefined1 *)(uVar6 * 0x28 + iVar2 + 0x24) = *(undefined1 *)(iVar4 + 0x100);
          if (*(char *)(iVar4 + 0x100) == '\b') {
            FUN_0044b728(&uStack_158,0x140,PTR_s__log__s_004592c8,iVar4);
            uVar3 = logger_file_size(&uStack_158);
            *(undefined4 *)(uVar6 * 0x28 + iVar2 + 0x20) = uVar3;
            *(int *)(iVar2 + 0x324) =
                 *(int *)(uVar6 * 0x28 + iVar2 + 0x20) + *(int *)(iVar2 + 0x324);
          }
          else {
            *(undefined4 *)(uVar6 * 0x28 + iVar2 + 0x20) = 0;
          }
          uVar6 = uVar6 + 1;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            uStack_148 = (uint)*(byte *)(iVar4 + 0x100);
            uStack_14c = *(undefined4 *)(uVar6 * 0x28 + iVar2 + -8);
            puStack_154 = PTR_s_Found___s__size___d_bytes__type__004592cc;
            uStack_158 = 0xd1;
            iStack_150 = iVar4;
            FUN_0043d574(4,DAT_0045927c,DAT_00459278,PTR_s_scan_log_files_004592b4);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            puStack_154 = (undefined *)(uint)*(byte *)(iVar4 + 0x100);
            uStack_158 = *(undefined4 *)(iVar2 + uVar6 * 0x28 + -8);
            compress_log_output(0x10c00000,PTR_s__logger_setting_Found___s__size__004592d0,
                                PTR_s__logger_setting_Found___s__size__004592d0,iVar4);
          }
        }
      }
    }
    *(uint *)(iVar2 + 800) = uVar6;
    file_closedir(iVar1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_14c = *(undefined4 *)(iVar2 + 0x324);
      iStack_150 = *(int *)(iVar2 + 800);
      puStack_154 = PTR_s_Total__d_files_found_in__log__to_004592d4;
      uStack_158 = 0xd8;
      FUN_0043d574(4,DAT_0045927c,DAT_00459278,PTR_s_scan_log_files_004592b4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uStack_158 = *(undefined4 *)(iVar2 + 0x324);
      compress_log_output(0x10800000,PTR_s__logger_setting_Total__d_files_f_004592d8,
                          PTR_s__logger_setting_Total__d_files_f_004592d8,
                          *(undefined4 *)(iVar2 + 800));
    }
    uVar3 = 0;
  }
  return uVar3;
}

