
undefined4 FUN_004f61f4(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = osKernelGetTickCount();
  if ((((DAT_004f6a00[1] != 0) || (*DAT_004f6a00 != 0)) &&
      (uVar3 = uVar1 - *DAT_004f6a00, -(uint)(uVar1 < *DAT_004f6a00) == DAT_004f6a00[1])) &&
     (uVar3 < 500)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f6a08,0x4a1,DAT_004f6a04,uVar3,0,500);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004f6d24,DAT_004f6d24);
    }
    return 0;
  }
  return 1;
}

