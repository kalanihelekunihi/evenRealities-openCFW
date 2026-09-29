
void FUN_00417570(void)

{
  int iVar1;
  
  iVar1 = DAT_00417bcc;
  if (*(char *)(DAT_00417bcc + 0xf2) == '\0') {
    *(undefined1 *)(DAT_00417bcc + 0xf3) = 1;
  }
  else {
    FUN_0041a69a();
    *(undefined1 *)(iVar1 + 0xf4) = 1;
  }
  return;
}

