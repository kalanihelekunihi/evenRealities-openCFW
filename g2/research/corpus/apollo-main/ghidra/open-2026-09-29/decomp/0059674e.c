
undefined8 FUN_0059674e(void)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r5;
  
  if (*(char *)(DAT_00596998 + 10) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x133;
      FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596ab8,0x133,DAT_00596a68);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_tag_Storage_not_init_00596a6c,
                          PTR_s__conversate_tag_Storage_not_init_00596a6c);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = (uint)*(ushort *)(DAT_00596998 + 8);
  }
  return CONCAT44(unaff_r5,uVar2);
}

