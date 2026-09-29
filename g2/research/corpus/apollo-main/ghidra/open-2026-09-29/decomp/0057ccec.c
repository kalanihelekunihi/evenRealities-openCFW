
int GX8002_SetMicGain(undefined4 param_1,undefined2 *param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_38 [14];
  undefined2 *puStack_2a;
  ushort uStack_26;
  undefined4 uStack_18;
  
  if (param_2 == (undefined2 *)0x0) {
    iVar1 = -1;
  }
  else {
    iVar1 = -1;
    uStack_18 = param_1;
    for (iVar3 = 0; iVar3 < 3; iVar3 = iVar3 + 1) {
      FUN_0043c0e4(auStack_38,0x1a,0);
      iVar1 = gx8002_send_and_wait_response(0xb,0x100,&uStack_18,1,0,auStack_38,param_3);
      if (iVar1 == 0) break;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_SetMicGain_0057d6b0,0x242,
                     PTR_s_SetMicGain_attempt__d_failed___d_0057d6ac,iVar3 + 1,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__codec_host_SetMicGain_attempt___0057d784,
                            PTR_s__codec_host_SetMicGain_attempt___0057d784,iVar3 + 1,iVar1);
      }
      semantic_gx8002_free_message(auStack_38);
    }
    if (iVar1 == 0) {
      if (uStack_26 < 2) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_SetMicGain_0057d6b0,0x24c,
                       PTR_s_Invalid_mic_gain_response_length_0057d790,uStack_26);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__codec_host_Invalid_mic_gain_res_0057d92c,
                              PTR_s__codec_host_Invalid_mic_gain_res_0057d92c,uStack_26);
        }
        semantic_gx8002_free_message(auStack_38);
        iVar1 = -1;
      }
      else {
        *param_2 = *puStack_2a;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0057d010,DAT_0057d00c,PTR_s_GX8002_SetMicGain_0057d6b0,0x251,
                       PTR_s_SetMicGain_status__0x_04X_0057d788,*param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__codec_host_SetMicGain_status__0_0057d78c,
                              PTR_s__codec_host_SetMicGain_status__0_0057d78c,*param_2);
        }
        semantic_gx8002_free_message(auStack_38);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

