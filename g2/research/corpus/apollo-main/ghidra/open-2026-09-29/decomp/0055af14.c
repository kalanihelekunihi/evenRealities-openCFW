
undefined4 PB_RxHealthMultHighlight(undefined4 param_1,ushort *param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  
  if (param_2 == (ushort *)0x0) {
    FUN_00439c04(&uStack_20,PTR_DAT_0055b268,0x14);
    puStack_1c = (undefined *)CONCAT22(puStack_1c._2_2_,1);
    APP_errorFaultHandler(&uStack_20);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_1c = (undefined *)DAT_0055b22c;
      uStack_20 = 0x178;
      FUN_0043d574(1,DAT_0055b238,DAT_0055b234,PTR_s_PB_RxHealthMultHighlight_0055b26c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055b23c);
    }
    uVar3 = 2;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_18 = (uint)*param_2;
      puStack_1c = PTR_s_pMultHighlight_Highlight_count___0055b270;
      uStack_20 = 0x17d;
      FUN_0043d574(4,DAT_0055b238,DAT_0055b234,PTR_s_PB_RxHealthMultHighlight_0055b26c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__pb_health_pMultHighlight_Highli_0055b274,
                          PTR_s__pb_health_pMultHighlight_Highli_0055b274,*param_2);
    }
    bVar1 = FUN_00559fb8(param_2);
    if (bVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uStack_18 = (uint)*param_2;
        puStack_1c = PTR_s_Health_mult_highlight_saved_succ_0055b280;
        uStack_20 = 0x187;
        FUN_0043d574(3,DAT_0055b238,DAT_0055b234,PTR_s_PB_RxHealthMultHighlight_0055b26c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__pb_health_Health_mult_highlight_0055b284,
                            PTR_s__pb_health_Health_mult_highlight_0055b284,*param_2);
      }
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uStack_18 = (uint)bVar1;
        puStack_1c = PTR_s_Failed_to_save_mult_health_highl_0055b278;
        uStack_20 = 0x182;
        FUN_0043d574(1,DAT_0055b238,DAT_0055b234,PTR_s_PB_RxHealthMultHighlight_0055b26c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__pb_health_Failed_to_save_mult_h_0055b27c,
                            PTR_s__pb_health_Failed_to_save_mult_h_0055b27c,bVar1);
      }
      uVar3 = 1;
    }
  }
  return uVar3;
}

