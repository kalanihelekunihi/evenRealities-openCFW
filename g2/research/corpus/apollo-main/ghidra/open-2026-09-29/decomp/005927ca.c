
/* WARNING: Removing unreachable block (ram,0x0059283e) */
/* WARNING: Removing unreachable block (ram,0x00592846) */
/* WARNING: Removing unreachable block (ram,0x0059286e) */
/* WARNING: Removing unreachable block (ram,0x00592876) */
/* WARNING: Removing unreachable block (ram,0x0059287e) */
/* WARNING: Removing unreachable block (ram,0x00592894) */
/* WARNING: Removing unreachable block (ram,0x005928a0) */
/* WARNING: Removing unreachable block (ram,0x005928a8) */
/* WARNING: Removing unreachable block (ram,0x005928d0) */
/* WARNING: Removing unreachable block (ram,0x005928d8) */
/* WARNING: Removing unreachable block (ram,0x005928e0) */
/* WARNING: Removing unreachable block (ram,0x005928f6) */
/* WARNING: Type propagation algorithm not settling */

undefined4 am_devices_mspi_jbd4010_configure(void)

{
  undefined4 uVar1;
  int iVar2;
  uint local_38;
  uint local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined1 local_24;
  undefined1 local_23;
  uint local_18 [2];
  
  local_18[0] = 0;
  local_18[1] = 0;
  uVar1 = service_settings_auto_brightness();
  SVC_Settings_BrightnessLevelToLumAndCurrent(uVar1,local_18 + 1,local_18);
  local_28 = 0;
  jbd4010_write_command(0x66,&local_28,0);
  FUN_004910f4(1);
  jbd4010_write_command(0x99,&local_28,0);
  osDelay(0x32);
  jbd4010_write_command(6,&local_28,0);
  FUN_0043c0e4(&local_24,10,0);
  local_24 = 0x10;
  jbd4010_write_command(1,&local_24,1);
  jbd4010_clear_display();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_2c = 10;
    local_30 = 0xc;
    local_34 = DAT_00593330;
    local_38 = 0x114;
    FUN_0043d574(3,DAT_00593320,DAT_0059331c,DAT_00593318);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    local_38 = 10;
    compress_log_output(0xc800000,DAT_00593524,DAT_00593524,0xc);
  }
  local_24 = 0;
  local_23 = 0;
  jbd4010_write_command(0xc0,&local_24,2);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  local_24 = 0;
  local_23 = 0x14;
  jbd4010_write_command(0xc0,&local_24,2);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  local_24 = 0x18;
  local_23 = 0;
  jbd4010_write_command(0xc0,&local_24,2);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  local_24 = 0x18;
  local_23 = 0x14;
  jbd4010_write_command(0xc0,&local_24,2);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  local_24 = 0xc;
  local_23 = 10;
  jbd4010_write_command(0xc0,&local_24,2);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  jbd4010_write_command(0x73,&local_28,0);
  FUN_00491102(100);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  jbd4010_write_command(0x73,&local_28,0);
  FUN_00491102(100);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  local_38 = local_18[0] >> 8;
  local_34 = local_18[0];
  jbd4010_write_command(0x36,&local_38,2);
  local_24 = (undefined1)local_18[1];
  jbd4010_write_command(0x46,&local_24,1);
  local_24 = 4;
  jbd4010_write_command(0x31,&local_24,1);
  jbd4010_write_command(0xa3,&local_28,0);
  jbd4010_write_command(0x97,&local_28,0);
  FUN_004910f4(1);
  am_devices_jbd4010_set_display_offset
            (*(undefined1 *)(DAT_00593738 + 0x2c),*(undefined1 *)(DAT_00593738 + 0x2d));
  return 0;
}

