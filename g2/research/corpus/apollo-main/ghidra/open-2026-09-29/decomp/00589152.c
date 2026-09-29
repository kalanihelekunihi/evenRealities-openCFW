
undefined8 FUN_00589152(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    *DAT_00589384 = 0;
    *DAT_0058936c = 0;
    *DAT_00589370 = 0;
    *DAT_00589374 = 0;
    *DAT_00589394 = 0;
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005893c8;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x110;
      FUN_0043d574(4,DAT_00589364,DAT_00589360,DAT_005893cc);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005893d0,DAT_005893d0);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

