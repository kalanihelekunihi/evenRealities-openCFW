
undefined8
app_ring_enable_touch(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_1 = 0xf0;
    param_2 = DAT_004c5660;
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c5664,0xf0,DAT_004c5660,param_3,param_4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004c5668,DAT_004c5668);
  }
  FUN_00472426(1);
  cVar2 = profile_get_conn_state_byte();
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xf9;
      param_2 = DAT_004c566c;
      FUN_0043d574(3,DAT_004c5640,DAT_004c563c,DAT_004c5664);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004c5670);
    }
    uVar1 = DAT_004c5674;
    fw_event_loop_remove_delayed(DAT_004c5674);
    fw_event_loop_push_delayed(uVar1,0,500);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xfd;
      param_2 = DAT_004c5678;
      FUN_0043d574(3,DAT_004c5640,DAT_004c563c,DAT_004c5664,0xfd,DAT_004c5678,cVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004c567c,DAT_004c567c,cVar2);
    }
  }
  return CONCAT44(param_2,param_1);
}

