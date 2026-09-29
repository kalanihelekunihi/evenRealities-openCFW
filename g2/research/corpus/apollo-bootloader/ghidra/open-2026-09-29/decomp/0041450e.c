
int FUN_0041450e(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 uStack_4c;
  undefined1 auStack_48 [22];
  undefined1 local_32;
  undefined1 auStack_28 [20];
  undefined1 *local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_00413ff8(param_1,param_2);
  if (iVar1 == 0) {
    if (*(int *)(param_2 + 0x20) == 0) {
      FUN_00415734(DAT_004150a8,DAT_004150fc,0x112c);
    }
    FUN_0041560c(*(undefined4 *)(param_1 + 100),*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x2c),0);
    *(undefined4 *)(param_1 + 0x54) = 0;
    uVar2 = lfs_min(*(int *)(*(int *)(param_1 + 0x68) + 0x2c) << 3,*(undefined4 *)(param_1 + 0x6c));
    *(undefined4 *)(param_1 + 0x58) = uVar2;
    *(undefined4 *)(param_1 + 0x5c) = 0;
    lfs_alloc_ckpoint(param_1);
    iVar1 = FUN_00412162(param_1,auStack_48);
    if (iVar1 == 0) {
      local_68 = lfs_fs_disk_version(param_1);
      local_64 = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c);
      local_60 = *(undefined4 *)(param_1 + 0x6c);
      local_5c = *(undefined4 *)(param_1 + 0x70);
      local_58 = *(undefined4 *)(param_1 + 0x74);
      local_54 = *(undefined4 *)(param_1 + 0x78);
      FUN_00410d54(&local_68);
      FUN_004156ac(auStack_28,DAT_004150ac,0x18);
      local_14 = (undefined1 *)&local_68;
      iVar1 = FUN_00412f8c(param_1,auStack_48,auStack_28,3);
      if (iVar1 == 0) {
        local_32 = 0;
        iVar1 = FUN_00412f8c(param_1,auStack_48,0,0);
        if (iVar1 == 0) {
          local_50 = *DAT_00415108;
          uStack_4c = DAT_00415108[1];
          iVar1 = FUN_00411be4(param_1,auStack_48,&local_50);
        }
      }
    }
    FUN_004144dc(param_1);
  }
  return iVar1;
}

