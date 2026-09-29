
void case_wait_elapsed(uint param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = case_tick_word2();
  if (param_1 != 0xffffffff) {
    param_1 = param_1 + *DAT_08004978;
  }
  do {
    iVar2 = case_tick_word2();
  } while ((uint)(iVar2 - iVar1) < param_1);
  return;
}

