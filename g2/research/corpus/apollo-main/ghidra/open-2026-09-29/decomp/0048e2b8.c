
undefined8
_thread_notify_event_handler(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0xd2;
    param_2 = PTR_s_notifyValue___0x_x_0048e450;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                 PTR_s__thread_notify_event_handler_0048e454,0xd2,PTR_s_notifyValue___0x_x_0048e450,
                 param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__task_notif_notifyValue___0x_x_0048e458,
                        PTR_s__task_notif_notifyValue___0x_x_0048e458,param_1,iVar2,param_2,param_3)
    ;
  }
  if (param_1 << 9 < 0) {
    thread_notification_drain_queue();
  }
  if (-1 < param_1 << 0x1e) goto LAB_0048e344;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0xda;
    param_2 = PTR_s__WHITELIST__Received_whitelist_u_0048e45c;
    FUN_0043d574(4,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                 PTR_s__thread_notify_event_handler_0048e454);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0048e334:
    compress_log_output(0x10000000,PTR_s__task_notif__WHITELIST__Received_0048e460);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0048e334;
  }
  SVC_WhitelistManagerInit();
LAB_0048e344:
  if (param_1 << 8 < 0) {
    _thread_exit();
  }
  return CONCAT44(param_2,iVar2);
}

