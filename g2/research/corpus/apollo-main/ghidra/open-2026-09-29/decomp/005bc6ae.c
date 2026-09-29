
void am_devices_mspi_hongshi_setBrightness(int param_1)

{
  byte bVar1;
  byte bVar2;
  byte *pbVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  if (param_1 < 2) {
    iVar6 = 5;
  }
  else if (param_1 < 0x65) {
    iVar6 = (param_1 * 0xfa + -0x1c3) / 0x62 + 5;
  }
  else {
    iVar6 = 0xff;
  }
  pbVar3 = (byte *)SVC_NvdbGetSysData(5);
  bVar1 = *pbVar3;
  iVar4 = FUN_0045a568();
  if (iVar4 == 1) {
    iVar4 = settings_get_config();
    bVar2 = *(byte *)(iVar4 + 0x17);
  }
  else {
    iVar4 = settings_get_config();
    bVar2 = *(byte *)(iVar4 + 0x16);
  }
  uVar5 = (uint)bVar2;
  if (10 < uVar5) {
    uVar5 = 10;
  }
  uVar5 = (int)((0x14 - uVar5) * ((int)((uint)bVar1 * iVar6) / 100)) / 0x14;
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bd2c4,0x271,DAT_005bd2c0,param_1,uVar5);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_005bd2c8,DAT_005bd2c8,param_1,uVar5);
  }
  driver_a6ng_write_register(0xe2,uVar5 & 0xff,0);
  FUN_004910f4(1);
  return;
}

