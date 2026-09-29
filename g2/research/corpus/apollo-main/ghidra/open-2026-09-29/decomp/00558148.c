
undefined8 FUN_00558148(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_00439be4(DAT_005588a8,DAT_005588ac,0x80);
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_005588b0;
    local_10 = 0x8c;
    FUN_0043d574(3,DAT_005588bc,DAT_005588b8,DAT_005588b4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__dashboard_layout_dashboard_layo_005588c0);
  }
  return CONCAT44(local_c,local_10);
}

