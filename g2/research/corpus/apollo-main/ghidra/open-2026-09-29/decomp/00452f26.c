
undefined4 FUN_00452f26(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    for (iVar1 = FUN_00452edc(0); iVar1 != 0; iVar1 = FUN_00452edc(iVar1)) {
      FUN_0045305c(iVar1,param_2);
    }
    *(undefined4 *)(DAT_00453058 + 0x54) = 0;
  }
  else {
    FUN_0045305c(param_1,param_2);
  }
  return param_4;
}

