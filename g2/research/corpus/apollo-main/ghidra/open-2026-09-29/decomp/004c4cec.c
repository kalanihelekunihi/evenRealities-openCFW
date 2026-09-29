
void thread_ring_entry(void)

{
  uint uVar1;
  int iVar2;
  
  thread_ring_state_enter();
  thread_ring_queue_init();
  thread_ring_init_hook();
  thread_ring_resource_hook();
  thread_ring_state_ready();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        _thread_notify_event_handler();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004c5640,DAT_004c563c,DAT_004c5638,100,DAT_004c5634);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,DAT_004c5644,DAT_004c5644);
  } while( true );
}

