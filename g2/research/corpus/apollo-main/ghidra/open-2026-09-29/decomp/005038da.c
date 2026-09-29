
undefined4 FUN_005038da(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  if ((int)((uint)*(byte *)(param_1 + 4) << 0x1f) < 0) {
    *(undefined1 *)((int)param_2 + 5) = 1;
    if (*param_2 != 0) {
      FUN_0047a49c(*param_2,*(undefined1 *)((int)param_2 + 0xb));
    }
    if (*param_2 != 0) {
      FUN_004bb098(param_1,(char)param_2[1]);
    }
  }
  *(undefined1 *)(param_2 + 2) = 0;
  return param_4;
}

