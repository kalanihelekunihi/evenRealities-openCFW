
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
PB_RxEvenAIAnalyseInfo(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_20;
  undefined *puStack_1c;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == 0) {
    FUN_00439c04(&uStack_20,PTR_DAT_004e4a10,0x14);
    puStack_1c = (undefined *)CONCAT22(puStack_1c._2_2_,1);
    APP_errorFaultHandler(&uStack_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_1c = (undefined *)DAT_004e4870;
      uStack_20 = 0x1a5;
      FUN_0043d574(1,DAT_004e487c,DAT_004e4878,PTR_s_PB_RxEvenAIAnalyseInfo_004e4a14);
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
      puStack_1c = PTR_s_pAnalyseInfo_004e4a18;
      uStack_20 = 0x1a9;
      FUN_0043d574(4,DAT_004e487c,DAT_004e4878,PTR_s_PB_RxEvenAIAnalyseInfo_004e4a14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_004e4b04,_DAT_004e4b04);
    }
    iVar1 = service_even_ai_fn_00497ea2(4,param_2,1);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

