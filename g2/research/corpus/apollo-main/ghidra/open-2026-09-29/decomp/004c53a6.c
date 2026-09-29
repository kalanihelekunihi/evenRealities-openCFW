
void _thread_exit(void)

{
  int iVar1;
  
  FUN_004c9c3c(6);
  iVar1 = DAT_004c5648;
  if (*(int *)(DAT_004c5648 + 0xc) != 0) {
    osMessageQueueDelete(*(undefined4 *)(DAT_004c5648 + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c56f4,0x16a,DAT_004c56f0);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_004c53fa;
    }
    compress_log_output(0x10000000,DAT_004c56f8,DAT_004c56f8);
  }
LAB_004c53fa:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c56f4,0x16c,DAT_004c56fc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004c5700,DAT_004c5700);
  }
  do {
    osDelay(0xffffffff);
  } while( true );
}

