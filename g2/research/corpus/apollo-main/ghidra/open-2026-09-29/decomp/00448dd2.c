
int FUN_00448dd2(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if (*DAT_00448fc4 == '\0') {
    iVar1 = 0;
  }
  else {
    iVar1 = 0;
    uVar3 = 0;
    while ((uVar3 < 0x100 && (iVar2 = FUN_00448b96(), iVar2 != 0))) {
      if (((int)((uint)*(byte *)(iVar2 + 10) << 0x1f) < 0) &&
         ((*DAT_00448fcc != '\0' && (*(int *)(DAT_00448fcc + 4) != 0)))) {
        (**(code **)(DAT_00448fcc + 4))(iVar2 + 0xd,*(undefined2 *)(iVar2 + 8));
      }
      FUN_00448a8e(iVar2);
      iVar1 = iVar1 + 1;
      *DAT_00448fbc = *DAT_00448fbc + 1;
      uVar3 = uVar3 + 1;
    }
  }
  return iVar1;
}

