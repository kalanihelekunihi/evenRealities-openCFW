
undefined4 case_start_controller(int *param_1)

{
  int iVar1;
  int iVar2;
  
  if ((char)param_1[10] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 10) = 1;
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  *(undefined4 *)(*param_1 + 0x24) = 0xca;
  *(undefined4 *)(*param_1 + 0x24) = 0x53;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffbff;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xffffbfff;
  iVar1 = case_tick_word2();
  do {
    if (*(int *)(*param_1 + 0xc) << 0x1d < 0) {
      *(undefined4 *)(*param_1 + 0x24) = 0xff;
      *(undefined1 *)((int)param_1 + 0x29) = 1;
      *(undefined1 *)(param_1 + 10) = 0;
      return 0;
    }
    iVar2 = case_tick_word2();
  } while ((uint)(iVar2 - iVar1) < 0x3e9);
  *(undefined4 *)(*param_1 + 0x24) = 0xff;
  *(undefined1 *)((int)param_1 + 0x29) = 3;
  *(undefined1 *)(param_1 + 10) = 0;
  return 3;
}

