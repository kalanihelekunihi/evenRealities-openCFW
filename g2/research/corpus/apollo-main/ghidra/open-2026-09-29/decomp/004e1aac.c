
undefined8 CB_ANCC_UnregisterMsgCountCallback(int param_1)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_Invalid_callback_function_004e1b10;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x35;
      FUN_0043d574(1,PTR_s_cb_msg_notif_004e1b1c,PTR_s_D__01_workspace_s200_ap510b_iar__004e1b18,
                   PTR_s_CB_ANCC_UnregisterMsgCountCallba_004e1b24);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_msg_notif_Invalid_callback_f_004e1b20,
                          PTR_s__cb_msg_notif_Invalid_callback_f_004e1b20);
    }
  }
  else {
    CALLBACK_MGR_Unregister(DAT_004e1b0c,param_1);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

