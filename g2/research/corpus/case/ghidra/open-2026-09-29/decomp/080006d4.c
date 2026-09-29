
undefined4 case_wait_controller_flag2(int *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = case_status_word2_bit2(*param_1);
  if (iVar1 != 0) {
    iVar1 = *param_1;
    if (-1 < *(int *)(iVar1 + 8) << 0x1e) {
      *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & DAT_08000730) + 0x10;
    }
    iVar1 = case_tick_word2();
    while (*(int *)(*param_1 + 8) << 0x1d < 0) {
      iVar2 = case_tick_word2();
      if ((2 < (uint)(iVar2 - iVar1)) && (*(int *)(*param_1 + 8) << 0x1d < 0)) {
        param_1[0x16] = param_1[0x16] | 0x10;
        param_1[0x17] = param_1[0x17] | 1;
        return 1;
      }
    }
  }
  return 0;
}

