
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005528b8(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = _DAT_00552adc;
  FUN_0043c0e4(_DAT_00552adc,0xc,0);
  *(undefined1 *)(iVar1 + 8) = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x16;
    param_3 = PTR_s_msg_notif_timer_mgr_init_00552ae0;
    FUN_0043d574(4,PTR_s_message_notify_timer_00552aec,
                 PTR_s_D__01_workspace_s200_ap510b_iar__00552ae8,
                 PTR_s_msg_notif_timer_mgr_init_00552ae4,0x16,
                 PTR_s_msg_notif_timer_mgr_init_00552ae0,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__message_notify_timer_msg_notif__00552af0);
  }
  return CONCAT44(param_3,param_2);
}

