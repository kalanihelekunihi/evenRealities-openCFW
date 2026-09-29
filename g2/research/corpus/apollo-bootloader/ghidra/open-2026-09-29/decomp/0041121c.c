
undefined4 FUN_0041121c(uint *param_1,uint param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = DAT_00411e3c;
  if ((int)(param_2 << 3) < 0) {
    uVar4 = DAT_00411e38;
  }
  if ((((param_2 & uVar4) == (uVar4 & *param_1)) || (iVar2 = FUN_00410b7c(*param_1), iVar2 != 0)) ||
     ((DAT_00411e38 & param_2) == (*param_1 & DAT_00411c40 | DAT_00411e40))) {
    *param_1 = 0;
    uVar3 = 1;
  }
  else {
    iVar2 = lfs_tag_type1(param_2);
    if (iVar2 == 0x400) {
      uVar4 = lfs_tag_id(*param_1);
      uVar5 = lfs_tag_id(param_2);
      if (uVar5 <= (uVar4 & 0xffff)) {
        cVar1 = FUN_00410bae(param_2);
        *param_1 = *param_1 + cVar1 * 0x400;
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

