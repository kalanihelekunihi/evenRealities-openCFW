
undefined8 FUN_005b3c70(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_005b37d8();
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005b3ec8;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x162;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3ecc);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_timer_Select_timeout_005b3ed0,
                          PTR_s__conversate_timer_Select_timeout_005b3ed0);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

