
int FUN_004cee2a(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

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
  iVar1 = FUN_004ce914(param_1,param_2);
  if (iVar1 == 0) {
    if (*(int *)(param_2 + 0x20) == 0) {
      FUN_004d09b4(DAT_004cf9d8,DAT_004cfa2c,0x112c);
    }
    FUN_0043c0e4(*(undefined4 *)(param_1 + 100),*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x2c),0);
    *(undefined4 *)(param_1 + 0x54) = 0;
    uVar2 = lfs_min(*(int *)(*(int *)(param_1 + 0x68) + 0x2c) << 3,*(undefined4 *)(param_1 + 0x6c));
    *(undefined4 *)(param_1 + 0x58) = uVar2;
    *(undefined4 *)(param_1 + 0x5c) = 0;
    lfs_alloc_ckpoint(param_1);
    iVar1 = FUN_004cc502(param_1,auStack_48);
    if (iVar1 == 0) {
      local_68 = lfs_fs_disk_version(param_1);
      local_64 = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c);
      local_60 = *(undefined4 *)(param_1 + 0x6c);
      local_5c = *(undefined4 *)(param_1 + 0x70);
      local_58 = *(undefined4 *)(param_1 + 0x74);
      local_54 = *(undefined4 *)(param_1 + 0x78);
      FUN_004cb04c(&local_68);
      FUN_00439c04(auStack_28,DAT_004cf9dc,0x18);
      local_14 = (undefined1 *)&local_68;
      iVar1 = FUN_004cd388(param_1,auStack_48,auStack_28,3);
      if (iVar1 == 0) {
        local_32 = 0;
        iVar1 = FUN_004cd388(param_1,auStack_48,0,0);
        if (iVar1 == 0) {
          local_50 = *DAT_004cfa38;
          uStack_4c = DAT_004cfa38[1];
          iVar1 = FUN_004cbedc(param_1,auStack_48,&local_50);
        }
      }
    }
    FUN_004cedf8(param_1);
  }
  return iVar1;
}

