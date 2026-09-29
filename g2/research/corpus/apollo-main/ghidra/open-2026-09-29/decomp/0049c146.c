
void FUN_0049c146(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int local_60;
  undefined1 local_5c;
  undefined1 local_5b;
  undefined4 local_58;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_send_notification_stat_0049cb38,0x8a,
                 PTR_s_dashboard_send_notification_to_a_0049cb34,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__dashboard_dashboard_send_notifi_0049cb3c,
                        PTR_s__dashboard_dashboard_send_notifi_0049cb3c,param_1);
  }
  FUN_0048949c(&local_60,0x50);
  local_60 = *DAT_0049cb40;
  *DAT_0049cb40 = *DAT_0049cb40 + 1;
  local_5c = 0;
  local_5b = 1;
  local_58 = param_1;
  iVar1 = FUN_004ff09c(&local_60);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                   PTR_s_dashboard_send_notification_stat_0049cb38,0x9b,
                   PTR_s_send_success__package_id__d__unr_0049cb4c,local_60,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__dashboard_send_success__package_0049cd14,
                          PTR_s__dashboard_send_success__package_0049cd14,local_60,param_1);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                   PTR_s_dashboard_send_notification_stat_0049cb38,0x98,
                   PTR_s_send_failed__ret__d_0049cb44,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_send_failed__ret__d_0049cb48,
                          PTR_s__dashboard_send_failed__ret__d_0049cb48,iVar1);
    }
  }
  return;
}

