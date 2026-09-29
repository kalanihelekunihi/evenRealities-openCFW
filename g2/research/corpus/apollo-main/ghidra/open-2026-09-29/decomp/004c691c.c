
undefined8
device_mgr_fn_004c691c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  
  piVar2 = DAT_004c6cd0;
  pcVar1 = DAT_004c6ca4;
  if (*DAT_004c6ca4 != '\0') {
    if (*DAT_004c6cd0 != 0) {
      uVar3 = xTaskGetTickCount();
      if (0xb4 < uVar3 / 1000 - *piVar2) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x1b8;
          param_3 = DAT_004c6cd4;
          FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,DAT_004c6cd8,0x1b8,DAT_004c6cd4,param_4);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004c6cdc,DAT_004c6cdc);
        }
        *pcVar1 = '\0';
        *piVar2 = 0;
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

