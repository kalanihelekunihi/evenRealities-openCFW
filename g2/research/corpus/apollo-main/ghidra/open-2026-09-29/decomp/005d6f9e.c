
void FUN_005d6f9e(int param_1,uint param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_005d6e44(param_1);
  if (uVar1 < param_2) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0x82);
  }
  else {
    *(undefined4 *)(*(int *)(param_1 + 8) + param_2 * 8) = param_3;
    *(undefined1 *)(*(int *)(param_1 + 8) + param_2 * 8 + 4) = 0;
  }
  return;
}

