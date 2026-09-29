
undefined8 CB_CHG_RegisterBatInfoCallback(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x2a;
      FUN_0043d574(1,PTR_s_cb_charge_004aeb14,PTR_s_D__01_workspace_s200_ap510b_iar__004aeb10,
                   PTR_s_CB_CHG_RegisterBatInfoCallback_004aeb0c,0x2a,
                   PTR_s_Invalid_callback_function_004aeb08);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_charge_Invalid_callback_func_004aeb18,
                          PTR_s__cb_charge_Invalid_callback_func_004aeb18);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = CALLBACK_MGR_Register(DAT_004aeb04,param_1);
  }
  return CONCAT44(unaff_r5,uVar2);
}

