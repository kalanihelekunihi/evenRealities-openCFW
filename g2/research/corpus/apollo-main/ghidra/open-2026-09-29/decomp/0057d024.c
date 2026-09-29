
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int GX8002_I2SOutputCtrl(char param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  bool abStack_38 [4];
  undefined1 auStack_34 [14];
  undefined1 *puStack_26;
  short sStack_22;
  undefined4 uStack_18;
  
  if (param_2 == (undefined1 *)0x0) {
    iVar1 = -1;
  }
  else {
    abStack_38[0] = param_1 != '\0';
    iVar1 = -1;
    uStack_18 = param_4;
    for (iVar3 = 0; iVar3 < 3; iVar3 = iVar3 + 1) {
      FUN_0043c0e4(auStack_34,0x1a,0);
      iVar1 = gx8002_send_and_wait_response(0xf,0x100,abStack_38,1,0,auStack_34,param_3);
      if (iVar1 == 0) break;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_GX8002_I2SOutputCtrl_0057da24,
                     0x290,PTR_s_I2SOutputCtrl_attempt__d_failed__0057da20,iVar3 + 1,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__codec_host_I2SOutputCtrl_attemp_0057da30,
                            PTR_s__codec_host_I2SOutputCtrl_attemp_0057da30,iVar3 + 1,iVar1);
      }
      semantic_gx8002_free_message(auStack_34);
    }
    if (iVar1 == 0) {
      if (sStack_22 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_GX8002_I2SOutputCtrl_0057da24,
                       0x29a,PTR_s_Invalid_I2S_output_ctrl_response_0057da3c,sStack_22);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,_DAT_0057db60,_DAT_0057db60,sStack_22);
        }
        semantic_gx8002_free_message(auStack_34);
        iVar1 = -1;
      }
      else {
        *param_2 = *puStack_26;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_codec_host_0057da2c,DAT_0057da28,PTR_s_GX8002_I2SOutputCtrl_0057da24,
                       0x29f,PTR_s_I2S_output_ctrl_status__0x_02X_0057da34,*param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__codec_host_I2S_output_ctrl_stat_0057da38,
                              PTR_s__codec_host_I2S_output_ctrl_stat_0057da38,*param_2);
        }
        semantic_gx8002_free_message(auStack_34);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

