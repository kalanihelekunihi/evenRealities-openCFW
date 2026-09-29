
void _anccNtfValueUpdate(short *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  char local_18;
  char local_17;
  char local_16;
  char local_15;
  int local_14;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (*(short *)(param_2 + 10) == *param_1) {
    pcVar1 = *(char **)(param_2 + 4);
    local_18 = *pcVar1;
    local_17 = pcVar1[1];
    local_16 = pcVar1[2];
    local_15 = pcVar1[3];
    local_14 = (uint)(byte)pcVar1[5] * 0x100 + (uint)(byte)pcVar1[4] +
               (uint)(byte)pcVar1[6] * 0x10000 + (uint)(byte)pcVar1[7] * 0x1000000;
    if (local_18 == '\x02') {
      _anccNotiRemoveCback(&local_18);
    }
    else {
      iVar2 = anccActionListPush(&local_18);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004bf220,DAT_004bf21c,DAT_004bf8d4,0x1ac,DAT_004bf8d0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004bf8d8);
        }
      }
      else {
        iVar2 = anccNoConnActive();
        if (iVar2 == 0) {
          fw_event_loop_push_delayed(DAT_004bf8dc,0xa2,200);
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf8d4,0x1b6,DAT_004bf8e0,local_14,local_18
                      );
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004bf8e4,DAT_004bf8e4,local_14,local_18);
        }
      }
    }
  }
  else if (*(short *)(param_2 + 10) == param_1[3]) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf8d4,0x1bc,DAT_004bf8e8,
                   *(undefined1 *)(DAT_004bf6c0 + 10),*(undefined2 *)(DAT_004bf6c0 + 0x14));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004bf8ec,DAT_004bf8ec,*(undefined1 *)(DAT_004bf6c0 + 10),
                          *(undefined2 *)(DAT_004bf6c0 + 0x14));
    }
    do {
      iVar2 = _anccAttrHandler(*(undefined4 *)(param_2 + 4),*(undefined2 *)(param_2 + 8));
    } while (iVar2 != 0);
  }
  return;
}

