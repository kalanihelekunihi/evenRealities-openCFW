
void FUN_004f5fd0(char param_1)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  char local_1c [4];
  undefined4 local_18;
  undefined1 local_14;
  
  puVar1 = DAT_004f6760;
  if (*DAT_004f6760 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f6314,DAT_004f6310,DAT_004f69dc,0x452,DAT_004f69d8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f69e0,DAT_004f69e0);
    }
  }
  else {
    quicklist_lock_storage();
    *(char *)((int)puVar1 + 0x2e4d) = param_1;
    quicklist_unlock_storage();
    FUN_0043c0e4(local_1c,0xc,0);
    local_14 = 0;
    local_1c[0] = param_1;
    if (param_1 == '\x01') {
      local_18 = *(undefined4 *)(puVar1 + 0x8a);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f69dc,0x464,DAT_004f69e4,local_18);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004f69e8,DAT_004f69e8,local_18);
      }
    }
    else {
      if (param_1 != '\x02') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004f6314,DAT_004f6310,DAT_004f69dc,0x46b,DAT_004f69fc,param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return;
        }
        compress_log_output(0x4400000,DAT_004f6d1c,DAT_004f6d1c,param_1);
        return;
      }
      local_18 = *(undefined4 *)(puVar1 + (*puVar1 - 1) * 0x94 + 0x8a);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f69dc,0x469,DAT_004f69f4,local_18);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004f69f8,DAT_004f69f8,local_18);
      }
    }
    iVar2 = APP_PbNotifyEncodeQuicklistEvent(0,local_1c);
    if (iVar2 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004f6314,DAT_004f6310,DAT_004f69dc,0x472,DAT_004f69ec,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004f69f0,DAT_004f69f0,iVar2);
      }
    }
  }
  return;
}

