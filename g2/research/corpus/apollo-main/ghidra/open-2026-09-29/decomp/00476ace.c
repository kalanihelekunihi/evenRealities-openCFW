
undefined8 fw_event_loop_remove_delayed(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  byte bVar5;
  
  puVar1 = DAT_00476c1c;
  bVar5 = 0;
  if (*DAT_00476c2c == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x11e;
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476ca4,0x11e,DAT_00476ca0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00476ca8,DAT_00476ca8);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = osMutexAcquire(*DAT_00476c1c,0xffffffff);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x124;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476ca4,0x124,DAT_00476cac);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00476cb0);
      }
    }
    for (iVar2 = 0; iVar2 < 0x40; iVar2 = iVar2 + 1) {
      if (param_1 == *(int *)(DAT_00476c6c + iVar2 * 4)) {
        *(undefined4 *)(DAT_00476c6c + iVar2 * 4) = 0;
        bVar5 = 1;
      }
    }
    iVar2 = osMutexRelease(*puVar1);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x12e;
        FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476ca4,0x12e,DAT_00476cb4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00476cb8,DAT_00476cb8);
      }
    }
    if (bVar5 != 0) {
      iVar2 = osKernelGetTickCount();
      iVar4 = *DAT_00476c80;
      osTimerStop(*DAT_00476c0c);
      fw_event_loop_timer_callback(iVar2 - iVar4 | 0xff000000);
    }
    uVar3 = (uint)bVar5;
  }
  return CONCAT44(param_3,uVar3);
}

