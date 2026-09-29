
undefined8 FUN_0044f730(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_0044f7a4;
  if (param_1 != 0) {
    iVar1 = FUN_0048431e(param_1);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      FUN_0044f70c(iVar1,param_1);
    }
  }
  return CONCAT44(param_4,iVar1);
}

