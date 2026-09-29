
void FUN_00495f6a(undefined4 *param_1,undefined2 *param_2)

{
  if ((param_1 != (undefined4 *)0x0) && (param_2 != (undefined2 *)0x0)) {
    *param_2 = (short)*param_1;
    param_2[1] = (short)param_1[1];
    param_2[2] = (short)param_1[2];
    param_2[3] = (short)param_1[3];
    *(undefined1 *)(param_2 + 4) = 0;
    *(undefined4 *)(param_2 + 6) = 0xf;
    *(undefined1 *)(param_2 + 8) = 0;
    *(undefined4 *)(param_2 + 10) = 0;
    *(undefined1 *)(param_2 + 0xc) = 1;
  }
  return;
}

