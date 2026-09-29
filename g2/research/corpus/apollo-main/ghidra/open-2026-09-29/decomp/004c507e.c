
undefined8
_thread_notify_event_handler(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  undefined2 uVar2;
  int iVar3;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0x10f;
    param_3 = DAT_004c5698;
    param_4 = param_1;
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c,0x10f,DAT_004c5698,param_1);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004c56a0,DAT_004c56a0,param_1,param_2,param_3,param_4);
  }
  if (param_1 << 9 < 0) {
    _thread_msg_handler();
  }
  if (param_1 << 0x1d < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x119;
      param_3 = DAT_004c56a4;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004c56a8);
    }
    uVar1 = DAT_004c56ac;
    fw_event_loop_remove_delayed(DAT_004c56ac);
    fw_event_loop_push_delayed(uVar1,0,200);
    uVar1 = DAT_004c56b0;
    fw_event_loop_remove_delayed(DAT_004c56b0);
    fw_event_loop_push_delayed(uVar1,0,500);
    uVar1 = DAT_004c56b4;
    fw_event_loop_remove_delayed(DAT_004c56b4);
    fw_event_loop_push_delayed(uVar1,0,3000);
  }
  if (param_1 << 0x1c < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x125;
      param_3 = DAT_004c56b8;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004c56bc,DAT_004c56bc);
    }
  }
  if (param_1 << 0x1b < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 300;
      param_3 = DAT_004c56c0;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004c56c4,DAT_004c56c4);
    }
    uVar1 = DAT_004c56b0;
    fw_event_loop_remove_delayed(DAT_004c56b0);
    fw_event_loop_push_delayed(uVar1,0,200);
    uVar1 = DAT_004c56b4;
    fw_event_loop_remove_delayed(DAT_004c56b4);
    fw_event_loop_push_delayed(uVar1,0,3000);
    FUN_0047243a();
    iVar3 = settings_get_terminal_mode();
    if (iVar3 == 0) {
      uVar2 = 1000;
    }
    else {
      uVar2 = 500;
    }
    FUN_00472362(uVar2);
  }
  if (param_1 << 0x1a < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x13d;
      param_3 = DAT_004c56c8;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1f < 0) {
LAB_004c526a:
      compress_log_output(0x10000000,DAT_004c56cc,DAT_004c56cc);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1d < 0) goto LAB_004c526a;
    }
    FUN_00472244();
  }
  if (param_1 << 0x19 < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x143;
      param_3 = DAT_004c56d0;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1f < 0) {
LAB_004c52b6:
      compress_log_output(0x10000000,DAT_004c56d4,DAT_004c56d4);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1d < 0) goto LAB_004c52b6;
    }
    FUN_00472546();
    uVar1 = DAT_004c56d8;
    fw_event_loop_remove_delayed(DAT_004c56d8);
    fw_event_loop_push_delayed(uVar1,0,500);
    uVar1 = DAT_004c56dc;
    fw_event_loop_remove_delayed(DAT_004c56dc);
    fw_event_loop_push_delayed(uVar1,0,700);
  }
  if (-1 < param_1 << 0x14) goto LAB_004c5358;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0x14e;
    param_3 = DAT_004c56e0;
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_004c532e:
    compress_log_output(0x10000000,DAT_004c56e4,DAT_004c56e4);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_004c532e;
  }
  FUN_0047243a();
  iVar3 = settings_get_terminal_mode();
  if (iVar3 == 0) {
    uVar2 = 1000;
  }
  else {
    uVar2 = 500;
  }
  FUN_00472362(uVar2);
LAB_004c5358:
  if (param_1 << 0x17 < 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x157;
      param_3 = DAT_004c56e8;
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c569c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004c56ec,DAT_004c56ec);
    }
  }
  if (param_1 << 8 < 0) {
    _thread_exit();
  }
  return CONCAT44(param_3,param_2);
}

