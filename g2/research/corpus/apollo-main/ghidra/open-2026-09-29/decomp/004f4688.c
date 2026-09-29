
undefined4 FUN_004f4688(undefined4 param_1)

{
  int iVar1;
  undefined4 uStack00000000;
  undefined4 uStack00000004;
  
  uStack00000000 = 0x849;
  uStack00000004 = param_1;
  FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_004f4f74,DAT_004f4f74);
  }
  return 0xffffffff;
}

