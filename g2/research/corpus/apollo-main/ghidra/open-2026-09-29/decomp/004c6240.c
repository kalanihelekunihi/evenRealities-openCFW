
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
device_mgr_fn_004c6240(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x8b;
    param_2 = _DAT_004c6bf4;
    FUN_0043d574(4,DAT_004c6c00,DAT_004c6bfc,_DAT_004c6bf8,0x8b,_DAT_004c6bf4,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_004c6c04,_DAT_004c6c04);
  }
  iVar1 = DAT_004c6c08;
  uVar2 = osThreadNew(0x4c64c9,0,PTR_DAT_004c6c0c);
  *(undefined4 *)(iVar1 + 8) = uVar2;
  if (*(int *)(iVar1 + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x8f;
      param_2 = PTR_s__DEV_ThreadInit_osThreadNew_fail_004c6c10;
      FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,_DAT_004c6bf8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__device_mgr__DEV_ThreadInit_osTh_004c6c14);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x93;
      param_2 = PTR_s__DEV_ThreadInit_osThreadNew_0x_x_004c6c18;
      FUN_0043d574(4,DAT_004c6c00,DAT_004c6bfc,_DAT_004c6bf8,0x93,
                   PTR_s__DEV_ThreadInit_osThreadNew_0x_x_004c6c18,*(undefined4 *)(iVar1 + 8));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__device_mgr__DEV_ThreadInit_osTh_004c6c1c,
                          PTR_s__device_mgr__DEV_ThreadInit_osTh_004c6c1c,*(undefined4 *)(iVar1 + 8)
                         );
    }
  }
  return CONCAT44(param_2,param_1);
}

