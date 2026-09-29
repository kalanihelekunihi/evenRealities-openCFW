
undefined4
PB_RxEvenAIAskInfo(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&uStack_20,PTR_DAT_004e478c,0x14);
    puStack_1c = (undefined *)CONCAT22(puStack_1c._2_2_,1);
    APP_errorFaultHandler(&uStack_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_1c = (undefined *)DAT_004e3e8c;
      uStack_20 = 0x16b;
      FUN_0043d574(1,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   PTR_s_PB_RxEvenAIAskInfo_004e4790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_PORINT_NULL_004e3e94);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_18 = (uint)*param_2;
      puStack_1c = PTR_s_pAskInfo_>status____d_004e4794;
      uStack_20 = 0x16f;
      FUN_0043d574(4,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   PTR_s_PB_RxEvenAIAskInfo_004e4790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__pb_evenai_pAskInfo_>status____d_004e4798,
                          PTR_s__pb_evenai_pAskInfo_>status____d_004e4798,*param_2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_18 = (uint)param_2[1];
      puStack_1c = PTR_s_pAskInfo_>stream_enable____d_004e479c;
      uStack_20 = 0x170;
      FUN_0043d574(4,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   PTR_s_PB_RxEvenAIAskInfo_004e4790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__pb_evenai_pAskInfo_>stream_enab_004e4864,
                          PTR_s__pb_evenai_pAskInfo_>stream_enab_004e4864,param_2[1]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_18 = (uint)param_2[2];
      puStack_1c = PTR_s_pAskInfo_>text_mode____d_004e4868;
      uStack_20 = 0x171;
      FUN_0043d574(4,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   PTR_s_PB_RxEvenAIAskInfo_004e4790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__pb_evenai_pAskInfo_>text_mode___004e4a0c,
                          PTR_s__pb_evenai_pAskInfo_>text_mode___004e4a0c,param_2[2]);
    }
    iVar1 = service_even_ai_fn_00497ea2(3,param_2,0x208);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

