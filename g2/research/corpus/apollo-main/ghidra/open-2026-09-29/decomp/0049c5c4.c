
void FUN_0049c5c4(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_20;
  undefined *puStack_1c;
  int iStack_18;
  uint uStack_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_14 = (uint)*param_2;
    puStack_1c = PTR_s_dashboard_ring_battery_callback__0049cd68;
    uStack_20 = 0xfb;
    iStack_18 = param_1;
    FUN_0043d574(3,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_ring_battery_callback_0049cd6c);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0049c61a;
  }
  uStack_20 = (uint)*param_2;
  compress_log_output(0xc800000,PTR_s__dashboard_dashboard_ring_batter_0049cd70,
                      PTR_s__dashboard_dashboard_ring_batter_0049cd70,param_1);
LAB_0049c61a:
  if (((param_1 == 0) && (iVar1 = FUN_00443484(), iVar1 == 1)) &&
     (iVar1 = FUN_004434d0(1), iVar1 == 1)) {
    FUN_0043c0e4(&uStack_20,3,0);
    FUN_0043c0e4(&uStack_20,3,0);
    uStack_20._0_3_ = CONCAT12(*param_2,0x413);
    FUN_00464bb2(1,&uStack_20,3,0);
  }
  return;
}

