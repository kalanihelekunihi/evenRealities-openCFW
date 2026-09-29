
undefined8 FUN_0045f876(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0045f840(param_1,param_2);
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      FUN_0045f58c(param_1,param_2);
      uVar1 = 1;
    }
  }
  return CONCAT44(param_4,uVar1);
}

