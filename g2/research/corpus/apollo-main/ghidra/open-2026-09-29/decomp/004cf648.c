
int FUN_004cf648(int param_1)

{
  int iVar1;
  undefined4 local_48;
  undefined *local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined1 *local_2c;
  undefined1 auStack_28 [32];
  
  iVar1 = FUN_004caf44(param_1 + 0x30);
  if (iVar1 == 0) {
    iVar1 = 0;
  }
  else {
    local_44 = &DAT_004cf944;
    local_48 = *(undefined4 *)(param_1 + 0x24);
    FUN_004733ee(DAT_004cfcbc,DAT_004cfa2c,0x1338,*(undefined4 *)(param_1 + 0x20));
    iVar1 = FUN_004cbedc(param_1,auStack_28,param_1 + 0x20);
    if (iVar1 == 0) {
      local_48 = lfs_fs_disk_version(param_1);
      local_44 = *(undefined **)(*(int *)(param_1 + 0x68) + 0x1c);
      local_40 = *(undefined4 *)(param_1 + 0x6c);
      local_3c = *(undefined4 *)(param_1 + 0x70);
      local_38 = *(undefined4 *)(param_1 + 0x74);
      local_34 = *(undefined4 *)(param_1 + 0x78);
      FUN_004cb04c(&local_48);
      local_30 = *DAT_004cfcc0;
      local_2c = (undefined1 *)&local_48;
      iVar1 = FUN_004cd388(param_1,auStack_28,&local_30,1);
      if (iVar1 == 0) {
        FUN_004cf564(param_1,0);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

