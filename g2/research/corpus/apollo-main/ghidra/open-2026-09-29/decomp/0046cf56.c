
undefined8 FUN_0046cf56(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0xc6;
      FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5c0,0xc6,DAT_0046d5bc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d5c4,DAT_0046d5c4);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = *param_1;
  }
  return CONCAT44(unaff_r5,uVar2);
}

