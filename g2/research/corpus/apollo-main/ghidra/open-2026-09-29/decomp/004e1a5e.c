
undefined8 CB_ANCC_RegisterMsgCountCallback(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x2a;
      FUN_0043d574(1,PTR_s_cb_msg_notif_004e1b1c,PTR_s_D__01_workspace_s200_ap510b_iar__004e1b18,
                   PTR_s_CB_ANCC_RegisterMsgCountCallback_004e1b14,0x2a,
                   PTR_s_Invalid_callback_function_004e1b10);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_msg_notif_Invalid_callback_f_004e1b20,
                          PTR_s__cb_msg_notif_Invalid_callback_f_004e1b20);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = CALLBACK_MGR_Register(DAT_004e1b0c,param_1);
  }
  return CONCAT44(unaff_r5,uVar2);
}

