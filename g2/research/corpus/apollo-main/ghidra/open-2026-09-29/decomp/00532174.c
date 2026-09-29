
void FUN_00532174(ushort *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_00532638 + (uint)(byte)*param_1 * 0x10;
  if (*(char *)(iVar1 + -4) == '\0') {
    iVar2 = FUN_004bb07c((char)*param_1);
    if (((iVar2 != 0) && (iVar3 = FUN_004bad26((char)*param_1), iVar3 != 0)) &&
       (*(char *)(iVar2 + 0x86) != '\0')) {
      FUN_0047b3cc(*(undefined4 *)(DAT_00532920 + (uint)*param_1 * 0x30 + -0x30),0);
    }
    iVar3 = FUN_004bad26((char)*param_1);
    if ((iVar3 == 0) || (*(char *)(iVar1 + -7) == '\0')) {
      if (*(char *)*DAT_0053291c != '\0') {
        FUN_00531d60((char)*param_1);
      }
    }
    else {
      if (((iVar2 != 0) &&
          ((FUN_0047b488(iVar2,*(undefined1 *)(iVar1 + -7)), *(char *)(iVar1 + -7) == '\x04' ||
           (*(char *)(iVar1 + -7) == '\b')))) && (*(int *)(iVar1 + -0xc) != 0)) {
        FUN_0047b48e(iVar2,*(undefined4 *)(iVar1 + -0xc));
      }
      if ((*(char *)(iVar1 + -3) != '\0') &&
         (*(undefined1 *)(iVar1 + -3) = 0, *(int *)(iVar1 + -0x10) != 0)) {
        AttcDiscConfigResume((char)*param_1,*(int *)(iVar1 + -0x10));
      }
    }
    *(undefined1 *)(iVar1 + -4) = 1;
  }
  return;
}

