
void FUN_00495f1a(undefined4 *param_1,undefined2 *param_2)

{
  if ((param_1 != (undefined4 *)0x0) && (param_2 != (undefined2 *)0x0)) {
    *param_2 = (short)*param_1;
    param_2[1] = (short)param_1[1];
    param_2[2] = (short)param_1[2];
    param_2[3] = (short)param_1[3];
    *(char *)(param_2 + 4) = (char)param_1[4];
    *(char *)((int)param_2 + 9) = (char)param_1[5];
    *(char *)(param_2 + 5) = (char)param_1[6];
    *(char *)((int)param_2 + 0xb) = (char)param_1[7];
    *(undefined4 *)(param_2 + 6) = 0xffffff;
    *(undefined1 *)(param_2 + 8) = 1;
    FUN_0044b5a0((int)param_2 + 0x11,param_1 + 0xe,0x7ff);
    *(undefined1 *)(param_2 + 0x408) = 0;
  }
  return;
}

