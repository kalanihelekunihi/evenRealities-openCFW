
undefined8
system_close_handle_scroll_down
          (undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0046ae98;
  if (*DAT_0046ae98 < 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x1f0;
      param_2 = DAT_0046b044;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046b03c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0046b048);
    }
    goto LAB_0046a820;
  }
  *DAT_0046ae98 = *DAT_0046ae98 + -1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = *piVar1;
    param_1 = 0x1eb;
    param_2 = DAT_0046b038;
    FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046b03c,0x1eb,DAT_0046b038,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046a7c6:
    compress_log_output(0x10400000,DAT_0046b040,DAT_0046b040,*piVar1,param_1,param_2,param_3);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046a7c6;
  }
  system_close_update_selection();
  system_close_process_next_event_0046a4e2();
LAB_0046a820:
  return CONCAT44(param_2,param_1);
}

