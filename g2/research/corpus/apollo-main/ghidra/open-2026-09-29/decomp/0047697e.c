
undefined8
fw_event_loop_push_delayed(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint unaff_r4;
  int iVar5;
  undefined4 local_28;
  undefined4 local_24;
  
  piVar2 = DAT_00476c2c;
  local_28 = param_3;
  local_24 = param_4;
  if (*DAT_00476c2c == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_24 = DAT_00476c84;
      local_28 = 0xef;
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c88);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00476c8c,DAT_00476c8c);
    }
    do {
      osDelay(10);
    } while (*piVar2 == 0);
  }
  puVar1 = DAT_00476c1c;
  if (param_3 < 2) {
    fw_event_loop_push(param_1,param_2,0xffffffff);
  }
  else {
    iVar3 = osMutexAcquire(*DAT_00476c1c,0xffffffff);
    if (iVar3 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_24 = DAT_00476c90;
        local_28 = 0x100;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c88);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00476c94,DAT_00476c94);
      }
    }
    iVar3 = DAT_00476c6c;
    for (iVar5 = 0; (iVar5 < 0x40 && (*(int *)(DAT_00476c6c + iVar5 * 4) != 0)); iVar5 = iVar5 + 1)
    {
    }
    if (iVar5 < 0x40) {
      *(undefined4 *)(DAT_00476c6c + iVar5 * 4) = param_1;
      *(undefined4 *)(iVar3 + iVar5 * 4 + 0x100) = param_2;
      iVar4 = osKernelGetTickCount();
      unaff_r4 = iVar4 - *DAT_00476c80;
      *(uint *)(iVar3 + iVar5 * 4 + 0x200) = unaff_r4 + param_3;
    }
    iVar3 = osMutexRelease(*puVar1);
    if (iVar3 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_24 = DAT_00476c98;
        local_28 = 0x110;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c88);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00476c9c,DAT_00476c9c);
      }
    }
    if (iVar5 < 0x40) {
      osTimerStop(*DAT_00476c0c);
      fw_event_loop_timer_callback(unaff_r4 | 0xff000000);
    }
  }
  return CONCAT44(local_24,local_28);
}

