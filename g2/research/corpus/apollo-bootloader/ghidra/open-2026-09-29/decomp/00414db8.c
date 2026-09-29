
int FUN_00414db8(int param_1)

{
  undefined4 uVar1;
  undefined2 uVar2;
  int iVar3;
  uint uVar4;
  uint local_34 [2];
  undefined1 auStack_2c [32];
  
  iVar3 = FUN_00410c36(param_1 + 0x3c);
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    uVar2 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
    uVar1 = DAT_004150fc;
    FUN_00415fae(DAT_004152e8,DAT_004150fc,0x1361,*(undefined4 *)(param_1 + 0x40),
                 *(undefined4 *)(param_1 + 0x44),uVar2,&DAT_00415014);
    iVar3 = lfs_tag_type3(*(undefined4 *)(param_1 + 0x3c));
    if (iVar3 != 0x4ff) {
      FUN_00415734(DAT_004152ec,uVar1,0x1365);
    }
    iVar3 = FUN_00411be4(param_1,auStack_2c,param_1 + 0x40);
    if (iVar3 == 0) {
      uVar4 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
      FUN_00414cbc(param_1,0x3ff,0);
      local_34[1] = 0;
      local_34[0] = DAT_004152dc | (uVar4 & 0xffff) << 10;
      iVar3 = FUN_00412f8c(param_1,auStack_2c,local_34,1);
      if (iVar3 == 0) {
        iVar3 = 0;
      }
    }
  }
  return iVar3;
}

