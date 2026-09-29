
void case_transition_word4(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba9c;
  if (*(int *)(DAT_0800ba9c + 4) != 1) {
    *(undefined4 *)(DAT_0800ba9c + 4) = 1;
    FUN_08004d30(DAT_0800baa0,iVar1);
  }
  return;
}

