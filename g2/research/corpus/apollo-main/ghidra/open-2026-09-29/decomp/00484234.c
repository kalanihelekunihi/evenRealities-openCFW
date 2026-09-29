
int FUN_00484234(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = 0;
  iVar1 = FUN_00441c44(*param_1,0xffffffff);
  if (iVar1 == 1) {
    iVar1 = FUN_004d05e4(param_2);
    iVar3 = FUN_004d0868(param_1[1],param_2,param_3);
    if (iVar3 != 0) {
      param_1[2] = param_1[2] - iVar1;
      iVar1 = FUN_004d05e4(iVar3);
      param_1[2] = iVar1 + param_1[2];
      if ((uint)param_1[3] < (uint)param_1[2]) {
        uVar2 = param_1[2];
      }
      else {
        uVar2 = param_1[3];
      }
      param_1[3] = uVar2;
    }
    FUN_004417ee(*param_1,0,0,0);
  }
  return iVar3;
}

