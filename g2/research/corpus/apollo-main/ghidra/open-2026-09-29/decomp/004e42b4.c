
undefined4
PB_RxEvenAIReplyInfo(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004e4b10,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004e4870;
      local_20 = 0x1dc;
      FUN_0043d574(1,DAT_004e487c,DAT_004e4878,DAT_004e4b14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e4880);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_18 = (uint)*param_2;
      local_1c = DAT_004e4b18;
      local_20 = 0x1e0;
      FUN_0043d574(4,DAT_004e487c,DAT_004e4878,DAT_004e4b14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__pb_evenai_pReplyInfo_>cmd_cnt___004e4e4c,
                          PTR_s__pb_evenai_pReplyInfo_>cmd_cnt___004e4e4c,*param_2);
    }
    iVar1 = service_even_ai_fn_00497ea2(5,param_2,0x208);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

