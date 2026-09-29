
undefined8 flash_mode_reconfigure(void)

{
  int iVar1;
  undefined4 uVar2;
  int unaff_r4;
  undefined4 *unaff_r5;
  undefined4 in_stack_00000000;
  
  iVar1 = am_hal_mspi_device_configure();
  if (iVar1 == 0) {
    iVar1 = am_hal_mspi_enable(*unaff_r5);
    if (iVar1 == 0) {
      FUN_0041fadc(*(undefined4 *)*DAT_004210a0,*(undefined1 *)(unaff_r4 + 8));
      uVar2 = 0;
    }
    else {
      in_stack_00000000 = 0x59a;
      elog_output(2,DAT_00421034,DAT_00421030,DAT_00421098);
      uVar2 = 1;
    }
  }
  else {
    in_stack_00000000 = 0x592;
    elog_output(2,DAT_00421034,DAT_00421030,DAT_00421098);
    uVar2 = 1;
  }
  return CONCAT44(in_stack_00000000,uVar2);
}

