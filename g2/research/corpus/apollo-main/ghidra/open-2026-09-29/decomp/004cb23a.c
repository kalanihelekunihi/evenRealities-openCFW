
int FUN_004cb23a(int param_1,undefined4 *param_2,uint param_3,int param_4,int param_5,int param_6,
                int param_7)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  uint local_30;
  int local_2c;
  int iStack_28;
  
  uVar7 = param_2[3];
  local_30 = param_2[4];
  iVar6 = 0;
  iStack_28 = param_4;
  iVar1 = FUN_004caf5c(param_1 + 0x3c,param_2);
  if ((iVar1 != 0) && (iVar1 = FUN_004caeb0(param_3), iVar1 != 0)) {
    uVar2 = FUN_004caeb0(*(undefined4 *)(param_1 + 0x3c));
    uVar3 = FUN_004caeb0(param_4);
    if ((uVar2 & 0xffff) == uVar3) {
      return -2;
    }
    uVar2 = FUN_004caeb0(*(undefined4 *)(param_1 + 0x3c));
    uVar3 = FUN_004caeb0(param_4);
    if ((uVar2 & 0xffff) < uVar3) {
      iVar6 = -0x400;
    }
  }
  do {
    iVar1 = FUN_004caebe(local_30);
    if (uVar7 < iVar1 + 4U) {
      return -2;
    }
    iVar1 = FUN_004caebe(local_30);
    uVar2 = local_30;
    uVar7 = uVar7 - iVar1;
    iVar1 = FUN_004ca83c(param_1,0,param_1,4,*param_2,uVar7,&local_30,4);
    if (iVar1 != 0) {
      return iVar1;
    }
    uVar3 = lfs_frombe32(local_30);
    local_30 = (uVar3 ^ uVar2) & 0x7fffffff;
    iVar1 = FUN_004caeb0(param_3);
    if ((iVar1 != 0) && (iVar1 = FUN_004cae88(uVar2), iVar1 == 0x400)) {
      uVar3 = FUN_004caeb0(param_4 - iVar6);
      uVar4 = FUN_004caeb0(uVar2);
      if (uVar4 <= (uVar3 & 0xffff)) {
        if (uVar2 == (param_4 - iVar6 & DAT_004cbfe0 | DAT_004cbfe4)) {
          return -2;
        }
        iVar1 = FUN_004caea6(uVar2);
        iVar6 = iVar6 + iVar1 * 0x400;
      }
    }
  } while ((uVar2 & param_3) != (param_4 - iVar6 & param_3));
  iVar1 = FUN_004cae74(uVar2);
  if (iVar1 == 0) {
    uVar5 = FUN_004caeb8(uVar2);
    local_2c = lfs_min(uVar5,param_7);
    iVar1 = FUN_004ca83c(param_1,0,param_1,local_2c,*param_2,param_5 + uVar7 + 4,param_6,local_2c);
    if (iVar1 == 0) {
      FUN_0043c0e4(param_6 + local_2c,param_7 - local_2c,0);
      iVar1 = iVar6 + uVar2;
    }
  }
  else {
    iVar1 = -2;
  }
  return iVar1;
}

