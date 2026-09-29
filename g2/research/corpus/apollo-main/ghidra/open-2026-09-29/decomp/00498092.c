
undefined4
service_even_ai_fn_00498092(char *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004985bc,DAT_004985b8,PTR_s_SVC_DecodeLocalEvenAIInfo_004985d4,0x103,
                   PTR_s_raw_data_is_NULL_or_len_is_0_004985d0,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__service_evenAI_raw_data_is_NULL_004985d8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (*param_1 == '\x02') {
      if (param_1[1] == '\x01') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004985bc,DAT_004985b8,PTR_s_SVC_DecodeLocalEvenAIInfo_004985d4,0x10e,
                       PTR_s_recv_evenai_startup__d_004985dc,param_1[2]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__service_evenAI_recv_evenai_star_004985e0,
                              PTR_s__service_evenAI_recv_evenai_star_004985e0,param_1[2]);
        }
        service_even_ai_fn_004982d4(param_1[2]);
        FUN_004e1fa6();
        puVar1 = DAT_004985a8;
        FUN_0043c0e4(DAT_004985a8,0x218,0);
        *puVar1 = 1;
        puVar1[1] = 1;
        puVar1[2] = 1;
        FUN_00439be4(puVar1 + 4,param_1 + 3,4);
        *(char *)(DAT_004985cc + 1) = param_1[7];
        puVar1[0x13] = param_1[8];
        *(undefined2 *)(puVar1 + 0x14) = *(undefined2 *)(param_1 + 9);
        FUN_004e1fbe();
      }
      else if (param_1[1] == '\x02') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004985bc,DAT_004985b8,PTR_s_SVC_DecodeLocalEvenAIInfo_004985d4,0x11f,
                       PTR_s_recv_evenai_stop_004985e4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__service_evenAI_recv_evenai_stop_004985e8,
                              PTR_s__service_evenAI_recv_evenai_stop_004985e8);
        }
        FUN_004e1fa6();
        puVar1 = DAT_004985a8;
        DAT_004985a8[1] = 1;
        puVar1[2] = 3;
        FUN_004e1fbe();
      }
      else if (param_1[1] == '\x03') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004985bc,DAT_004985b8,PTR_s_SVC_DecodeLocalEvenAIInfo_004985d4,0x129,
                       PTR_s_recv_vad_status____d_004985ec,param_1[2]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__service_evenAI_recv_vad_status___004985f0,
                              PTR_s__service_evenAI_recv_vad_status___004985f0,param_1[2]);
        }
        service_even_ai_fn_004982f2(param_1[2]);
        FUN_004e1fa6();
        puVar1 = DAT_004985a8;
        DAT_004985a8[1] = 2;
        puVar1[8] = param_1[2];
        FUN_004e1fbe();
      }
    }
    else {
      if (*param_1 != '\a') {
        return 0xffffffff;
      }
      FUN_004e1fa6();
      puVar1 = DAT_004985a8;
      DAT_004985a8[1] = param_1[1];
      puVar1[2] = param_1[2];
      FUN_004e1fbe();
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004985bc,DAT_004985b8,PTR_s_SVC_DecodeLocalEvenAIInfo_004985d4,0x13b,
                     PTR_s__evenai_action_id____d__action_t_004985f4,puVar1[1],puVar1[2]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__service_evenAI__evenai_action_i_004985f8,
                            PTR_s__service_evenAI__evenai_action_i_004985f8,puVar1[1],puVar1[2]);
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

