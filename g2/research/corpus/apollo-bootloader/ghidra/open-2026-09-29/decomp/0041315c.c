
int FUN_0041315c(int param_1,int param_2,undefined4 param_3)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_3;
  iVar2 = FUN_00411caa(param_1,param_2 + 8,&uStack_14,0);
  if (-1 < iVar2) {
    iVar3 = lfs_tag_type3(iVar2);
    if (iVar3 == 2) {
      iVar3 = lfs_tag_id(iVar2);
      if (iVar3 == 0x3ff) {
        local_1c = *(undefined4 *)(param_1 + 0x20);
        local_18 = *(undefined4 *)(param_1 + 0x24);
      }
      else {
        uVar1 = lfs_tag_id(iVar2);
        iVar2 = FUN_004110d0(param_1,param_2 + 8,DAT_00413cec,DAT_00413ac0 | (uint)uVar1 << 10,
                             &local_1c);
        if (iVar2 < 0) {
          return iVar2;
        }
        FUN_00410b46(&local_1c);
      }
      iVar2 = FUN_00411be4(param_1,param_2 + 8,&local_1c);
      if (iVar2 == 0) {
        *(undefined4 *)(param_2 + 0x2c) = *(undefined4 *)(param_2 + 8);
        *(undefined4 *)(param_2 + 0x30) = *(undefined4 *)(param_2 + 0xc);
        *(undefined2 *)(param_2 + 4) = 0;
        *(undefined4 *)(param_2 + 0x28) = 0;
        *(undefined1 *)(param_2 + 6) = 2;
        lfs_mlist_append(param_1,param_2);
        iVar2 = 0;
      }
    }
    else {
      iVar2 = -0x14;
    }
  }
  return iVar2;
}

