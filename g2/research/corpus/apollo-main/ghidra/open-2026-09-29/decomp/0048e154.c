
void thread_notification_entry(void)

{
  uint uVar1;
  int iVar2;
  
  thread_notification_state_enter();
  thread_notification_queue_init();
  thread_notification_init_hook();
  thread_notification_whitelist_init();
  thread_notification_state_exit();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        _thread_notify_event_handler();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                     PTR_s_thread_notif_0048e434,0x5d,PTR_s_Notify_error__0048e430);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,PTR_s__task_notif_Notify_error__0048e440,
                        PTR_s__task_notif_Notify_error__0048e440);
  } while( true );
}

