
undefined8
system_close_handle_scroll_up(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0046ae98;
  if (*DAT_0046b00c + -1 <= *DAT_0046ae98) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x1e2;
      param_2 = DAT_0046b030;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046b028);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0046b034);
    }
    goto LAB_0046a77c;
  }
  *DAT_0046ae98 = *DAT_0046ae98 + 1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = *piVar1;
    param_1 = 0x1dd;
    param_2 = DAT_0046b024;
    FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046b028,0x1dd,DAT_0046b024,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046a722:
    compress_log_output(0x10400000,DAT_0046b02c,DAT_0046b02c,*piVar1,param_1,param_2,param_3);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046a722;
  }
  system_close_update_selection();
  system_close_process_next_event_0046a4e2();
LAB_0046a77c:
  return CONCAT44(param_2,param_1);
}

