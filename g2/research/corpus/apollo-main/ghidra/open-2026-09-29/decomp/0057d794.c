
int SVC_CodecDMICClose(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  short asStack_10 [2];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(asStack_10,2,0);
  iVar1 = GX8002_DMICCtrl(0,asStack_10,200);
  if ((iVar1 == 0) && (asStack_10[0] == 1)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_CodecDMICClose_0057dbec,0x33a,
                   PTR_s_DMICClose_success_0057dbf4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__codec_host_DMICClose_success_0057dbf8,
                          PTR_s__codec_host_DMICClose_success_0057dbf8);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_CodecDMICClose_0057dbec,0x337,
                   PTR_s_DMICClose_failed___d__rsp_0x_04X_0057dbe8,iVar1,asStack_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__codec_host_DMICClose_failed___d_0057dbf0,
                          PTR_s__codec_host_DMICClose_failed___d_0057dbf0,iVar1,asStack_10[0]);
    }
    if (iVar1 == 0) {
      iVar1 = -1;
    }
  }
  return iVar1;
}

