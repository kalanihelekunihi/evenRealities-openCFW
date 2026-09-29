
undefined4
tracepoint_send_to_master
          (undefined2 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 local_18 [2];
  undefined4 uStack_14;
  
  local_18[0] = 0;
  uStack_14 = param_4;
  iVar1 = tracepoint_encode_response(param_2,local_18);
  if (iVar1 == 0) {
    uVar2 = FUN_00465480(0x11,DAT_005ee898,local_18[0],0,param_1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb58,0x108,DAT_005eeb54,param_1,*param_2,
                   local_18[0],uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_005eeb5c,DAT_005eeb5c,param_1,*param_2,local_18[0],uVar2);
    }
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

