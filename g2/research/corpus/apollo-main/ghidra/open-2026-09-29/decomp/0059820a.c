
undefined8 FUN_0059820a(undefined4 param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00598134(param_1);
  if (iVar1 == 0) {
    uVar2 = 0;
    while ((uVar2 < param_3 && (iVar1 = FUN_005981e0(param_1,param_2), iVar1 != 0))) {
      uVar2 = uVar2 + 1;
      param_2 = param_2 + 1;
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

