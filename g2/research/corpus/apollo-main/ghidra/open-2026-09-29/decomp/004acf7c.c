
undefined8
CHG_InitBatterySync(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar3 = FUN_0043d0ce();
  local_18 = param_3;
  local_14 = param_4;
  if (iVar3 << 0x1e < 0) {
    local_14 = DAT_004ad918;
    local_18 = 0x68;
    FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,DAT_004ad91c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004ad920,DAT_004ad920);
  }
  piVar1 = DAT_004ad924;
  iVar3 = osMutexNew(0);
  *piVar1 = iVar3;
  iVar3 = DAT_004ad908;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_004ad928;
      local_18 = 0x6d;
      FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad91c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ad92c);
    }
  }
  else {
    FUN_0043c0e4(DAT_004ad908,0x18,0);
    puVar2 = DAT_004ad930;
    FUN_0043c0e4(DAT_004ad930,8,0);
    *puVar2 = 0xffffffff;
    *(undefined4 *)(iVar3 + 0x10) = 0xffffffff;
    *DAT_004ad934 = 0;
    *DAT_004ad7c8 = 1;
    *DAT_004ad7d8 = 0;
    *DAT_004ad878 = 2;
    *DAT_004ad874 = 0;
    CB_CHG_InitBatInfoCallbacks();
  }
  return CONCAT44(local_14,local_18);
}

