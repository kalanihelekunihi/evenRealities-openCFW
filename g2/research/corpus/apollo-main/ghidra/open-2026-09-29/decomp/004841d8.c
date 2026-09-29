
undefined8 FUN_004841d8(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = 0;
  if (param_2 == 0) {
    iVar3 = 0;
  }
  else {
    iVar1 = FUN_00441c44(*param_1,0xffffffff);
    if (iVar1 == 1) {
      iVar3 = FUN_004d0744(param_1[1],param_3,param_2);
      if (iVar3 != 0) {
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
  }
  return CONCAT44(param_4,iVar3);
}

