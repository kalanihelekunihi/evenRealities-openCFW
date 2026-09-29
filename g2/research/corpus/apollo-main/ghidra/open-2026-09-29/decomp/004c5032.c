
undefined8 _ring_enable_pair(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004c568c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x109;
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c5690);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004c5078;
  }
  compress_log_output(0x10000000,DAT_004c5694,DAT_004c5694);
LAB_004c5078:
  FUN_00472630();
  return CONCAT44(unaff_r6,unaff_r5);
}

