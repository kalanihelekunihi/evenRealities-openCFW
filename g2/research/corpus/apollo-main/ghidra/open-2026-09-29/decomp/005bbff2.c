
/* WARNING: Removing unreachable block (ram,0x005bc42c) */
/* WARNING: Removing unreachable block (ram,0x005bc436) */

undefined4 am_devices_mspi_hongshi_configure(void)

{
  undefined4 *puVar1;
  undefined1 uVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 in_r3;
  uint uVar6;
  uint uVar7;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uVar6 = 0;
  local_14 = 0;
  local_18 = 0;
  uStack_10 = in_r3;
  uVar4 = service_settings_auto_brightness();
  SVC_Settings_BrightnessLevelToLumAndCurrent(uVar4,&local_18,&local_14);
  driver_a6ng_write_register(0x55,0,1);
  while (iVar5 = DAT_005bcc00, uVar6 < 0x32) {
    uVar2 = *(undefined1 *)(DAT_005bcc00 + uVar6 + 1);
    if (*(char *)(DAT_005bcc00 + uVar6) == '\0') {
      driver_a6ng_write_register(uVar2,*(undefined1 *)(DAT_005bcc00 + uVar6 + 2),0);
    }
    else {
      driver_a6ng_write_register(uVar2,*(undefined1 *)(DAT_005bcc00 + uVar6 + 2),1);
    }
    uVar7 = uVar6 + 3;
    if (*(char *)(iVar5 + uVar7) == -1) {
      FUN_00491102(*(undefined1 *)(iVar5 + uVar7 + 1));
      uVar7 = uVar6 + 5;
    }
    uVar6 = uVar7;
    if (*(char *)(iVar5 + uVar6) == -0x12) {
      osDelay(*(undefined1 *)(iVar5 + uVar6 + 1));
      uVar6 = uVar6 + 2;
    }
  }
  FUN_00491102(100);
  driver_a6ng_write_register(0xf0,0x28,0);
  FUN_00491102(100);
  uVar2 = am_devices_mspi_hongshi_read_bank(0xf0,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1aa,DAT_005bcc04,uVar2);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005bcc08,DAT_005bcc08,uVar2);
  }
  FUN_00491102(100);
  uVar2 = am_devices_mspi_hongshi_read_bank(0xbe,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1af,DAT_005bcc0c,uVar2);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcd34,DAT_005bcd34,uVar2);
  }
  FUN_00491102(100);
  cVar3 = am_devices_mspi_hongshi_read_bank(0,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1b3,DAT_005bcd38,cVar3);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcd3c,DAT_005bcd3c,cVar3);
  }
  if (cVar3 != '6') {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1b6,DAT_005bcd40,cVar3);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005bcde0,DAT_005bcde0,cVar3);
    }
  }
  FUN_00491102(100);
  cVar3 = am_devices_mspi_hongshi_read_bank(0xf1,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1bb,DAT_005bcde4,cVar3);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcde8,DAT_005bcde8,cVar3);
  }
  if (cVar3 != '?') {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1be,DAT_005bcdec,cVar3);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005bcdf0,DAT_005bcdf0,cVar3);
    }
  }
  FUN_00491102(100);
  cVar3 = am_devices_mspi_hongshi_read_bank(0x7e,1);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1c3,DAT_005bcdf4,cVar3);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcdf8,DAT_005bcdf8,cVar3);
  }
  if (cVar3 != '\x02') {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1c6,DAT_005bcdfc,cVar3);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005bcf28,DAT_005bcf28,cVar3);
    }
  }
  FUN_00491102(100);
  uVar2 = am_devices_mspi_hongshi_read_bank(0xa5,1);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1cc,DAT_005bcf2c,uVar2);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcf30,DAT_005bcf30,uVar2);
  }
  FUN_00491102(100);
  uVar2 = am_devices_mspi_hongshi_read_bank(0xe2,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1d1,DAT_005bcf34,uVar2);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005bcf38,DAT_005bcf38,uVar2);
  }
  FUN_004910f4(1);
  driver_a6ng_clear_framebuffer();
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcd30,0x1e6,DAT_005bcf3c,8,8);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_005bcf40,DAT_005bcf40,8,8);
  }
  puVar1 = DAT_005bcf44;
  uVar4 = service_settings_auto_brightness();
  *puVar1 = uVar4;
  am_devices_mspi_hongshi_setBrightness(*puVar1,0,0);
  FUN_004910f4(2);
  am_devices_hongshi_set_display_offset
            (*(undefined1 *)(DAT_005bcf48 + 0x2c),*(undefined1 *)(DAT_005bcf48 + 0x2d));
  return 0;
}

