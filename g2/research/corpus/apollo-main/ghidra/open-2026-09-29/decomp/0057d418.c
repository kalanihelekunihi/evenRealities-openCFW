
int SVC_SwitchBFMode(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  char acStack_10 [4];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(acStack_10,1,0);
  iVar1 = GX8002_SwitchBFMode(acStack_10,200);
  if ((iVar1 == 0) && (acStack_10[0] == '\x01')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SwitchBFMode_0057db9c,0x2f6,
                   PTR_s_SwitchBFMode_success_0057dba4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__codec_host_SwitchBFMode_success_0057dba8,
                          PTR_s__codec_host_SwitchBFMode_success_0057dba8);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SwitchBFMode_0057db9c,0x2f3,
                   PTR_s_SwitchBFMode_failed___d__respons_0057db98,iVar1,acStack_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__codec_host_SwitchBFMode_failed__0057dba0,
                          PTR_s__codec_host_SwitchBFMode_failed__0057dba0,iVar1,acStack_10[0]);
    }
  }
  return iVar1;
}

