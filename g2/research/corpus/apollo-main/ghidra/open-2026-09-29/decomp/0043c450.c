
undefined4 FUN_0043c450(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x39;
    param_2 = PTR_s_received_event___d_0043c76c;
    uVar2 = param_3;
    FUN_0043d574(4,DAT_0043c764,DAT_0043c760,PTR_s_aging_test_page_event_handler_0043c770,0x39,
                 PTR_s_received_event___d_0043c76c,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0043c774,DAT_0043c774,param_3,param_1,param_2,uVar2);
  }
  return 1;
}

