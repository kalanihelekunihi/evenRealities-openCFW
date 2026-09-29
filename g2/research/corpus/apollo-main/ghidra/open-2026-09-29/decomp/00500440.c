
undefined8 try_create(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((param_1 == (int *)0x0) || (*param_1 == 0)) {
    param_1 = (int *)0x0;
  }
  else {
    iVar1 = (*(code *)*param_1)(param_2,param_3,param_4,(code *)*param_1,param_2,param_3,param_4);
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x2b;
        FUN_0043d574(2,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,PTR_s_try_create_005007e0,0x2b,
                     PTR_s_layout_create_returned__d_005007dc,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__dashboard_wf_mgr_layout_create_r_005007ec,
                            PTR_s__dashboard_wf_mgr_layout_create_r_005007ec,iVar1);
      }
      param_1 = (int *)0x0;
    }
  }
  return CONCAT44(param_2,param_1);
}

