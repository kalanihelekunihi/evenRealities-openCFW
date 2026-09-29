
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00552906(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  *(undefined1 *)(_DAT_00552adc + 8) = 0;
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_msg_notif_timer_mgr_deinit_00552af4;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x1c;
    FUN_0043d574(4,PTR_s_message_notify_timer_00552aec,
                 PTR_s_D__01_workspace_s200_ap510b_iar__00552ae8,
                 PTR_s_msg_notif_timer_mgr_deinit_00552af8);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__message_notify_timer_msg_notif__00552afc,
                        PTR_s__message_notify_timer_msg_notif__00552afc);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

