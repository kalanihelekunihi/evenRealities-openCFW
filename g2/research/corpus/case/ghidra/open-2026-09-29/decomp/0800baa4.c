
void case_transition_word4_alt(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bac0;
  if (*(int *)(DAT_0800bac0 + 4) != 1) {
    *(undefined4 *)(DAT_0800bac0 + 4) = 1;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}

