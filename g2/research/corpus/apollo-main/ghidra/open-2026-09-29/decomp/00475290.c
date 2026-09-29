
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void threadBleMsgTxTask(void)

{
  uint uVar1;
  int iVar2;
  
  threadBleMsgTxEnter();
  threadBleMsgTxQueueInit();
  threadBleMsgTxApplicationInit();
  threadBleMsgTxThreadInitHook();
  threadBleMsgTxReady();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        threadBleMsgTxDispatchFlags();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00475d6c,DAT_00475d68,_DAT_00475d64,0x67,_DAT_00475d60);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,_DAT_00475e64,_DAT_00475e64);
  } while( true );
}

