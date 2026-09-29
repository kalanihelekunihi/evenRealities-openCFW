
int SVC_I2SOutputCtrl(char param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  char acStack_10 [4];
  
  FUN_0043c0e4(acStack_10,1,0);
  iVar1 = GX8002_I2SOutputCtrl(param_1,acStack_10,200);
  if ((iVar1 == 0) && (acStack_10[0] == '\x01')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      if (param_1 == '\0') {
        uVar3 = 0x57db5c;
      }
      else {
        uVar3 = 0x57db58;
      }
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_I2SOutputCtrl_0057dc14,0x35b,
                   PTR_s_I2SOutputCtrl_success___s_0057dc1c,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      if (param_1 == '\0') {
        uVar3 = 0x57db5c;
      }
      else {
        uVar3 = 0x57db58;
      }
      compress_log_output(0xc400000,PTR_s__codec_host_I2SOutputCtrl_succes_0057dc20,
                          PTR_s__codec_host_I2SOutputCtrl_succes_0057dc20,uVar3);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_SVC_I2SOutputCtrl_0057dc14,0x358,
                   PTR_s_I2SOutputCtrl_failed___d__rsp_0x_0057dc10,iVar1,acStack_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__codec_host_I2SOutputCtrl_failed_0057dc18,
                          PTR_s__codec_host_I2SOutputCtrl_failed_0057dc18,iVar1,acStack_10[0]);
    }
    if (iVar1 == 0) {
      iVar1 = -1;
    }
  }
  return iVar1;
}

