
undefined8
compress_log_export_notify(byte param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_4 = (uint)param_1;
    param_2 = 0x15d;
    param_3 = DAT_0044aa10;
    FUN_0043d574(4,DAT_0044a9e4,DAT_0044a9e0,DAT_0044aa14,0x15d,DAT_0044aa10,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044aa18,DAT_0044aa18,param_1,param_2,param_3,param_4);
  }
  if (param_1 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x171;
      param_3 = DAT_0044aa1c;
      FUN_0043d574(4,DAT_0044a9e4,DAT_0044a9e0,DAT_0044aa14);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0044aa20);
    }
    uVar1 = DAT_0044aa24;
    fw_event_loop_remove_delayed(DAT_0044aa24);
    fw_event_loop_push_delayed(uVar1,0,DAT_0044aa28);
  }
  else {
    fw_event_loop_remove_delayed(DAT_0044aa24);
  }
  *DAT_0044aa0c = param_1;
  return CONCAT44(param_3,param_2);
}

