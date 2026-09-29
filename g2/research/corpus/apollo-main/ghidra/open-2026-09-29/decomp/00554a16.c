
uint FUN_00554a16(undefined4 param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_005553c4;
  if (*(uint *)(DAT_005553c4 + 0xc) < 5) {
    param_2 = 0;
  }
  else {
    iVar1 = FUN_005549e6(param_1,param_2,param_3,param_4);
    if (iVar1 == 0) {
      if (param_3 == 0) {
        param_2 = 0;
      }
      else {
        param_2 = param_3 - 1;
      }
      if (*(uint *)(iVar2 + 0xc) < param_2 + 4) {
        param_2 = *(int *)(iVar2 + 0xc) - 4;
      }
      while ((param_2 < param_3 &&
             (iVar2 = FUN_005549e6(param_1,param_2,param_3,param_4), iVar2 == 0))) {
        param_2 = param_2 + 1;
      }
    }
  }
  return param_2;
}

