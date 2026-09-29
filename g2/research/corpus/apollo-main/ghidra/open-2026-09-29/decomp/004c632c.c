
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 device_mgr_fn_004c632c(undefined4 param_1,undefined *param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  CHG_InitBatterySync();
  func_0x004ff8d4();
  FUN_004ac02a();
  SVC_Settings_Init();
  FUN_00466660();
  iVar3 = DAT_004c6c08;
  uVar2 = osMessageQueueNew(0x32,8,0);
  *(undefined4 *)(iVar3 + 0xc) = uVar2;
  if (*(int *)(iVar3 + 0xc) == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xa7;
      param_2 = PTR_s__DEV_ResourceInit_osMessageQueue_004c6c20;
      FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_ResourceInit_004c6c24);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__device_mgr__DEV_ResourceInit_os_004c6c28,
                          PTR_s__device_mgr__DEV_ResourceInit_os_004c6c28);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0xab;
      param_2 = PTR_s__DEV_ResourceInit_osMessageQueue_004c6c2c;
      FUN_0043d574(4,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_ResourceInit_004c6c24,0xab,
                   PTR_s__DEV_ResourceInit_osMessageQueue_004c6c2c,*(undefined4 *)(iVar3 + 0xc));
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__device_mgr__DEV_ResourceInit_os_004c6c30,
                          PTR_s__device_mgr__DEV_ResourceInit_os_004c6c30,
                          *(undefined4 *)(iVar3 + 0xc));
    }
  }
  piVar1 = _DAT_004c6c34;
  if (*_DAT_004c6c34 == 0) {
    iVar3 = osTimerNew(0x4c661d,1,0,PTR_DAT_004c6c38);
    *piVar1 = iVar3;
    if (*piVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0xb5;
        param_2 = PTR_s__DEV_ResourceInit_osTimerNew_fai_004c6c3c;
        FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_ResourceInit_004c6c24);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__device_mgr__DEV_ResourceInit_os_004c6c40,
                            PTR_s__device_mgr__DEV_ResourceInit_os_004c6c40);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0xb9;
        param_2 = PTR_s__DEV_ResourceInit_osTimerNew_suc_004c6c44;
        FUN_0043d574(4,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_ResourceInit_004c6c24);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__device_mgr__DEV_ResourceInit_os_004c6c48,
                            PTR_s__device_mgr__DEV_ResourceInit_os_004c6c48);
      }
      osTimerStart(*piVar1,1000);
    }
  }
  return CONCAT44(param_2,param_1);
}

