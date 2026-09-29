
void FUN_00442030(int param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_004420d0();
  if (*(char *)(param_1 + 0x44) == -1) {
    *(undefined1 *)(param_1 + 0x44) = 0;
  }
  if (*(char *)(param_1 + 0x45) == -1) {
    *(undefined1 *)(param_1 + 0x45) = 0;
  }
  FUN_004420e8();
  if (*(int *)(param_1 + 0x38) == 0) {
    FUN_00455320(param_1 + 0x24,param_2,param_3);
  }
  FUN_00441f88(param_1);
  return;
}

