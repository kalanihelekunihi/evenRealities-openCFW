
undefined8
dashboard_watchface_manager_set_battery
          (uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar2 = 0x7e;
    param_2 = DAT_00500818;
    FUN_0043d574(4,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,DAT_0050081c,0x7e,DAT_00500818,
                 param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00500820,DAT_00500820,param_1 & 0xff,uVar2,param_2,param_3);
  }
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 0x18) != 0)) {
    (**(code **)(*DAT_005007fc + 0x18))(param_1 & 0xff);
  }
  return CONCAT44(param_2,uVar2);
}

