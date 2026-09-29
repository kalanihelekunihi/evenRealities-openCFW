
undefined4 FUN_00419bb8(uint param_1,uint param_2,int param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (param_3 == 0) {
    if ((param_1 & param_2) != 0) {
      uVar1 = 1;
    }
  }
  else if ((param_1 & param_2) == param_2) {
    uVar1 = 1;
  }
  return uVar1;
}

