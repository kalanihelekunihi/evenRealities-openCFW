
void FUN_0053223c(byte *param_1)

{
  int iVar1;
  
  iVar1 = DAT_00532638 + (uint)*param_1 * 0x10;
  if ((param_1[4] != 0) && (*(char *)(iVar1 + -4) == '\0')) {
    if (*(char *)*DAT_0053291c == '\0') {
      if ((*(char *)(iVar1 + -3) != '\0') &&
         (*(undefined1 *)(iVar1 + -3) = 0, *(int *)(iVar1 + -0x10) != 0)) {
        AttcDiscConfigResume((char)*(undefined2 *)param_1,*(int *)(iVar1 + -0x10));
      }
    }
    else {
      FUN_00531d60((char)*(undefined2 *)param_1);
    }
    *(undefined1 *)(iVar1 + -4) = 1;
  }
  return;
}

