
undefined4 FUN_00417b7c(undefined1 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_00417bcc;
  *(undefined1 *)(DAT_00417bcc + 0xf2) = param_1;
  if (*(char *)(iVar1 + 0xf2) != '\0') {
    if ((*(char *)(iVar1 + 0xf4) == '\0') && (*(char *)(iVar1 + 0xf3) != '\0')) {
      FUN_0041a69a();
    }
    else if ((*(char *)(iVar1 + 0xf4) != '\0') && (*(char *)(iVar1 + 0xf3) == '\0')) {
      FUN_0041a6a2();
    }
  }
  return unaff_r7;
}

