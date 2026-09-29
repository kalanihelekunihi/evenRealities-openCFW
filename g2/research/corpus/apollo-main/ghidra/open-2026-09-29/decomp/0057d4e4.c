
int SVC_SwitchWakeupMode(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  char acStack_10 [4];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(acStack_10,1,0);
  iVar1 = GX8002_SwitchWakeupMode(acStack_10,200);
  if ((iVar1 == 0) && (acStack_10[0] == '\0')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SwitchWakeupMode_0057dbb0,
                   0x306,PTR_s_SwitchWakeupMode_success_0057dbb8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__codec_host_SwitchWakeupMode_suc_0057dbbc,
                          PTR_s__codec_host_SwitchWakeupMode_suc_0057dbbc);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_SwitchWakeupMode_0057dbb0,
                   0x303,PTR_s_SwitchWakeupMode_failed___d__res_0057dbac,iVar1,acStack_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__codec_host_SwitchWakeupMode_fai_0057dbb4,
                          PTR_s__codec_host_SwitchWakeupMode_fai_0057dbb4,iVar1,acStack_10[0]);
    }
  }
  return iVar1;
}

