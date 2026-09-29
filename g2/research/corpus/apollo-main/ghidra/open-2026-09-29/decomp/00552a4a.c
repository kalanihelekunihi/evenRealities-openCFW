
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00552a4a(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*(char *)(_DAT_00552adc + 8) != '\x02') goto LAB_00552aae;
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_msg_notif_timer_mgr_process_time_00552b24;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x4b;
    FUN_0043d574(3,PTR_s_message_notify_timer_00552aec,
                 PTR_s_D__01_workspace_s200_ap510b_iar__00552ae8,
                 PTR_s_msg_notif_timer_mgr_process_time_00552b28);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_00552a80:
    compress_log_output(0xc000000,PTR_s__message_notify_timer_msg_notif__00552b2c,
                        PTR_s__message_notify_timer_msg_notif__00552b2c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_00552a80;
  }
  FUN_005529a2();
  iVar2 = FUN_00443484();
  if ((iVar2 == 1) && (iVar2 = FUN_004434d0(4), iVar2 == 1)) {
    FUN_00464c36(4,0,0,0);
  }
LAB_00552aae:
  return CONCAT44(unaff_r6,unaff_r5);
}

