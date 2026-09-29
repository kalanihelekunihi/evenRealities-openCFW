
undefined4
tracepoint_send_to_phone
          (undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 local_14 [2];
  undefined4 uStack_10;
  
  local_14[0] = 0;
  uStack_10 = param_4;
  iVar1 = tracepoint_encode_response(param_1,local_14);
  if (iVar1 == 0) {
    uVar2 = Thread_MsgPbTxByBle(1,0x11,DAT_005ee898,local_14[0]);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb4c,0xf9,DAT_005eeb48,*param_1,local_14[0],
                   uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_005eeb50,DAT_005eeb50,*param_1,local_14[0],uVar2);
    }
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

