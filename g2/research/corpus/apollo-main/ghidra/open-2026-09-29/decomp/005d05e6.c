
int FUN_005d05e6(int *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if ((param_2 < 0) || (param_1[4] <= param_2)) {
    iVar1 = 6;
  }
  else {
    if ((uint)param_1[2] < (uint)(param_4 + param_1[1])) {
      uVar2 = param_1[2];
      uVar3 = param_3 - *param_1;
      if (((int)uVar3 < 0) || ((uint)param_1[2] <= uVar3)) {
        uVar3 = 0xffffffff;
      }
      for (; uVar2 < (uint)(param_4 + param_1[1]); uVar2 = uVar2 + (uVar2 >> 2) + 0x400 & 0xfffffc00
          ) {
      }
      iVar1 = FUN_005d0596(param_1);
      if (iVar1 != 0) {
        return iVar1;
      }
      if (-1 < (int)uVar3) {
        param_3 = *param_1 + uVar3;
      }
    }
    *(int *)(param_1[6] + param_2 * 4) = *param_1 + param_1[1];
    *(int *)(param_1[7] + param_2 * 4) = param_4;
    FUN_00439be4(*param_1 + param_1[1],param_3,param_4);
    param_1[1] = param_4 + param_1[1];
    iVar1 = 0;
  }
  return iVar1;
}

