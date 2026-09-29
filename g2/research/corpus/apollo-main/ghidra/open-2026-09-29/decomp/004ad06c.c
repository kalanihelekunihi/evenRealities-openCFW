
undefined8
CHG_DeinitBatterySync(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar2 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar2 << 0x1e < 0) {
    uStack_c = PTR_s_CHG_DeinitBatterySync_004ad938;
    uStack_10 = 0x84;
    FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,PTR_s_CHG_DeinitBatterySync_004ad93c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__charger_common_CHG_DeinitBatter_004ad940,
                        PTR_s__charger_common_CHG_DeinitBatter_004ad940);
  }
  piVar1 = DAT_004ad924;
  if (*DAT_004ad924 != 0) {
    osMutexDelete(*DAT_004ad924);
    *piVar1 = 0;
  }
  CB_CHG_DeinitBatInfoCallbacks();
  return CONCAT44(uStack_c,uStack_10);
}

