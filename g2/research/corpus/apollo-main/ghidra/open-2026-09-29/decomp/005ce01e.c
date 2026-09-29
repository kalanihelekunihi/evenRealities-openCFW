
void FUN_005ce01e(void)

{
  int iVar1;
  
  FUN_004910f4(200);
  FUN_005bf0bc();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005ce158,DAT_005ce154,DAT_005ce1ac,0x50,DAT_005ce1a8);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005ce058:
    compress_log_output(0x10000000,DAT_005ce1b0,DAT_005ce1b0);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005ce058;
  }
  FUN_005cdd6c();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_005ce158,DAT_005ce154,DAT_005ce1ac,0x56,DAT_005ce1b4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005ce094:
    compress_log_output(0x8000000,DAT_005ce1b8,DAT_005ce1b8);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005ce094;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_005ce158,DAT_005ce154,DAT_005ce1ac,0x57,DAT_005ce1c0,DAT_005ce1bc);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005ce0d0:
    compress_log_output(0x8400000,DAT_005ce1c4,DAT_005ce1c4,DAT_005ce1bc);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005ce0d0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_005ce158,DAT_005ce154,DAT_005ce1ac,0x58,DAT_005ce1d0,PTR_s_2_2_6_10_005ce140,
                 DAT_005ce1cc,DAT_005ce1c8);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005ce12c;
  }
  compress_log_output(0x8c00000,DAT_005ce1d4,DAT_005ce1d4,PTR_s_2_2_6_10_005ce140,DAT_005ce1cc,
                      DAT_005ce1c8);
LAB_005ce12c:
  task_vote_init();
  (*(code *)*DAT_005ce1d8)();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

