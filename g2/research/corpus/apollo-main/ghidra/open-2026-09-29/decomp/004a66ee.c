
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
HUB_ResourceInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = DAT_004a6ecc;
  uVar2 = osMessageQueueNew(0x32,8,0);
  *(undefined4 *)(iVar3 + 0xc) = uVar2;
  if (*(int *)(iVar3 + 0xc) == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 99;
      param_2 = PTR_s__HUB_ResourceInit_osMessageQueue_004a7144;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ResourceInit_004a7148,99,
                   PTR_s__HUB_ResourceInit_osMessageQueue_004a7144,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_hub__HUB_ResourceInit_os_004a714c);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0x65;
      param_2 = PTR_s__HUB_ResourceInit_osMessageQueue_004a7150;
      FUN_0043d574(4,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ResourceInit_004a7148,0x65,
                   PTR_s__HUB_ResourceInit_osMessageQueue_004a7150,*(undefined4 *)(iVar3 + 0xc),
                   param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__sensor_hub__HUB_ResourceInit_os_004a7154,
                          PTR_s__sensor_hub__HUB_ResourceInit_os_004a7154,
                          *(undefined4 *)(iVar3 + 0xc));
    }
  }
  piVar1 = DAT_004a7158;
  if (*DAT_004a7158 == 0) {
    iVar3 = osTimerNew(0x4a696d,1,0,PTR_DAT_004a715c);
    *piVar1 = iVar3;
    if (*piVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0x6b;
        param_2 = PTR_s__HUB_ResourceInit_osTimerNew_fai_004a7160;
        FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ResourceInit_004a7148);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sensor_hub__HUB_ResourceInit_os_004a7164,
                            PTR_s__sensor_hub__HUB_ResourceInit_os_004a7164);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0x6d;
        param_2 = PTR_s__HUB_ResourceInit_osTimerNew_suc_004a7168;
        FUN_0043d574(4,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_ResourceInit_004a7148);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_004a7344,_DAT_004a7344);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

