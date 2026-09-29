
undefined8 FUN_005969a4(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*(char *)((int)DAT_00596af0 + 10) == '\0') {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00596a68;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x1b8;
      FUN_0043d574(2,DAT_00596a8c,DAT_00596a88,DAT_00596af4);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_tag_Storage_not_init_00596a6c,
                          PTR_s__conversate_tag_Storage_not_init_00596a6c);
    }
  }
  else {
    DAT_00596af0[1] = *DAT_00596af0;
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00596af8;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x1bd;
      FUN_0043d574(4,DAT_00596a8c,DAT_00596a88,DAT_00596af4);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00596afc,DAT_00596afc);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

