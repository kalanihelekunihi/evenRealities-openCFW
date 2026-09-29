
uint am_devices_mspi_hongshi_read_bank(undefined1 param_1,undefined1 param_2)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  uint local_1c;
  
  bVar4 = 0;
  do {
    iVar2 = driver_a6ng_read_register(param_1,&local_1c,1,param_2);
    if (iVar2 == 0) break;
    bVar4 = bVar4 + 1;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005bc8ac,DAT_005bc8a8,DAT_005bc8a4,0x140,DAT_005bc8a0,bVar4,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_005bc8b0,DAT_005bc8b0,bVar4,iVar2);
    }
    osDelay(2);
  } while (bVar4 < 3);
  uVar1 = local_1c;
  if (bVar4 < 3) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bc8a4,0x150,DAT_005bcbb0,iVar2,uVar1 >> 0x18,
                   uVar1 >> 0x10 & 0xff,uVar1 >> 8 & 0xff,uVar1 & 0xff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x11400000,DAT_005bcd2c,DAT_005bcd2c,iVar2,uVar1 >> 0x18,
                          uVar1 >> 0x10 & 0xff,uVar1 >> 8 & 0xff,uVar1 & 0xff);
    }
    local_1c = local_1c & 0xff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bc8ac,DAT_005bc8a8,DAT_005bc8a4,0x148,DAT_005bcb24,bVar4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005bcb68,DAT_005bcb68,bVar4);
    }
    local_1c = 0xff;
  }
  return local_1c;
}

