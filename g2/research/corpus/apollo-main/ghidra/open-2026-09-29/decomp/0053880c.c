
void _thread_exit(void)

{
  int iVar1;
  
  FUN_004c9c3c(0xb);
  iVar1 = DAT_00538b5c;
  if (*(int *)(DAT_00538b5c + 0xc) != 0) {
    osMessageQueueDelete(*(undefined4 *)(DAT_00538b5c + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00538b54,DAT_00538b50,PTR_s__thread_exit_00538bd0,0x103,
                   PTR_s_ble_production_message_queue_del_00538bcc);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_0053886c;
    }
    compress_log_output(0x10000000,PTR_s__task_ble_production_ble_product_00538bd4,
                        PTR_s__task_ble_production_ble_product_00538bd4);
  }
LAB_0053886c:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00538b54,DAT_00538b50,PTR_s__thread_exit_00538bd0,0x105,
                 PTR_s_thread_ble_production_exit_00538bd8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__task_ble_production_thread_ble_p_00538bdc,
                        PTR_s__task_ble_production_thread_ble_p_00538bdc);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

