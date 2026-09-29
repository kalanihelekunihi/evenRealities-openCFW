
void _buzzerPlayVoice(void)

{
  int *piVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  piVar1 = DAT_00502cb4;
  if ((*DAT_00502cb4 == 0) || (*(char *)(*DAT_00502cb4 + (uint)*DAT_00502cb8) == '\0')) {
    *DAT_00502cb8 = 0;
    pcVar2 = DAT_00502cbc;
    if ((*piVar1 == 0) || (*DAT_00502cbc = *DAT_00502cbc + -1, *pcVar2 == '\0')) {
      buzzer_beep_stop(1);
      *piVar1 = 0;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00502cd0,DAT_00502ccc,DAT_00502cc8,0xe3,DAT_00502cdc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00502ce0);
      }
    }
    else {
      buzzer_beep_stop(0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00502cd0,DAT_00502ccc,DAT_00502cc8,0xdd,DAT_00502cc4,*pcVar2,
                     *DAT_00502cc0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00502cd4,DAT_00502cd4,*pcVar2,*DAT_00502cc0);
      }
      osTimerStart(*DAT_00502cd8,*DAT_00502cc0);
    }
  }
  else {
    if (*(byte *)(*DAT_00502cb4 + (uint)*DAT_00502cb8) < 8) {
      iVar3 = (uint)*(byte *)(*DAT_00502cb4 + (uint)*DAT_00502cb8 + 1) * 7 +
              (uint)*(byte *)(*DAT_00502cb4 + (uint)*DAT_00502cb8) + -1;
      iVar3 = DAT_00502ce4 /
              (int)(0xffff - (uint)CONCAT11(*(undefined1 *)(DAT_00502ce8 + iVar3),
                                            *(undefined1 *)(DAT_00502cec + iVar3)));
    }
    else {
      iVar3 = 0;
    }
    sVar5 = (ushort)*(byte *)(*DAT_00502cb4 + (uint)*DAT_00502cb8 + 2) * 0x3e;
    *DAT_00502cb8 = *DAT_00502cb8 + 3;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00502cd0,DAT_00502ccc,DAT_00502cc8,0xf3,DAT_00502cf0,iVar3,sVar5,
                   *DAT_00502cbc);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_00502cf4,DAT_00502cf4,iVar3,sVar5,*DAT_00502cbc);
    }
    if (iVar3 == 0) {
      buzzer_beep_stop(0);
    }
    else {
      buzzer_beep_start(iVar3,0x1e);
    }
    osTimerStart(*DAT_00502cd8,sVar5);
  }
  return;
}

