
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0051238c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0055fa0e(DAT_00512b14,1);
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_c = _DAT_00512b18;
      uStack_10 = 0x3ab;
      FUN_0043d574(1,DAT_00512408,DAT_00512404,_DAT_00512b1c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_buck2_is_null__00512bb8,
                          PTR_s__npmx_driver_p_buck2_is_null__00512bb8);
    }
  }
  else {
    FUN_0055fa40(iVar1,1);
    FUN_0055fa22(iVar1,0x15);
    FUN_0055fa18(iVar1,0);
  }
  return CONCAT44(uStack_c,uStack_10);
}

