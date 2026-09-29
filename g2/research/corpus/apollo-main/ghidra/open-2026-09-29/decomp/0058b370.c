
undefined8
teleprompt_page_data_deinit
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 local_18;
  undefined4 local_14;
  
  piVar2 = DAT_0058bc40;
  local_18 = param_3;
  local_14 = param_4;
  if (*DAT_0058bc40 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_0058bc44;
      local_18 = 0x16c;
      FUN_0043d574(4,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc48);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0058bc54,DAT_0058bc54);
    }
  }
  else {
    iVar4 = page_data_lock();
    iVar3 = DAT_0058b530;
    if (iVar4 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_0058bc58;
        local_18 = 0x170;
        FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc48);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058bc5c);
      }
    }
    else if (*(char *)(DAT_0058b530 + 0x51a0) == '\0') {
      semantic_page_data_unlock();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_0058bc44;
        local_18 = 0x175;
        FUN_0043d574(4,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc48);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0058bc54,DAT_0058bc54);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_14 = DAT_0058bc60;
        local_18 = 0x178;
        FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc48);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0058bc64,DAT_0058bc64);
      }
      semantic_preload_timer_stop();
      piVar1 = DAT_0058bc18;
      if (*DAT_0058bc18 != 0) {
        osTimerDelete(*DAT_0058bc18);
        *piVar1 = 0;
      }
      FUN_0043c0e4(iVar3,0x51a4,0);
      semantic_page_data_unlock();
      if (*piVar2 != 0) {
        osMutexDelete(*piVar2);
        *piVar2 = 0;
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_0058bc68;
        local_18 = 0x184;
        FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bc48);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0058bc6c,DAT_0058bc6c);
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

