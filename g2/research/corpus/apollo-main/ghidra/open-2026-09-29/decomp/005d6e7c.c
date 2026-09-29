
void FUN_005d6e7c(int param_1,undefined4 param_2)

{
  if (*(int *)(param_1 + 0xc) == *(int *)(param_1 + 8) + *(int *)(param_1 + 0x10) * 8) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0x82);
  }
  else {
    **(undefined4 **)(param_1 + 0xc) = param_2;
    *(undefined1 *)(*(int *)(param_1 + 0xc) + 4) = 0;
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + 8;
  }
  return;
}

