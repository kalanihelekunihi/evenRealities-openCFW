
void FUN_00515048(undefined4 *param_1)

{
  if (param_1 == (undefined4 *)0x0) {
    FUN_0051565c(1);
    return;
  }
  *param_1 = 0;
  param_1[1] = 0;
  *(undefined1 *)(param_1 + 0xb) = 0;
  *(undefined1 *)((int)param_1 + 0xd5) = 0;
  *(undefined1 *)(param_1 + 0x33) = 0;
  param_1[0xc] = 0;
  param_1[0x34] = 0x3f800000;
  param_1[0x36] = 0xff000000;
  FUN_00561810(param_1 + 0xd);
  FUN_00561810(param_1 + 2);
  *(undefined1 *)(param_1 + 0x35) = 0;
  return;
}

