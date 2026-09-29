
void production_pcm_callback_single
               (byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_1ac;
  uint local_1a8;
  undefined4 local_1a4;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_1a8 = (uint)param_1;
    local_1ac = DAT_0058f868;
    local_1a4 = param_3;
    FUN_0043d574(4,DAT_0058f874,DAT_0058f870,DAT_0058f888,0x4b);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0058f878,DAT_0058f878,param_1,param_3);
  }
  FUN_0043c0e4(&local_1a8,400,0);
  local_1ac = 0;
  if (*DAT_0058f87c == '\0') {
    SVC_PcmRecoderProcess(param_1,param_2,param_3);
  }
  else {
    if (param_1 == 0) {
      SVC_Lc3EncodeMono(param_2,param_3,&local_1a8,&local_1ac,DAT_0058f884);
    }
    else if (param_1 == 1) {
      SVC_Lc3EncodeMono(param_2,param_3,&local_1a8,&local_1ac,DAT_0058f88c);
    }
    SVC_PcmRecoderProcess(param_1,&local_1a8,local_1ac);
  }
  return;
}

