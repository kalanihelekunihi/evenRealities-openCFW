
undefined8
fw_event_loop_timer_callback(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = 0xffffffff;
  uVar8 = param_1;
  FUN_004420d0(0);
  puVar2 = DAT_00476c5c;
  uVar7 = *DAT_00476c5c;
  FUN_004420e8();
  puVar1 = DAT_00476c1c;
  if ((param_1 & 0xff000000) == 0xff000000) {
    uVar7 = param_1 & 0xffffff;
  }
  iVar4 = osMutexAcquire(*DAT_00476c1c,0xffffffff);
  if (iVar4 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar8 = 0xb8;
      param_2 = DAT_00476c60;
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c64,0xb8,DAT_00476c60,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00476c68,DAT_00476c68);
    }
  }
  for (iVar4 = 0; iVar3 = DAT_00476c6c, iVar4 < 0x40; iVar4 = iVar4 + 1) {
    if (*(int *)(DAT_00476c6c + iVar4 * 4) != 0) {
      if (uVar7 < *(uint *)(DAT_00476c6c + iVar4 * 4 + 0x200)) {
        *(uint *)(DAT_00476c6c + iVar4 * 4 + 0x200) =
             *(int *)(DAT_00476c6c + iVar4 * 4 + 0x200) - uVar7;
      }
      else {
        *(undefined4 *)(DAT_00476c6c + iVar4 * 4 + 0x200) = 0;
      }
      if (*(int *)(iVar3 + iVar4 * 4 + 0x200) == 0) {
        uVar5 = *(undefined4 *)(iVar3 + iVar4 * 4);
        *(undefined4 *)(iVar3 + iVar4 * 4) = 0;
        fw_event_loop_push(uVar5,*(undefined4 *)(iVar3 + iVar4 * 4 + 0x100),1);
      }
    }
  }
  for (iVar4 = 0; iVar4 < 0x40; iVar4 = iVar4 + 1) {
    if ((*(int *)(DAT_00476c6c + iVar4 * 4) != 0) &&
       (*(uint *)(DAT_00476c6c + iVar4 * 4 + 0x200) < uVar6)) {
      uVar6 = *(uint *)(DAT_00476c6c + iVar4 * 4 + 0x200);
    }
  }
  iVar4 = osMutexRelease(*puVar1);
  if (iVar4 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar8 = 0xd5;
      param_2 = DAT_00476c70;
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c64);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00476c74);
    }
  }
  if ((uVar6 == 0x7fffffff) || (uVar6 == 0)) goto LAB_0047697a;
  FUN_004420d0();
  *puVar2 = uVar6;
  FUN_004420e8();
  uVar7 = osTimerStart(*DAT_00476c0c,uVar6);
  if (uVar7 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar8 = 0xe1;
      param_2 = DAT_00476c78;
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c64,0xe1,DAT_00476c78,uVar6,uVar7);
    }
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1f) {
      iVar4 = FUN_0043d0ce();
      if (-1 < iVar4 << 0x1d) goto LAB_00476972;
    }
    compress_log_output(0x4800000,DAT_00476c7c,DAT_00476c7c,uVar6);
    uVar8 = uVar7;
  }
LAB_00476972:
  uVar5 = osKernelGetTickCount();
  *DAT_00476c80 = uVar5;
LAB_0047697a:
  return CONCAT44(param_2,uVar8);
}

