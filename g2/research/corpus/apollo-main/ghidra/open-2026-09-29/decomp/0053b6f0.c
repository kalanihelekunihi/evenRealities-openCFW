
void bq27427_update_dm_block(int param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined1 *puVar3;
  
  puVar3 = (undefined1 *)(DAT_0053c1cc + (uint)param_2 * 8);
  uVar2 = (uint)(byte)puVar3[1] % 0x20;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c1d4,0x1be,DAT_0053c1d0,param_2,*puVar3,uVar2,
                 param_3,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x11400000,DAT_0053c1d8,DAT_0053c1d8,param_2,*puVar3,uVar2,param_3,param_3);
  }
  if (*(char *)(param_1 + 0x22) != '\0') {
    if (puVar3[2] == '\x01') {
      *(char *)(param_1 + uVar2 + 2) = (char)param_3;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c1d4,0x1c5,DAT_0053c1dc,uVar2,
                     *(undefined1 *)(param_1 + uVar2 + 2));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_0053c1e0,DAT_0053c1e0,uVar2,
                            *(undefined1 *)(param_1 + uVar2 + 2));
      }
    }
    else {
      if (puVar3[2] != '\x02') {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c1d4,0x1cb,DAT_0053c1ec);
        }
        iVar1 = FUN_0043d0ce();
        if ((-1 < iVar1 << 0x1f) && (iVar1 = FUN_0043d0ce(), -1 < iVar1 << 0x1d)) {
          return;
        }
        compress_log_output(0x10000000,DAT_0053c1f0,DAT_0053c1f0);
        return;
      }
      *(char *)(param_1 + uVar2 + 2) = (char)((uint)param_3 >> 8);
      *(char *)(param_1 + uVar2 + 3) = (char)param_3;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c1d4,0x1c9,DAT_0053c1e4,uVar2,
                     *(undefined1 *)(param_1 + uVar2 + 2),*(undefined1 *)(param_1 + uVar2 + 3));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_0053c1e8,DAT_0053c1e8,uVar2,
                            *(undefined1 *)(param_1 + uVar2 + 2),
                            *(undefined1 *)(param_1 + uVar2 + 3));
      }
    }
    *(undefined1 *)(param_1 + 0x23) = 1;
  }
  return;
}

