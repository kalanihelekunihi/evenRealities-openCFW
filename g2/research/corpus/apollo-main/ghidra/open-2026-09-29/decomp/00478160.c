
void APP_ConnectParamESSSetFastMode(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  uint uVar4;
  
  piVar1 = DAT_004786e4;
  if ((*DAT_004786e8 != '\0') && (*DAT_004786e4 != 0)) {
    iVar3 = osKernelGetTickCount();
    uVar4 = iVar3 - *piVar1;
    if (uVar4 < 30000) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_0047872c,0x1e8,DAT_00478728,uVar4,30000 - uVar4
                     ,in_r3);
      }
      iVar3 = FUN_0043d0ce();
      if ((-1 < iVar3 << 0x1f) && (iVar3 = FUN_0043d0ce(), -1 < iVar3 << 0x1d)) {
        return;
      }
      compress_log_output(0x10800000,DAT_00478730,DAT_00478730,uVar4,30000 - uVar4);
      return;
    }
  }
  uVar2 = DAT_00478724;
  fw_event_loop_remove_delayed(DAT_00478724);
  fw_event_loop_push_delayed(uVar2,0xa3,0);
  return;
}

