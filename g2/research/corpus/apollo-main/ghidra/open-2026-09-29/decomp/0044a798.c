
void compress_log_sync_to_files(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 local_50;
  undefined4 local_4c;
  uint local_48;
  
  if ((param_1 != 0) && (param_2 != 0)) {
    if (*DAT_0044a9c8 == '\0') {
      compress_log_manager_load();
    }
    iVar4 = DAT_0044a9bc;
    if (*(char *)(DAT_0044a9bc + 6) == '\0') {
      *(undefined1 *)(DAT_0044a9bc + 6) = 1;
    }
    for (uVar5 = 0; uVar5 < param_2; uVar5 = uVar6 + uVar5) {
      uVar2 = 0x7d000 - *(int *)(iVar4 + 8);
      if (uVar2 == 0) {
        compress_log_rotate_file();
        uVar2 = 0x7d000;
      }
      uVar6 = param_2 - uVar5;
      if (uVar2 < param_2 - uVar5) {
        uVar6 = uVar2;
      }
      compress_log_path_format(*(undefined1 *)(iVar4 + 4),&local_50,0x30);
      iVar3 = file_open(&local_50,&DAT_0044a8fc);
      if (iVar3 == 0) {
        iVar3 = file_open(&local_50,&LAB_0044a900);
        if (iVar3 == 0) {
          return;
        }
        *(undefined4 *)(iVar4 + 8) = 0;
        iVar1 = _write_file_version_header(iVar3);
        if (iVar1 != 0) {
          *(int *)(iVar4 + 8) = iVar1;
        }
        uVar2 = 0x7d000 - *(int *)(iVar4 + 8);
        if (uVar2 < uVar6) {
          uVar6 = uVar2;
        }
      }
      file_seek(iVar3,*(undefined4 *)(iVar4 + 8),0);
      uVar2 = file_write(param_1 + uVar5,1,uVar6,iVar3);
      file_close(iVar3);
      if (uVar2 != uVar6) break;
      *(uint *)(iVar4 + 8) = uVar6 + *(int *)(iVar4 + 8);
      compress_log_manager_save();
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_4c = DAT_0044a9f4;
      local_50 = 0x115;
      local_48 = uVar5;
      FUN_0043d574(4,DAT_0044a9e4,DAT_0044a9e0,DAT_0044a9f8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0044a9fc,DAT_0044a9fc,uVar5);
    }
  }
  return;
}

