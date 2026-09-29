
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void AUD_ThreadExit(void)

{
  int *piVar1;
  int iVar2;
  
  FUN_004c9c3c(3);
  piVar1 = _DAT_0053ce74;
  if (*_DAT_0053ce74 != 0) {
    osTimerStop(*_DAT_0053ce74);
    osTimerDelete(*piVar1);
    *piVar1 = 0;
  }
  iVar2 = DAT_0053cea4;
  if (*(int *)(DAT_0053cea4 + 0xc) != 0) {
    osMessageQueueDelete(*(undefined4 *)(DAT_0053cea4 + 0xc));
    *(undefined4 *)(iVar2 + 0xc) = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_thread_audio_0053cf68,PTR_s_D__01_workspace_s200_ap510b_iar__0053cf64,
                   PTR_s_AUD_ThreadExit_0053cf60,0x25a,PTR_s_audio_message_queue_deleted_0053cf5c);
    }
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1f) {
      iVar2 = FUN_0043d0ce();
      if (-1 < iVar2 << 0x1d) goto LAB_0053ce2e;
    }
    compress_log_output(0x10000000,PTR_s__thread_audio_audio_message_queu_0053cf6c,
                        PTR_s__thread_audio_audio_message_queu_0053cf6c);
  }
LAB_0053ce2e:
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_thread_audio_0053cf68,PTR_s_D__01_workspace_s200_ap510b_iar__0053cf64,
                 PTR_s_AUD_ThreadExit_0053cf60,0x25d,PTR_s_thread_audio_exit_0053cf70);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__thread_audio_thread_audio_exit_0053cf74,
                        PTR_s__thread_audio_thread_audio_exit_0053cf74);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

