
undefined4 FUN_005c2ac8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  for (iVar1 = 0; *(int *)(*(int *)(param_1 + 0x2c) + iVar1 * 4) != 0; iVar1 = iVar1 + 1) {
    FUN_0044f758(*(undefined4 *)(*(int *)(param_1 + 0x2c) + iVar1 * 4));
  }
  FUN_0044f758(*(undefined4 *)(param_1 + 0x2c));
  *(undefined4 *)(param_1 + 0x2c) = 0;
  return param_4;
}

