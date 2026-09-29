
void FUN_004c9778(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_0043d0ce(0);
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_task_exit_004c9cb4,0xff,
                 PTR_s_thread_exit_start__004c9cb0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__task_manager_thread_exit_start__004c9cb8,
                        PTR_s__task_manager_thread_exit_start__004c9cb8);
  }
  iVar1 = FUN_004c96b6(param_1);
  iVar2 = osEventFlagsWait(*(undefined4 *)(DAT_004c9c58 + 0x1c),iVar1,1,5000);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_task_exit_004c9cb4,0x103,
                 PTR_s_thread_sync_exit_0x_x__0x_x_004c9cbc,iVar2,iVar1);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_004c9818:
    compress_log_output(0xc800000,PTR_s__task_manager_thread_sync_exit_0_004c9cc0,
                        PTR_s__task_manager_thread_sync_exit_0_004c9cc0,iVar2,iVar1);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_004c9818;
  }
  if (iVar2 != iVar1) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_task_exit_004c9cb4,0x106,
                   PTR_s_thread_sync_exit_failed_0x_x____0_004c9cc4,iVar2,iVar1);
    }
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1f) {
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1d) goto LAB_004c987a;
    }
    compress_log_output(0x4800000,PTR_s__task_manager_thread_sync_exit_f_004c9cc8,
                        PTR_s__task_manager_thread_sync_exit_f_004c9cc8,iVar2,iVar1);
  }
LAB_004c987a:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_task_exit_004c9cb4,0x109,
                 PTR_s_thread_exit_end__004c9ccc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__task_manager_thread_exit_end__004c9cd0,
                        PTR_s__task_manager_thread_exit_end__004c9cd0);
  }
  return;
}

