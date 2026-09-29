
int GX8002_DMICCtrl(char param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;
  undefined1 auStack_38 [14];
  undefined2 *puStack_2a;
  ushort uStack_26;
  undefined4 uStack_1c;
  
  if (param_2 == (undefined2 *)0x0) {
    iVar1 = -1;
  }
  else {
    if (param_1 == '\0') {
      uVar3 = 0xd;
    }
    else {
      uVar3 = 0xc;
    }
    iVar1 = -1;
    uStack_1c = param_4;
    for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
      FUN_0043c0e4(auStack_38,0x1a,0);
      iVar1 = gx8002_send_and_wait_response(uVar3,0x100,0,0,0,auStack_38,param_3);
      if (iVar1 == 0) break;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_DMICCtrl_0057d868,0x269,
                     PTR_s_DMICCtrl_attempt__d_failed___d_0057d864,iVar4 + 1,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__codec_host_DMICCtrl_attempt__d_f_0057d86c,
                            PTR_s__codec_host_DMICCtrl_attempt__d_f_0057d86c,iVar4 + 1,iVar1);
      }
      semantic_gx8002_free_message(auStack_38);
    }
    if (iVar1 == 0) {
      if (uStack_26 < 2) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_DMICCtrl_0057d868,0x273,
                       PTR_s_Invalid_DMIC_ctrl_response_lengt_0057d938,uStack_26);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__codec_host_Invalid_DMIC_ctrl_re_0057da1c,
                              PTR_s__codec_host_Invalid_DMIC_ctrl_re_0057da1c,uStack_26);
        }
        semantic_gx8002_free_message(auStack_38);
        iVar1 = -1;
      }
      else {
        *param_2 = *puStack_2a;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_DMICCtrl_0057d868,0x278,
                       PTR_s_DMIC_ctrl_status__0x_04X_0057d930,*param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__codec_host_DMIC_ctrl_status__0x_0057d934,
                              PTR_s__codec_host_DMIC_ctrl_status__0x_0057d934,*param_2);
        }
        semantic_gx8002_free_message(auStack_38);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

