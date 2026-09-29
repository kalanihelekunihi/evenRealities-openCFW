
undefined8 FUN_00512410(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0055fa0e(DAT_00512b14,0);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00512a68;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x3bf;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_disable_buck1_voltage_00512bbc);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_buck1_is_null__00512bb4,
                          PTR_s__npmx_driver_p_buck1_is_null__00512bb4);
    }
  }
  else {
    FUN_0055fa18(iVar2,1);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

