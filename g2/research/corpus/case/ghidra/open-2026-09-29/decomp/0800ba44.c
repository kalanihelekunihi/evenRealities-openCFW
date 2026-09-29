
void case_transition_word4(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba5c;
  if (*(int *)(DAT_0800ba5c + 4) != 0) {
    *(undefined4 *)(DAT_0800ba5c + 4) = 0;
    FUN_08004d30(DAT_0800ba60,iVar1);
  }
  return;
}

