
undefined4 case_wait_peripheral(int *param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1[5] == 8) {
    uVar3 = 8;
  }
  else {
    if ((*(uint *)(*param_1 + 0xc) & 1) != 0) {
      param_1[0x16] = param_1[0x16] | 0x20;
      return 1;
    }
    uVar3 = 4;
  }
  iVar1 = case_tick_word2();
  do {
    if ((*(uint *)*param_1 & uVar3) != 0) {
      param_1[0x16] = param_1[0x16] | 0x200;
      iVar1 = case_status_word3_field10_clear(*param_1);
      if (((iVar1 != 0) && (*(char *)((int)param_1 + 0x1a) == '\0')) &&
         (*(int *)*param_1 << 0x1c < 0)) {
        iVar1 = case_status_word2_bit2();
        if (iVar1 == 0) {
          *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffffff3;
          param_1[0x16] = param_1[0x16] & 0xfffffeffU | 1;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
      if ((char)param_1[6] == '\0') {
        *(undefined4 *)*param_1 = 0xc;
      }
      return 0;
    }
  } while (((param_2 == 0xffffffff) ||
           ((iVar2 = case_tick_word2(), (uint)(iVar2 - iVar1) <= param_2 && (param_2 != 0)))) ||
          ((*(uint *)*param_1 & uVar3) != 0));
  param_1[0x16] = param_1[0x16] | 4;
  *(undefined1 *)(param_1 + 0x15) = 0;
  return 3;
}

