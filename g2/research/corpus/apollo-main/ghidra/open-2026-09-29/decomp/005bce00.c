
undefined8 am_devices_hongshi_status_recovery(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_hongshi_status_abnormal__do_powe_005bd328;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x38b;
    FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_recove_005bd32c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_005bce46;
  }
  compress_log_output(0x4000000,PTR_s__driver_a6n_g_hongshi_status_abn_005bd330,
                      PTR_s__driver_a6n_g_hongshi_status_abn_005bd330);
LAB_005bce46:
  hongshi_power_off_sequence();
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_hongshi_power_down_done_005bd334;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x38e;
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_recove_005bd32c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__driver_a6n_g_hongshi_power_down_005bd338,
                        PTR_s__driver_a6n_g_hongshi_power_down_005bd338);
  }
  FUN_004910f4(1);
  hongshi_power_on_sequence();
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_hongshi_power_up_done_005bd33c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x392;
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_recove_005bd32c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__driver_a6n_g_hongshi_power_up_d_005bd340,
                        PTR_s__driver_a6n_g_hongshi_power_up_d_005bd340);
  }
  am_devices_mspi_hongshi_init(0);
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_hongshi_driver_init_done_005bd344;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x395;
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_recove_005bd32c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__driver_a6n_g_hongshi_driver_ini_005bd348,
                        PTR_s__driver_a6n_g_hongshi_driver_ini_005bd348);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

