
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0049c668(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x10d;
    param_3 = PTR_s_dashboard_clear_stock_ui_data__C_0049cd74;
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_clear_stock_ui_data_0049cd78,0x10d,
                 PTR_s_dashboard_clear_stock_ui_data__C_0049cd74,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0049c6ae;
  }
  compress_log_output(0x10000000,PTR_s__dashboard_dashboard_clear_stock_0049cd7c,
                      PTR_s__dashboard_dashboard_clear_stock_0049cd7c);
LAB_0049c6ae:
  FUN_004e9fde();
  FUN_0043c0e4(_DAT_0049cd80,0x428,0);
  FUN_0043c0e4(_DAT_0049cd84,0x430,0);
  FUN_0043c0e4(_DAT_0049cd88,0x428,0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x119;
    param_3 = PTR_s_dashboard_clear_stock_ui_data__S_0049cd8c;
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_clear_stock_ui_data_0049cd78);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__dashboard_dashboard_clear_stock_0049cd90);
  }
  return CONCAT44(param_3,param_2);
}

