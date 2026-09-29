
void threadBleProductionTask(void)

{
  uint uVar1;
  int iVar2;
  
  threadBleProductionEnter();
  _thread_resource_init();
  threadBleProductionLoopInit();
  threadBleProductionStart();
  threadBleProductionReady();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        _thread_notify_event_handler();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00538b54,DAT_00538b50,DAT_00538b4c,99,DAT_00538b48);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,DAT_00538b58,DAT_00538b58);
  } while( true );
}

