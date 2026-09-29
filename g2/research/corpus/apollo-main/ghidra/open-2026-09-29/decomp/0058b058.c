
void teleprompt_preload_timer_callback(void)

{
  int iVar1;
  
  iVar1 = page_data_lock();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b96c,0x126,DAT_0058b968);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058b970,DAT_0058b970);
    }
  }
  else {
    iVar1 = semantic_range_ready();
    if (iVar1 == 0) {
      iVar1 = semantic_find_next_request(&stack0xfffffff4);
      if (iVar1 == 0) {
        iVar1 = osTimerStart(*DAT_0058b358,0x9c4);
        if (iVar1 != 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0058b354,DAT_0058b350,DAT_0058b96c,0x13a,DAT_0058bc10);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0058bc14,DAT_0058bc14);
          }
        }
        semantic_page_data_unlock();
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058b96c,0x132,DAT_0058b97c,0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0058bc0c,DAT_0058bc0c,0);
        }
        semantic_page_data_unlock();
        teleprompt_request_page_data(0,1);
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0058b354,DAT_0058b350,DAT_0058b96c,299,DAT_0058b974);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0058b978,DAT_0058b978);
      }
      semantic_page_data_unlock();
    }
  }
  return;
}

