
undefined4 FUN_00471cae(undefined2 *param_1)

{
  *param_1 = 1;
  *(undefined1 *)(param_1 + 1) = 1;
  *(undefined4 *)(param_1 + 8) = 0xffffffff;
  *(undefined4 *)(param_1 + 10) = 0xffffffff;
  *(undefined1 *)((int)param_1 + 3) = 0;
  *(undefined1 *)(param_1 + 2) = 0;
  *(undefined1 *)((int)param_1 + 5) = 0;
  param_1[3] = 1;
  *(undefined4 *)(param_1 + 6) = 0;
  return 0;
}

