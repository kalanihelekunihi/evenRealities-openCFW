
undefined4 FUN_0044fbfc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 != 0) {
    *(undefined4 *)(param_1 + 0x1c) = param_2;
    *(undefined4 *)(param_1 + 0x20) = param_3;
    *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_1 + 0x1c);
  }
  return param_4;
}

