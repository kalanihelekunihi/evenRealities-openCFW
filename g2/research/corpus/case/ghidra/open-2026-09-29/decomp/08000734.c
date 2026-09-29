
undefined4 case_start_controller_flag0(int *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(*param_1 + 8);
  iVar1 = case_status_word2_bit0();
  if ((iVar1 != 0) && ((uVar3 & 3) >> 1 == 0)) {
    iVar1 = *param_1;
    if ((*(uint *)(iVar1 + 8) & 5) == 1) {
      *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & DAT_080007a4) + 2;
      *(undefined4 *)*param_1 = 3;
      iVar1 = case_tick_word2();
      do {
        if ((*(uint *)(*param_1 + 8) & 1) == 0) {
          return 0;
        }
        iVar2 = case_tick_word2();
      } while (((uint)(iVar2 - iVar1) < 3) || ((*(uint *)(*param_1 + 8) & 1) == 0));
    }
    param_1[0x16] = param_1[0x16] | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
    return 1;
  }
  return 0;
}

