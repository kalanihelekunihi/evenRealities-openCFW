
undefined4 FUN_005ccc00(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (uint)(*(int *)(param_2 + 0x30) * *(int *)(param_2 + 0x2c));
      uVar1 = uVar1 + 1) {
    if (*(int *)(*(int *)(param_2 + 0x34) + uVar1 * 4) != 0) {
      if (*(int *)(*(int *)(*(int *)(param_2 + 0x34) + uVar1 * 4) + 4) != 0) {
        FUN_0044f758(*(undefined4 *)(*(int *)(*(int *)(param_2 + 0x34) + uVar1 * 4) + 4));
        *(undefined4 *)(*(int *)(*(int *)(param_2 + 0x34) + uVar1 * 4) + 4) = 0;
      }
      FUN_0044f758(*(undefined4 *)(*(int *)(param_2 + 0x34) + uVar1 * 4));
      *(undefined4 *)(*(int *)(param_2 + 0x34) + uVar1 * 4) = 0;
    }
  }
  if (*(int *)(param_2 + 0x34) != 0) {
    FUN_0044f758(*(undefined4 *)(param_2 + 0x34));
  }
  if (*(int *)(param_2 + 0x38) != 0) {
    FUN_0044f758(*(undefined4 *)(param_2 + 0x38));
  }
  if (*(int *)(param_2 + 0x3c) != 0) {
    FUN_0044f758(*(undefined4 *)(param_2 + 0x3c));
  }
  return param_4;
}

