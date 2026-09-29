
undefined8 FUN_005b011c(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 extraout_r2;
  undefined4 uVar4;
  
  FUN_005b011c();
  piVar1 = DAT_005b09e0;
  uVar4 = extraout_r2;
  if (*DAT_005b09e0 == 0) {
    iVar2 = osMutexNew(DAT_005b09e4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar4 = 0x46;
        FUN_0043d574(1,DAT_005b09f4,DAT_005b09f0,DAT_005b09ec,0x46,DAT_005b09e8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005b09f8,DAT_005b09f8);
      }
      uVar3 = 0xffffffff;
      goto LAB_005b01c8;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar4 = 0x49;
      FUN_0043d574(4,DAT_005b09f4,DAT_005b09f0,DAT_005b09ec,0x49,DAT_005b09fc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005b0a00,DAT_005b0a00);
    }
  }
  uVar3 = 0;
LAB_005b01c8:
  return CONCAT44(uVar4,uVar3);
}

