
void FUN_005d8f4e(int param_1,undefined4 param_2)

{
  if (*(int *)(param_1 + 0xc) != 0) {
    *(undefined4 *)(*(int *)(param_1 + 0x14) + *(int *)(param_1 + 0xc) * 0x10 + -4) = param_2;
  }
  return;
}

