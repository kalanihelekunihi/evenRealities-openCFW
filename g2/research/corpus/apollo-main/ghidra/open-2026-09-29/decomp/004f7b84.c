
undefined8 FUN_004f7b84(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  piVar1 = DAT_004f7f14;
  if ((*DAT_004f8094 != 0) && (*DAT_004f7f14 == 0)) {
    *DAT_004f81d8 = 3;
    *piVar1 = 1;
    iVar3 = FUN_0043d0ce();
    uVar2 = DAT_004f8618;
    if (iVar3 << 0x1e < 0) {
      unaff_r5 = 0xa4e;
      FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f861c);
      unaff_r6 = uVar2;
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f8620,DAT_004f8620);
    }
    FUN_004f7634(0,100,DAT_004f8870);
    FUN_004f76b6(0,0xfa);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

