
longlong _nvdbUpdataProdMd(void)

{
  int iVar1;
  uint unaff_r5;
  undefined4 unaff_r7;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x2e;
    FUN_0043d574(2,DAT_004abeb0,DAT_004abeac,DAT_004abea8,0x2e,DAT_004abea4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_004abeb4,DAT_004abeb4);
  }
  iVar1 = SVC_NvdbRead(DAT_004abeb8,&stack0xfffffff8,4);
  if (iVar1 < 1) {
    productModeUpdate(*(undefined1 *)(DAT_004abea0 + 1));
  }
  else if (((short)((uint)unaff_r7 >> 0x10) != *(short *)(DAT_004abea0 + 2)) &&
          ((char)unaff_r7 == '\0')) {
    productModeUpdate(*(undefined1 *)(DAT_004abea0 + 1));
  }
  return (ulonglong)unaff_r5 << 0x20;
}

