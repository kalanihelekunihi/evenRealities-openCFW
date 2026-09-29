
undefined8
terminal_data_dismiss_query_notification
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_c;
  
  uVar2 = param_1;
  local_c = param_4;
  iVar1 = td_find_record_index(param_1,&local_c);
  if (iVar1 != 0) {
    *(undefined1 *)(DAT_00597c08 + local_c * 0x90 + 0x9688) = 1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x140;
      param_2 = DAT_00597c20;
      FUN_0043d574(3,DAT_00597c2c,DAT_00597c28,DAT_00597c24,0x140,DAT_00597c20,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00597c30,DAT_00597c30,param_1);
    }
  }
  return CONCAT44(param_2,uVar2);
}

