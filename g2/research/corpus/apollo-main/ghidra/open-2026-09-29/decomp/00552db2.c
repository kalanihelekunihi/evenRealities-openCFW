
void text_stream_start_pending_animation(int param_1)

{
  int iVar1;
  
  if ((((param_1 != 0) && (*(int *)(param_1 + 0xc) < *(int *)(param_1 + 0x10))) &&
      (*(undefined1 *)(param_1 + 0x14) = 0, *(int *)(param_1 + 0x20) != 0)) &&
     (iVar1 = osMutexAcquire(*(undefined4 *)(param_1 + 0x20),0xffffffff), iVar1 == 0)) {
    if (*(int *)(param_1 + 0x1c) != 0) {
      osTimerStart(*(undefined4 *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 8));
    }
    osMutexRelease(*(undefined4 *)(param_1 + 0x20));
  }
  return;
}

