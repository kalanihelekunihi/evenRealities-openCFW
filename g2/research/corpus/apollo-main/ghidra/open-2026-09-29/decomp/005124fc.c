
undefined8 FUN_005124fc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  byte *pbVar2;
  undefined4 local_10;
  undefined *local_c;
  
  local_10 = param_3;
  local_c = param_4;
  iVar1 = FUN_0055face(DAT_00512b14,1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s_p_ldsw2_is_null__00512bd4;
      local_10 = 0x3eb;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_configure_lsdw2_voltage_00512bd8)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_ldsw2_is_null__00512bdc,
                          PTR_s__npmx_driver_p_ldsw2_is_null__00512bdc);
    }
  }
  else {
    pbVar2 = (byte *)FUN_0050938e(1);
    if (3 < *pbVar2) {
      local_10 = *(undefined4 *)PTR_DAT_00512be0;
      local_c = *(undefined **)(PTR_DAT_00512be0 + 4);
      FUN_0055fb7c(iVar1,0);
      FUN_0055fae2(iVar1,&local_10);
      FUN_0055fad8(iVar1,0);
    }
  }
  return CONCAT44(local_c,local_10);
}

