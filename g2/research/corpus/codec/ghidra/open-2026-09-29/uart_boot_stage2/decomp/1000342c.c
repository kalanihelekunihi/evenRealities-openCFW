
undefined4 FUN_1000342c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 0xc) != 0) {
    uVar1 = (*(code *)(*(uint *)(param_1 + 0xc) & 0xfffffffe))(param_2,param_3);
    return uVar1;
  }
  return 0xffffffff;
}

