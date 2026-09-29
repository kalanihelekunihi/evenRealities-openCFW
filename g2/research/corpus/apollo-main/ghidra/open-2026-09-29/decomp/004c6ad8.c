
void device_mgr_fn_004c6ad8(void)

{
  int iVar1;
  char *pcVar2;
  ushort *puVar3;
  int iVar4;
  int iVar5;
  undefined4 in_r3;
  undefined1 auStack_38 [40];
  undefined4 uStack_10;
  
  puVar3 = DAT_004c6cec;
  pcVar2 = DAT_004c6ce8;
  iVar1 = DAT_004c6ca0;
  if ((*(int *)(DAT_004c6ca0 + 0xc) < -0x13) && (*DAT_004c6ce8 == '\0')) {
    *DAT_004c6cec = *DAT_004c6cec + 1;
    if (2 < *puVar3) {
      *puVar3 = 0;
      *pcVar2 = '\x01';
      uStack_10 = in_r3;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004c6c00,DAT_004c6bfc,DAT_004c6cf4,0x235,DAT_004c6cf0,*pcVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004c6cf8,DAT_004c6cf8,*pcVar2);
      }
      service_time_current_calendar_get(auStack_38);
      iVar4 = DAT_004c6ce4;
      FUN_00439c04(DAT_004c6ce4 + 0x80,auStack_38,0x28);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004c6c00,DAT_004c6bfc,DAT_004c6cf4,0x239,DAT_004c6cfc,
                     *(undefined4 *)(iVar4 + 0x8c),*(undefined4 *)(iVar4 + 0x90),
                     *(undefined4 *)(iVar4 + 0x94),*(undefined4 *)(iVar4 + 0x98),
                     *(undefined4 *)(iVar4 + 0x9c),*(undefined4 *)(iVar4 + 0xa0));
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x9800000,DAT_004c6d00,DAT_004c6d00,*(undefined4 *)(iVar4 + 0x8c),
                            *(undefined4 *)(iVar4 + 0x90),*(undefined4 *)(iVar4 + 0x94),
                            *(undefined4 *)(iVar4 + 0x98),*(undefined4 *)(iVar4 + 0x9c),
                            *(undefined4 *)(iVar4 + 0xa0));
      }
      SVC_NvdbWriteSysData(10,iVar1 + 4);
    }
  }
  else if (*DAT_004c6ce8 == '\0') {
    *DAT_004c6cec = 0;
  }
  return;
}

