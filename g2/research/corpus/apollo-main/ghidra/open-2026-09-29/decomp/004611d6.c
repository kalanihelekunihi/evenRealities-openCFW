
void FUN_004611d6(void)

{
  int iVar1;
  char local_14;
  undefined1 local_13;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_004615e4,0x272,DAT_004615e0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004615e8,DAT_004615e8);
  }
  *DAT_004615b0 = 0;
  iVar1 = FUN_004602b6();
  if (iVar1 == 0) {
    FUN_0043c0e4(&local_14,10,0);
    FUN_0043c0e4(&local_14,10,0);
    FUN_004602ca(&local_14,5);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_004615e4,0x279,DAT_004615b4,local_14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004615b8,DAT_004615b8,local_14);
    }
    if (local_14 == '\n') {
      FUN_00461620(2);
    }
    else if (local_14 == 'D') {
      FUN_00461620(1);
    }
    else if (local_14 == 'E') {
      FUN_00461620(0);
    }
    else if (local_14 == 'F') {
      FUN_00462594(local_13);
    }
    else if ((local_14 == 'H') && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      FUN_00464c36(3,0,0,0);
    }
  }
  return;
}

