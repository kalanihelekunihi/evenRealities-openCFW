
undefined4 FUN_005d6fcc(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = FUN_005d6e44(param_1);
  if (uVar1 < param_2) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0xa1);
  }
  else {
    *(uint *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + param_2 * -8;
  }
  return param_4;
}

