
undefined8 FUN_00470f68(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_00470d7c(DAT_00471148);
  if (iVar2 == 0) {
    FUN_0046f6ba(0);
    iVar2 = FUN_004c0f78(*DAT_004710ac,0x18,&stack0xfffffff8);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      uVar1 = DAT_00471158;
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x5c7;
        FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_00471150);
        unaff_r6 = uVar1;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047115c,DAT_0047115c);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0047114c;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x5c0;
      FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_00471150);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00471154,DAT_00471154);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

