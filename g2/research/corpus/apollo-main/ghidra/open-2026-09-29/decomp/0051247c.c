
undefined8 FUN_0051247c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0055face(DAT_00512b14,0);
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_c = PTR_s_p_ldsw1_is_null__00512bc8;
      uStack_10 = 0x3dd;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_configure_lsdw1_voltage_00512bcc)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_ldsw1_is_null__00512bd0,
                          PTR_s__npmx_driver_p_ldsw1_is_null__00512bd0);
    }
  }
  else {
    FUN_0055fb7c(iVar1,1);
    func_0x0055fbe4(iVar1,8);
    FUN_0055fad8(iVar1,0);
  }
  return CONCAT44(uStack_c,uStack_10);
}

