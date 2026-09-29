
void thread_ble_wsf_tx_complete_notify(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar2 = DAT_004d0cdc;
  if (*(int *)(DAT_004d0cdc + 0x14) != 0) {
    iVar1 = osSemaphoreGetCount(*(undefined4 *)(DAT_004d0cdc + 0x14));
    if (iVar1 == 0) {
      iVar2 = osSemaphoreRelease(*(undefined4 *)(iVar2 + 0x14));
      if (iVar2 != 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_task_ble_wsf_004d0cec,DAT_004d0ce8,DAT_004d0d14,0xf2,DAT_004d0d10,
                       iVar2,0,in_r3);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_004d0d18,DAT_004d0d18,iVar2,0);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_task_ble_wsf_004d0cec,DAT_004d0ce8,DAT_004d0d14,0xf5,DAT_004d0d1c,iVar1
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d0d20,DAT_004d0d20,iVar1);
      }
    }
  }
  return;
}

