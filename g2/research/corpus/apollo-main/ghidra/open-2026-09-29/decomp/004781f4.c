
undefined8
APP_ConnectParamOTASetFastMode
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_00478734;
    local_10 = 499;
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_00478738);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047873c,DAT_0047873c);
  }
  *DAT_00478298 = 0;
  uVar1 = DAT_00478724;
  fw_event_loop_remove_delayed(DAT_00478724);
  fw_event_loop_push_delayed(uVar1,0xa3,0);
  return CONCAT44(local_c,local_10);
}

