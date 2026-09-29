
undefined4 case_wait_serial_idle(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = case_tick_word2();
  iVar1 = DAT_08003fc0;
  while ((*(uint *)(iVar1 + 0x10) & 0x30000) != 0) {
    uVar3 = case_tick_word2();
    if ((uint)(iVar2 + param_1) <= uVar3) {
      return 3;
    }
  }
  uVar3 = *(uint *)(iVar1 + 0x10) & DAT_08003fc4;
  *(undefined4 *)(iVar1 + 0x10) = DAT_08003fc8;
  if (uVar3 == 0) {
    iVar2 = case_tick_word2();
    do {
      if (-1 < *(int *)(iVar1 + 0x10) << 0xd) {
        return 0;
      }
      uVar3 = case_tick_word2();
    } while (uVar3 < (uint)(iVar2 + param_1));
    return 3;
  }
  *(uint *)(DAT_08003fcc + 4) = uVar3;
  return 1;
}

