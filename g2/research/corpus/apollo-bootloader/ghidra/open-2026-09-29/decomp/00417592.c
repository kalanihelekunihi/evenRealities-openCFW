
void FUN_00417592(void)

{
  int iVar1;
  
  iVar1 = DAT_00417bcc;
  if (*(char *)(DAT_00417bcc + 0xf2) == '\0') {
    *(undefined1 *)(DAT_00417bcc + 0xf3) = 0;
  }
  else {
    FUN_0041a6a2();
    *(undefined1 *)(iVar1 + 0xf4) = 0;
  }
  return;
}

