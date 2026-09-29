
void case_transition_word8_alt(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb48;
  if (*(int *)(DAT_0800bb48 + 8) != 1) {
    *(undefined4 *)(DAT_0800bb48 + 8) = 1;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}

