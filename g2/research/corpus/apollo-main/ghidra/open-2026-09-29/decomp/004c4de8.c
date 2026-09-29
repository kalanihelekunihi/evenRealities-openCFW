
void _thread_msg_handler(void)

{
  int iVar1;
  int *local_8;
  
  while( true ) {
    local_8 = (int *)0x0;
    iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_004c5648 + 0xc),&local_8,0,0);
    if ((iVar1 != 0) || (local_8 == (int *)0x0)) break;
    iVar1 = *local_8;
    if (iVar1 == 2) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004c5640,DAT_004c563c,PTR_s__thread_msg_handler_004c5658,0xc0,
                     PTR_s_ring_task_RX__msg_id____d__msg_l_004c5654,*local_8,local_8[1]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__task_ring_ring_task_RX__msg_id___004c565c,
                            PTR_s__task_ring_ring_task_RX__msg_id___004c565c,*local_8,local_8[1]);
      }
      FUN_00472988(local_8 + 2,local_8[1] & 0xffff);
    }
    else if (iVar1 == 0x80) {
      if (local_8[1] != 0) {
        FUN_00472378((char)local_8[2]);
      }
    }
    else if (iVar1 == 0x400) {
      if (local_8[1] != 0) {
        FUN_004723d6((char)local_8[2],*(undefined1 *)((int)local_8 + 9));
      }
    }
    else if ((iVar1 == 0x1000) && (1 < (uint)local_8[1])) {
      FUN_004722d8(CONCAT11((char)local_8[2],*(undefined1 *)((int)local_8 + 9)));
    }
    file_heap_free(local_8);
  }
  return;
}

