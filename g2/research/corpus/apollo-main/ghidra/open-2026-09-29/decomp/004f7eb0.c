
undefined8 FUN_004f7eb0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  *DAT_004f7f14 = 0;
  iVar1 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 << 0x1e < 0) {
    uStack_c = DAT_004f88bc;
    uStack_10 = 0xaf4;
    FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f88c0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004f88c4,DAT_004f88c4);
  }
  FUN_004f7860(param_1);
  return CONCAT44(uStack_c,uStack_10);
}

