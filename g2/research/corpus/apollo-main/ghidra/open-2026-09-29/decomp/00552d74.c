
void text_stream_stop_and_delete_animation(int param_1)

{
  int iVar1;
  
  if (((param_1 != 0) && (*(undefined1 *)(param_1 + 0x14) = 1, *(int *)(param_1 + 0x20) != 0)) &&
     (iVar1 = osMutexAcquire(*(undefined4 *)(param_1 + 0x20),0xffffffff), iVar1 == 0)) {
    if (*(int *)(param_1 + 0x1c) != 0) {
      osTimerStop(*(undefined4 *)(param_1 + 0x1c));
      osTimerDelete(*(undefined4 *)(param_1 + 0x1c));
      *(undefined4 *)(param_1 + 0x1c) = 0;
    }
    osMutexRelease(*(undefined4 *)(param_1 + 0x20));
  }
  return;
}

