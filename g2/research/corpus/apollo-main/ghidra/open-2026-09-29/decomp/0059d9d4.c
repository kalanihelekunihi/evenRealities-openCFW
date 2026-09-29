
undefined8
translate_ui_0059d9d4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_0059e3bc;
    local_10 = 0xee;
    FUN_0043d574(3,DAT_0059defc,DAT_0059def8,DAT_0059e3c0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__translate_ui_Translate_UI_deini_0059e484,
                        PTR_s__translate_ui_Translate_UI_deini_0059e484);
  }
  FUN_0043c0e4(DAT_0059e5cc,0x2c,0);
  return CONCAT44(local_c,local_10);
}

