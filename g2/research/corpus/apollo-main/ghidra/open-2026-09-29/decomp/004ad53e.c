
void CHG_SendBatteryInfoToPeer(undefined1 param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined1 local_24;
  undefined1 local_23;
  char local_22;
  undefined1 local_21;
  undefined1 auStack_20 [8];
  undefined1 auStack_18 [8];
  
  FUN_0043c0e4(&local_24,0xc,0);
  FUN_0043c0e4(auStack_18,8,0);
  iVar2 = charger_get_local_battery_info(auStack_18);
  if (iVar2 == 0) {
    local_22 = FUN_0045a568();
    puVar1 = DAT_004ad930;
    local_23 = 8;
    if (local_22 == '\x01') {
      local_21 = 2;
    }
    else {
      local_21 = 1;
    }
    local_24 = param_1;
    FUN_00439be4(auStack_20,DAT_004ad930,8);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,DAT_004ad98c,0x13a,DAT_004ad990,param_1,*puVar1,
                   (int)*(char *)(puVar1 + 1));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004ad994,DAT_004ad994,param_1,*puVar1,
                          (int)*(char *)(puVar1 + 1));
    }
    FUN_004651e0(0x105,&local_24,0xc,0);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad98c,300,DAT_004ad944);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ad94c,DAT_004ad94c);
    }
  }
  return;
}

