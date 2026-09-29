
void threadBleMsgTxExit(void)

{
  int iVar1;
  
  FUN_004c9c3c(8);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,PTR_s__thread_exit_00475edc,0xfd,
                 PTR_s_thread_ble_msgtx_exit_00475ed8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__ble_msgtx_thread_ble_msgtx_exit_00475ee0,
                        PTR_s__ble_msgtx_thread_ble_msgtx_exit_00475ee0);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

