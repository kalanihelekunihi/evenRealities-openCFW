
uint bq27427_checksum_dm_block(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  for (iVar1 = 0; iVar1 < 0x20; iVar1 = iVar1 + 1) {
    uVar2 = uVar2 + *(byte *)(param_1 + iVar1 + 2);
  }
  uVar2 = uVar2 & 0xff;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0xff - uVar2;
    param_1 = 0x185;
    param_2 = DAT_0053c01c;
    FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053c020,0x185,DAT_0053c01c,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0053c0dc,DAT_0053c0dc,0xff - uVar2,param_1,param_2,param_3);
  }
  return 0xff - uVar2 & 0xff;
}

