
void case_transition_word4_alt(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba80;
  if (*(int *)(DAT_0800ba80 + 4) != 0) {
    *(undefined4 *)(DAT_0800ba80 + 4) = 0;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}

