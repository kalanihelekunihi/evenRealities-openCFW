
int SVC_SetMicGain(undefined1 param_1)

{
  int iVar1;
  int iVar2;
  short asStack_10 [2];
  
  FUN_0043c0e4(asStack_10,2,0);
  iVar1 = GX8002_SetMicGain(param_1,asStack_10,200);
  if ((iVar1 == 0) && (asStack_10[0] == 1)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SetMicGain_0057dbc4,0x322,
                   PTR_s_SetMicGain_success__gain__u_0057dbcc,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__codec_host_SetMicGain_success__g_0057dbd0,
                          PTR_s__codec_host_SetMicGain_success__g_0057dbd0,param_1);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SetMicGain_0057dbc4,799,
                   PTR_s_SetMicGain_failed___d__rsp_0x_04_0057dbc0,iVar1,asStack_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__codec_host_SetMicGain_failed____0057dbc8,
                          PTR_s__codec_host_SetMicGain_failed____0057dbc8,iVar1,asStack_10[0]);
    }
    if (iVar1 == 0) {
      iVar1 = -1;
    }
  }
  return iVar1;
}

