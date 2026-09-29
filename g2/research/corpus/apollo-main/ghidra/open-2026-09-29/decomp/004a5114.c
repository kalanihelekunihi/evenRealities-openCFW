
void DRV_IMUCheckCompassEvent(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = osKernelGetTickCount();
  iVar4 = 0;
  if ((*DAT_004a5d28 == '\0') && (*DAT_004a5d2c == '\x01')) {
    *DAT_004a5d28 = '\x01';
    semantic_emit_imu_event(0x10,1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5e14,0x466,DAT_004a5d30);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a5d34,DAT_004a5d34);
    }
  }
  else if ((*DAT_004a5d28 == '\x01') && (*DAT_004a5d2c == '\0')) {
    *DAT_004a5d28 = '\0';
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5e14,0x46a,DAT_004a5e18);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a5e44);
    }
  }
  if (*DAT_004a56d0 <= (uint)(iVar2 - *DAT_004a5e48)) {
    *DAT_004a5e48 = iVar2;
    piVar1 = DAT_004a5ec4;
    iVar2 = *(int *)(DAT_004a5698 + 8);
    do {
      iVar2 = iVar2 + -1;
      if (iVar2 < 0) goto LAB_004a521e;
    } while ((*(byte *)(iVar2 * 0x70 + DAT_004a5698 + 0x10) & 0x3f) >> 5 == 0);
    iVar4 = (int)*(float *)(iVar2 * 0x70 + DAT_004a5698 + 0x74);
LAB_004a521e:
    iVar2 = FUN_00509694(iVar4 - *DAT_004a5ec4);
    if (*DAT_004a5b74 < iVar2) {
      semantic_emit_imu_event(9,iVar4);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5e14,0x478,DAT_004a5ec8,iVar4,*piVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_004a5eec,DAT_004a5eec,iVar4,*piVar1);
      }
      *piVar1 = iVar4;
    }
  }
  return;
}

