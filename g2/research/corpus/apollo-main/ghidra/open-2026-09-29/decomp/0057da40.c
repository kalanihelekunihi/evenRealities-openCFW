
int GX8002_GetVoiceEvent
              (undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined2 auStack_38 [2];
  undefined1 auStack_34 [4];
  undefined1 uStack_30;
  undefined2 *puStack_26;
  undefined4 uStack_18;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar2 = -1;
  }
  else {
    iVar2 = -1;
    uStack_18 = param_4;
    for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
      FUN_0043c0e4(auStack_34,0x1a,0);
      uVar1 = DAT_0057db7c;
      auStack_38[0] = 0;
      iVar2 = gx8002_read_uart_data(DAT_0057db7c,0x1e,auStack_38,200);
      if (iVar2 == 0) {
        iVar2 = gx8002_unpack_message(uVar1,auStack_38[0],auStack_34);
        if (iVar2 == 0) break;
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_codec_host_0057dc30,PTR_s_D__01_workspace_s200_ap510b_iar__0057dc2c,
                       PTR_s_GX8002_GetVoiceEvent_0057dc28,0x37a,
                       PTR_s_GetVoiceEvent__unpack_message_at_0057dc24,iVar4 + 1,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__codec_host_GetVoiceEvent__unpac_0057dc34,
                              PTR_s__codec_host_GetVoiceEvent__unpac_0057dc34,iVar4 + 1,iVar2);
        }
        semantic_gx8002_free_message(auStack_34);
      }
    }
    if (iVar2 == 0) {
      *param_1 = uStack_30;
      *(undefined2 *)(param_1 + 2) = *puStack_26;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_codec_host_0057dc30,PTR_s_D__01_workspace_s200_ap510b_iar__0057dc2c,
                     PTR_s_GX8002_GetVoiceEvent_0057dc28,900,
                     PTR_s_voice_event__cmd_id_0x_04X__even_0057dc38,*param_1,
                     *(undefined2 *)(param_1 + 2));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__codec_host_voice_event__cmd_id__0057dc3c,
                            PTR_s__codec_host_voice_event__cmd_id__0057dc3c,*param_1,
                            *(undefined2 *)(param_1 + 2));
      }
      semantic_gx8002_free_message(auStack_34);
      iVar2 = 0;
    }
  }
  return iVar2;
}

