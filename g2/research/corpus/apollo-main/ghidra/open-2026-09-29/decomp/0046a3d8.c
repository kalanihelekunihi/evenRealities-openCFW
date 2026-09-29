
void sc_selection_change_anim_ready_cb(void)

{
  int iVar1;
  char local_14 [12];
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046ae7c,0x176,DAT_0046ae78);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0046ae80,DAT_0046ae80);
  }
  *DAT_0046b004 = 0;
  iVar1 = system_close_fifo_empty_00469c98();
  if (iVar1 == 0) {
    FUN_0043c0e4(local_14,10,0);
    FUN_0043c0e4(local_14,10,0);
    system_close_fifo_pop_00469cac(local_14,5);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046ae7c,0x17d,DAT_0046ae84,local_14[0]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0046b008,DAT_0046b008,local_14[0]);
    }
    if (local_14[0] == '\n') {
      system_close_handle_click();
    }
    else if (local_14[0] == 'D') {
      system_close_handle_scroll_up();
    }
    else if (local_14[0] == 'E') {
      system_close_handle_scroll_down();
    }
    else if ((local_14[0] == 'H') && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      FUN_00464c36(0x22,0,0,0);
    }
  }
  return;
}

