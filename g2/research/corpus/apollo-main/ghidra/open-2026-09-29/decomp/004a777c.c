
undefined8 SVC_SetKvdbOnboardingConfig(char param_1,undefined1 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  uVar1 = 0;
  if (param_1 == '\0') {
    if (param_2 != (undefined1 *)0x0) {
      *DAT_004a789c = *param_2;
    }
  }
  else {
    iVar2 = FUN_0043d0ce(0);
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x2d;
      FUN_0043d574(2,DAT_004a78ac,DAT_004a78a8,DAT_004a78a4,0x2d,DAT_004a78a0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a78b0,DAT_004a78b0);
    }
    uVar1 = 0xffffffff;
  }
  return CONCAT44(unaff_r5,uVar1);
}

