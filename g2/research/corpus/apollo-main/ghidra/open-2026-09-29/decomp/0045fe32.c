
undefined8 FUN_0045fe32(undefined4 param_1,undefined1 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (*DAT_0045fe88 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x70f;
      FUN_0043d574(1,DAT_0045fe98,DAT_0045fe94,DAT_0045fea4,0x70f,DAT_0045fea0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0045fea8,DAT_0045fea8);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_0045fe10(*DAT_0045fe88,param_1,param_2);
  }
  return CONCAT44(unaff_r5,uVar2);
}

