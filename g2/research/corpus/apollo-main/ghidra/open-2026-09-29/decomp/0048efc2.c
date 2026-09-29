
void _thread_exit(void)

{
  int iVar1;
  
  FUN_004c9c3c(7);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,PTR_s__thread_exit_0048f354,0x10a,
                 PTR_s_thread_ble_msgrx_exit_0048f350);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__ble_msgrx_thread_ble_msgrx_exit_0048f358,
                        PTR_s__ble_msgrx_thread_ble_msgrx_exit_0048f358);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

