
undefined8 FUN_005125a8(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0055face(DAT_00512b14,1);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_p_ldsw2_is_null__00512bd4;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x41e;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_disable_lsdw2_voltage_00512be4);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_ldsw2_is_null__00512bdc,
                          PTR_s__npmx_driver_p_ldsw2_is_null__00512bdc);
    }
  }
  else {
    FUN_0055fad8(iVar2,1);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

