
undefined4 FUN_0044fa5e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 != 0) {
    *(undefined4 *)(param_1 + 0x10) = param_2;
    *(undefined4 *)(param_1 + 0x14) = param_3;
    FUN_00440656(*(undefined4 *)(param_1 + 700));
  }
  return param_4;
}

