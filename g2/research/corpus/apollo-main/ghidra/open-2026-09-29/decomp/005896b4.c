
undefined8 FUN_005896b4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_0043c0e4(DAT_00589934,0xd0,0);
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_00589968;
    local_10 = 0xda;
    FUN_0043d574(3,DAT_00589944,DAT_00589940,DAT_0058996c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00589970);
  }
  return CONCAT44(local_c,local_10);
}

