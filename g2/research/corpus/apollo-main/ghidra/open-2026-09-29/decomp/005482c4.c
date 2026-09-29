
void FUN_005482c4(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 in_r3;
  char acStack_18 [8];
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b90,0x5ba,DAT_00548b8c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b94,DAT_00548b94);
  }
  *DAT_00548550 = 0;
  puVar1 = DAT_00548b68;
  iVar2 = ui_common_api_fn_00509dfa(*DAT_00548b68);
  if (iVar2 != 0) {
    return;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b90,0x5be,DAT_00548b6c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b70);
  }
  FUN_0043c0e4(acStack_18,5,0);
  ui_common_api_fn_00509e14(*puVar1,acStack_18,5);
  if (acStack_18[0] != '\n') {
    return;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b90,0x5c4,DAT_00548b74);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b78,DAT_00548b78);
  }
  if (*DAT_00548b7c == 0) {
    *DAT_00548b7c = 1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b90,0x5c7,DAT_00548b80);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00548b84,DAT_00548b84);
    }
    FUN_0054853a();
    return;
  }
  *DAT_00548b7c = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b90,0x5cb,DAT_00548b88);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548f24,DAT_00548f24);
  }
  FUN_00548542();
  return;
}

