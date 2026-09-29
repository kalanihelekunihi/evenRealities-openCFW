
void FUN_00548014(void)

{
  undefined4 *puVar1;
  byte bVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 in_r3;
  uint auStack_18 [2];
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x59e,DAT_00548b44);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b54,DAT_00548b54);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar5 = FUN_0043e0e0(*DAT_00548558,1);
    auStack_18[0] = (uVar5 ^ 1) & 0xff;
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x59f,DAT_00548b58);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    bVar2 = FUN_0043e0e0(*DAT_00548558,1);
    compress_log_output(0x10400000,DAT_00548b5c,DAT_00548b5c,bVar2 ^ 1);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    bVar2 = FUN_00545588(*DAT_00548558,0);
    auStack_18[0] = (uint)bVar2;
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x5a0,DAT_00548b60);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    uVar3 = FUN_00545588(*DAT_00548558,0);
    compress_log_output(0x10400000,DAT_00548b64,DAT_00548b64,uVar3);
  }
  *DAT_00548550 = 0;
  puVar1 = DAT_00548b68;
  iVar4 = ui_common_api_fn_00509dfa(*DAT_00548b68);
  if (iVar4 != 0) {
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x5a4,DAT_00548b6c);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b70,DAT_00548b70);
  }
  FUN_0043c0e4(auStack_18,5,0);
  ui_common_api_fn_00509e14(*puVar1,auStack_18,5);
  if ((auStack_18[0] & 0xff) != 10) {
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x5aa,DAT_00548b74);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548b78,DAT_00548b78);
  }
  if (*DAT_00548b7c == 0) {
    *DAT_00548b7c = 1;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x5ad,DAT_00548b80);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00548b84,DAT_00548b84);
    }
    FUN_0054853a();
    return;
  }
  *DAT_00548b7c = 0;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,DAT_00548b48,0x5b1,DAT_00548b88);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00548f24,DAT_00548f24);
  }
  FUN_00548542();
  return;
}

