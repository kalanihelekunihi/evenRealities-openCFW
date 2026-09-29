
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0051283c(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*_DAT_00512c20 != '\0') goto LAB_00512890;
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_Fuel_gauge_not_initialized__init_00512c24;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x46f;
    FUN_0043d574(2,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_check_fuel_gauge_init_00512c28);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0051287e:
    compress_log_output(0x8000000,PTR_s__npmx_driver_Fuel_gauge_not_init_00512c2c,
                        PTR_s__npmx_driver_Fuel_gauge_not_init_00512c2c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0051287e;
  }
  FUN_00511c24();
LAB_00512890:
  return CONCAT44(unaff_r6,unaff_r5);
}

