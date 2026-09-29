
undefined4 PB_RxEvenAIConfig(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  uint uStack_14;
  uint uStack_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&uStack_20,PTR_DAT_004e5490,0x14);
    puStack_1c = (undefined *)CONCAT22(puStack_1c._2_2_,1);
    APP_errorFaultHandler(&uStack_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_1c = PTR_s_PORINT_NULL_004e5494;
      uStack_20 = 0x33c;
      FUN_0043d574(1,DAT_004e51b4,DAT_004e51b0,PTR_s_PB_RxEvenAIConfig_004e5498);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e51b8);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_10 = (uint)param_2[3];
      uStack_14 = (uint)param_2[1];
      uStack_18 = (uint)*param_2;
      puStack_1c = PTR_s_EvenAI_config_voice_switch__d__s_004e549c;
      uStack_20 = 0x341;
      FUN_0043d574(4,DAT_004e51b4,DAT_004e51b0,PTR_s_PB_RxEvenAIConfig_004e5498);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      puStack_1c = (undefined *)(uint)param_2[3];
      uStack_20 = (uint)param_2[1];
      compress_log_output(0x10c00000,PTR_s__pb_evenai_EvenAI_config_voice_s_004e54a0,
                          PTR_s__pb_evenai_EvenAI_config_voice_s_004e54a0,*param_2);
    }
    iVar1 = service_even_ai_fn_00497ea2(10,param_2,4);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

