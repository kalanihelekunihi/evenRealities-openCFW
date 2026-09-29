
void FUN_00470e90(void)

{
  int iVar1;
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined2 local_18;
  undefined1 local_14;
  undefined1 local_d;
  
  FUN_00439c04(local_1c,DAT_00471130,0x18);
  local_14 = 0x10;
  local_18 = 0x6c;
  local_1c[0] = 8;
  local_d = 1;
  iVar1 = FUN_00470d7c(local_1c);
  if (iVar1 == 0) {
    FUN_0046f6ba(1);
    local_20[0] = 0x10;
    iVar1 = FUN_004c0f78(*DAT_004710ac,0x18,local_20);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_00471138,0x5b5,DAT_00471140);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00471144,DAT_00471144);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_00471138,0x5ae,DAT_00471134);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0047113c,DAT_0047113c);
    }
  }
  return;
}

