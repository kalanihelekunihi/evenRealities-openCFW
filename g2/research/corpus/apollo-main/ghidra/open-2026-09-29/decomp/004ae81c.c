
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 als_function_36(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*DAT_004ae984 == 0) {
    uVar1 = 1;
  }
  else {
    if (param_1 < 0x65) {
      if (param_1 < 2) {
        param_1 = 2;
      }
    }
    else {
      param_1 = 100;
    }
    param_1 = param_1 & 0xfffffffe;
    if (*_DAT_004aea20 == 0) {
      iVar2 = *_DAT_004ae8e4;
    }
    else {
      iVar2 = *_DAT_004aea20;
    }
    als_function_19(iVar2);
    als_function_21(param_1);
    als_function_19(iVar2);
    als_function_13();
    *DAT_004ae8dc = param_1;
    *DAT_004ae8e0 = param_1;
    *DAT_004ae950 = 1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,PTR_s_DRV_ALSManualSetBrightness_004aea2c,0x295,
                   PTR_s_manual_brightness_learn__brightn_004aea28,param_1,*_DAT_004aea24,
                   *DAT_004ae8d4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__sensor_als_manual_brightness_le_004aea30,
                          PTR_s__sensor_als_manual_brightness_le_004aea30,param_1,*_DAT_004aea24,
                          *DAT_004ae8d4);
    }
    uVar1 = 0;
  }
  return uVar1;
}

