
undefined4 FUN_0043da24(undefined1 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_0043da70;
  *(undefined1 *)(DAT_0043da70 + 0xf2) = param_1;
  if (*(char *)(iVar1 + 0xf2) != '\0') {
    if ((*(char *)(iVar1 + 0xf4) == '\0') && (*(char *)(iVar1 + 0xf3) != '\0')) {
      FUN_0044aa98();
    }
    else if ((*(char *)(iVar1 + 0xf4) != '\0') && (*(char *)(iVar1 + 0xf3) == '\0')) {
      FUN_0044aaa0();
    }
  }
  return unaff_r7;
}

