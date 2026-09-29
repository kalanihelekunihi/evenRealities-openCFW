
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 PB_RxEvenAICtrl(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&uStack_20,_DAT_004e3e88,0x14);
    puStack_1c = (undefined *)CONCAT22(puStack_1c._2_2_,1);
    APP_errorFaultHandler(&uStack_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_1c = (undefined *)DAT_004e3e8c;
      uStack_20 = 0xb7;
      FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,_DAT_004e3e90);
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
      puStack_1c = PTR_s_pCtrl_>status____d_004e3e98;
      uStack_20 = 0xbb;
      FUN_0043d574(4,DAT_004e3d08,DAT_004e3d04,_DAT_004e3e90);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,_DAT_004e410c,_DAT_004e410c,*param_2);
    }
    iVar1 = service_even_ai_fn_00497ea2(1,param_2,2);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

