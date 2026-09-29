
void FUN_005d91bc(undefined4 *param_1,uint param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_2c [4];
  
  if (param_1[1] == 0) {
    uVar3 = *param_1;
    if (1 < param_2) {
      param_2 = (uint)(param_2 != 0);
    }
    if (*(char *)(param_1 + 3) == '\x01') {
      local_2c[3] = param_4;
      for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
        iVar1 = FT_RoundFix(param_3[1]);
        iVar2 = FT_RoundFix(*param_3);
        iVar1 = FUN_005d8fae(param_1 + param_2 * 9 + 4,iVar2 >> 0x10,iVar1 >> 0x10,uVar3,
                             local_2c + iVar4);
        if (iVar1 != 0) goto LAB_005d9230;
        param_3 = param_3 + 2;
      }
      iVar1 = FUN_005d905c(param_1 + param_2 * 9 + 4,local_2c[0],local_2c[1],local_2c[2],uVar3);
      if (iVar1 == 0) {
        return;
      }
    }
    else {
      iVar1 = 6;
    }
LAB_005d9230:
    param_1[1] = iVar1;
  }
  return;
}

