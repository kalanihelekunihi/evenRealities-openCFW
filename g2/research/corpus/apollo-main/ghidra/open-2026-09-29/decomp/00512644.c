
undefined8 FUN_00512644(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  char *pcVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Start_to_check_npm1300_init___00512be8;
    uStack_10 = 0x430;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__npmx_driver_Start_to_check_npm1_00512bf0,
                        PTR_s__npmx_driver_Start_to_check_npm1_00512bf0);
  }
  pcVar2 = (char *)FUN_0050938e(1);
  iVar1 = FUN_0043d0ce(7,0);
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Start_npmx_backend_init___00512bf4;
    uStack_10 = 0x440;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005126d4:
    compress_log_output(0x10000000,PTR_s__npmx_driver_Start_npmx_backend__00512bf8);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005126d4;
  }
  FUN_00511108();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Start_npmx_int_pin_configure___00512bfc;
    uStack_10 = 0x442;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0051271c:
    compress_log_output(0x10000000,PTR_s__npmx_driver_Start_npmx_int_pin__00512c00,
                        PTR_s__npmx_driver_Start_npmx_int_pin__00512c00);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0051271c;
  }
  FUN_005111e6();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Configure_bchg_vbat_low_charge_b_00512c04;
    uStack_10 = 0x444;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00512764:
    compress_log_output(0x10000000,PTR_s__npmx_driver_Configure_bchg_vbat_00512c08,
                        PTR_s__npmx_driver_Configure_bchg_vbat_00512c08);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00512764;
  }
  FUN_00512a34();
  FUN_00512a4c();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Start_npmx_application_configure_00512c0c;
    uStack_10 = 0x447;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005127b0:
    compress_log_output(0x10000000,PTR_s__npmx_driver_Start_npmx_applicat_00512c10,
                        PTR_s__npmx_driver_Start_npmx_applicat_00512c10);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005127b0;
  }
  FUN_00511342();
  FUN_004910f4(1);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Start_to_check_npm1300_init_done_00512c14;
    uStack_10 = 0x44d;
    FUN_0043d574(4,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_main_driver_init_00512bec);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0051280c;
  }
  compress_log_output(0x10000000,PTR_s__npmx_driver_Start_to_check_npm1_00512c18,
                      PTR_s__npmx_driver_Start_to_check_npm1_00512c18);
LAB_0051280c:
  FUN_00511c24();
  FUN_004910f4(0x32);
  FUN_0051238c();
  FUN_0051247c();
  if (*pcVar2 == '\x06') {
    FUN_005125a8();
  }
  return CONCAT44(uStack_c,uStack_10);
}

