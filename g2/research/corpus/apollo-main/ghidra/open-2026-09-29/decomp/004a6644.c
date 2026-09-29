
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
HUB_ThreadInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_004a6ecc;
  uVar1 = osThreadNew(0x4a6869,0,PTR_LAB_004a6ed0);
  *(undefined4 *)(iVar2 + 8) = uVar1;
  if (*(int *)(iVar2 + 8) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x59;
      param_2 = PTR_s__HUB_ThreadInit_osThreadNew_fail_004a6ed4;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ThreadInit_004a6ed8,0x59,
                   PTR_s__HUB_ThreadInit_osThreadNew_fail_004a6ed4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_004a6ee4);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x5b;
      param_2 = PTR_s__HUB_ThreadInit_osThreadNew_0x_x_004a713c;
      FUN_0043d574(4,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ThreadInit_004a6ed8,0x5b,
                   PTR_s__HUB_ThreadInit_osThreadNew_0x_x_004a713c,*(undefined4 *)(iVar2 + 8),
                   param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sensor_hub__HUB_ThreadInit_osTh_004a7140,
                          PTR_s__sensor_hub__HUB_ThreadInit_osTh_004a7140,*(undefined4 *)(iVar2 + 8)
                         );
    }
  }
  return CONCAT44(param_2,param_1);
}

