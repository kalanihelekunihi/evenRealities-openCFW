
undefined4 FUN_0800a8d8(void)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if (uVar2 != 0) {
    return 0xfffffffa;
  }
  if (*DAT_0800a8fc != 0) {
    return 0xffffffff;
  }
  *DAT_0800a8fc = 1;
  return 0;
}

