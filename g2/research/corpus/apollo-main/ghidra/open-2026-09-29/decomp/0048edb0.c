
void threadBleMsgRxTask(void)

{
  uint uVar1;
  int iVar2;
  
  threadBleMsgRxEnter();
  threadBleMsgRxQueueInit();
  threadBleMsgRxApplicationInit();
  threadBleMsgRxThreadInitHook();
  threadBleMsgRxReady();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        threadBleMsgRxDispatchFlags();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_ble_msgrx_0048f32c,DAT_0048f328,PTR_s_thread_ble_msgrx_0048f334,0x72,
                     PTR_s_Notify_error__0048f330);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,PTR_s__ble_msgrx_Notify_error__0048f338,
                        PTR_s__ble_msgrx_Notify_error__0048f338);
  } while( true );
}

