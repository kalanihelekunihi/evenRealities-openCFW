
undefined4 FUN_0046d8e0(int *param_1,int param_2,uint param_3,int *param_4,int param_5)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  if ((((param_1 == (int *)0x0) || (*param_1 == 0)) || (param_1[1] == 0)) ||
     ((param_2 == 0 || (param_3 == 0)))) {
    uVar1 = 0;
  }
  else {
    uVar2 = FUN_0046da92(param_1);
    if ((uVar2 == 0) || ((uVar2 < param_3 && (param_5 << 0x1f < 0)))) {
      uVar1 = 0;
    }
    else {
      if (uVar2 < param_3) {
        param_3 = uVar2;
      }
      iVar3 = param_1[3];
      uVar2 = param_3;
      if ((uint)(param_1[1] - iVar3) < param_3) {
        uVar2 = param_1[1] - iVar3;
      }
      FUN_00439be4(*param_1 + iVar3,param_2,uVar2);
      param_3 = param_3 - uVar2;
      uVar4 = uVar2 + iVar3;
      if (param_3 != 0) {
        FUN_00439be4(*param_1,param_2 + uVar2,param_3);
        uVar4 = param_3;
      }
      if ((uint)param_1[1] <= uVar4) {
        uVar4 = 0;
      }
      param_1[3] = uVar4;
      if (param_1[4] != 0) {
        (*(code *)param_1[4])(param_1,1,param_3 + uVar2);
      }
      if (param_4 != (int *)0x0) {
        *param_4 = param_3 + uVar2;
      }
      uVar1 = 1;
    }
  }
  return uVar1;
}

