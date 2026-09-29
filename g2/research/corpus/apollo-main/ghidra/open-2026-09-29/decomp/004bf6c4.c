
undefined8
_anccResetStateMachine(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x2ec;
    param_3 = DAT_004bf964;
    FUN_0043d574(4,DAT_004bf92c,DAT_004bf928,DAT_004bf968,0x2ec,DAT_004bf964,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004bf96c,DAT_004bf96c);
  }
  iVar1 = DAT_004bf970;
  *(undefined1 *)(DAT_004bf970 + 10) = 0;
  *(undefined2 *)(iVar1 + 0xe) = 0;
  *(undefined2 *)(iVar1 + 0xc) = 0;
  *(undefined2 *)(iVar1 + 0x14) = 0;
  *(undefined1 *)(iVar1 + 0x12) = 0;
  *(undefined2 *)(iVar1 + 0x10) = 0;
  *(undefined1 *)(iVar1 + 0x16) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  FUN_0043c0e4(iVar1 + 0x31c,0x40,0);
  FUN_0043c0e4(iVar1 + 0x35c,0x200,0);
  return CONCAT44(param_3,param_2);
}

