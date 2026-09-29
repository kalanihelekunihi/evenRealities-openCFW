
undefined4 FUN_004cff9a(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (0x7f < param_1) {
    iVar1 = FUN_004cfd66(param_1);
    param_1 = (1 << (iVar1 - 5U & 0xff)) + -1 + param_1;
  }
  FUN_004cff6c(param_1,param_2,param_3);
  return param_4;
}

