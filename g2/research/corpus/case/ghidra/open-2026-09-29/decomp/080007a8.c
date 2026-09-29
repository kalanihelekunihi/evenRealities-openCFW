
undefined4 case_start_peripheral(int *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = case_status_word2_bit0(*param_1);
  if (iVar1 != 0) {
    return 0;
  }
  iVar1 = *param_1;
  if ((*(uint *)(iVar1 + 8) & DAT_0800084c) == 0) {
    uVar3 = ~DAT_0800084c;
    *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & uVar3) + 1;
    if ((int)((*DAT_08000850 & 0x1c00000) << 8) < 0) {
      iVar1 = __aeabi_uidiv(*DAT_08000858,DAT_08000854);
      for (iVar1 = iVar1 + 1; iVar1 != 0; iVar1 = iVar1 + -1) {
      }
    }
    if (*(char *)((int)param_1 + 0x19) == '\x01') {
      return 0;
    }
    iVar1 = case_tick_word2();
    do {
      if ((~*(uint *)*param_1 & 1) == 0) {
        return 0;
      }
      iVar2 = case_status_word2_bit0();
      if (iVar2 == 0) {
        *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & uVar3) + 1;
      }
      iVar2 = case_tick_word2();
    } while (((uint)(iVar2 - iVar1) < 3) || ((~*(uint *)*param_1 & 1) == 0));
  }
  param_1[0x16] = param_1[0x16] | 0x10;
  param_1[0x17] = param_1[0x17] | 1;
  return 1;
}

