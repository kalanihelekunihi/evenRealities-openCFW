
undefined8 FUN_004640c0(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004642e8;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x1a7;
    FUN_0043d574(4,DAT_004642cc,DAT_004642c8,DAT_004642ec);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004642f0,DAT_004642f0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

