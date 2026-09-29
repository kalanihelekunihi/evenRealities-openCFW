
void case_transition_word8(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb24;
  if (*(int *)(DAT_0800bb24 + 8) != 1) {
    *(undefined4 *)(DAT_0800bb24 + 8) = 1;
    FUN_08004d30(DAT_0800bb28,iVar1);
  }
  return;
}

