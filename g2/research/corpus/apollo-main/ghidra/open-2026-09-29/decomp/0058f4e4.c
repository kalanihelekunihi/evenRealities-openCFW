
void production_pcm_callback_stereo(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iStack_33c;
  uint uStack_338;
  undefined4 uStack_334;
  undefined1 auStack_1a8 [400];
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_338 = (uint)param_1;
    iStack_33c = DAT_0058f868;
    uStack_334 = param_3;
    FUN_0043d574(4,DAT_0058f874,DAT_0058f870,DAT_0058f86c,0x15);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0058f878,DAT_0058f878,param_1,param_3);
  }
  FUN_0043c0e4(auStack_1a8,400,0);
  FUN_0043c0e4(&uStack_338,400,0);
  iStack_33c = 0;
  if (param_1 == 0) {
    if (*DAT_0058f87c == '\0') {
      SVC_PcmRecoderProcess(0,param_2,param_3);
    }
    else {
      SVC_Lc3EncodeMono(param_2,param_3,auStack_1a8,&iStack_33c,DAT_0058f880);
      FUN_00439be4(&uStack_338,auStack_1a8,iStack_33c);
      SVC_Lc3EncodeMono(param_2,param_3,auStack_1a8,&iStack_33c,DAT_0058f884);
      FUN_00439be4((int)&uStack_338 + iStack_33c,auStack_1a8,iStack_33c);
      SVC_PcmRecoderProcess(0,&uStack_338,iStack_33c << 1);
    }
  }
  return;
}

