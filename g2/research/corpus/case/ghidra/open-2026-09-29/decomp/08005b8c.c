
undefined4 case_wait_status_bit5(int *param_1)

{
  int iVar1;
  int iVar2;
  
  *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & 0xffffff5f;
  iVar1 = case_tick_word2();
  do {
    if (*(int *)(*param_1 + 0xc) << 0x1a < 0) {
      return 0;
    }
    iVar2 = case_tick_word2();
  } while ((uint)(iVar2 - iVar1) < 0x3e9);
  return 3;
}

