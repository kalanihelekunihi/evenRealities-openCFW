
void _thread_exit(void)

{
  int iVar1;
  
  FUN_004c9c3c(1);
  iVar1 = DAT_0048e444;
  if (*(int *)(DAT_0048e444 + 0xc) != 0) {
    osMessageQueueDelete(*(undefined4 *)(DAT_0048e444 + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                   PTR_s__thread_exit_0048e468,0xed,PTR_s_notif_message_queue_deleted_0048e464);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_0048e3a0;
    }
    compress_log_output(0x10000000,PTR_s__task_notif_notif_message_queue_d_0048e46c,
                        PTR_s__task_notif_notif_message_queue_d_0048e46c);
  }
LAB_0048e3a0:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                 PTR_s__thread_exit_0048e468,0xef,PTR_s_thread_notif_exit_0048e470);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__task_notif_thread_notif_exit_0048e474,
                        PTR_s__task_notif_thread_notif_exit_0048e474);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

