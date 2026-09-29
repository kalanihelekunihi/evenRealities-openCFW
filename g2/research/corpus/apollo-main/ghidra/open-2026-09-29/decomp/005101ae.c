
undefined8 CALLBACK_MGR_Deinit(int *param_1,undefined4 param_2,undefined *param_3)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    iVar1 = *param_1;
    while (iVar1 != 0) {
      iVar1 = *(int *)(iVar1 + 4);
      callback_mgr_delete_node();
    }
    *param_1 = 0;
    *(undefined1 *)(param_1 + 1) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x4e;
      param_3 = PTR_s___s__Callback_manager_deinitiali_00510570;
      FUN_0043d574(4,DAT_00510554,DAT_00510550,PTR_s_CALLBACK_MGR_Deinit_00510574,0x4e,
                   PTR_s___s__Callback_manager_deinitiali_00510570,param_1[2]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__callback_mgr___s__Callback_mana_00510578,
                          PTR_s__callback_mgr___s__Callback_mana_00510578,param_1[2]);
    }
  }
  return CONCAT44(param_3,param_2);
}

