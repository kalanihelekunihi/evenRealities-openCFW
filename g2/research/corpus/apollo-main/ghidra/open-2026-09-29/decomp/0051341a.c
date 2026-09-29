
void INP_ThreadExit(void)

{
  int iVar1;
  
  FUN_004c9c3c(4);
  iVar1 = DAT_005134b4;
  if (*(int *)(DAT_005134b4 + 0xc) != 0) {
    osMessageQueueDelete(*(undefined4 *)(DAT_005134b4 + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_0051356c,0x166,DAT_00513568);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_0051346e;
    }
    compress_log_output(0x10000000,DAT_00513570,DAT_00513570);
  }
LAB_0051346e:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_0051356c,0x168,DAT_00513574);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00513578,DAT_00513578);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

