
undefined4 FUN_005d2390(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_2 <= *(uint *)(param_1 + 0xc)) || (iVar1 = FUN_005d232c(param_1,param_2), iVar1 != 0))
  {
    *(uint *)(param_1 + 0x14) = param_2;
  }
  return param_4;
}

