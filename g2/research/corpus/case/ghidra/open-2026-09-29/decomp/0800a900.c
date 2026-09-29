
undefined4 FUN_0800a900(void)

{
  bool bVar1;
  int *piVar2;
  uint uVar3;
  
  piVar2 = DAT_0800a934;
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1ff;
  }
  if (uVar3 != 0) {
    return 0xfffffffa;
  }
  if (*DAT_0800a934 != 1) {
    return 0xffffffff;
  }
  *(uint *)(DAT_0800a938 + 0x1c) = *(uint *)(DAT_0800a938 + 0x1c) & 0xffffff;
  *piVar2 = 2;
  FUN_0800c284();
  return 0;
}

