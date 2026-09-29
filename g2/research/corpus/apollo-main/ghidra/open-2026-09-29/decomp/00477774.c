
void _bleConnParaConnectEvt(int param_1)

{
  char *pcVar1;
  int *piVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x141,DAT_00478274);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047827c,DAT_0047827c);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x142,DAT_00478280,
                 *(undefined2 *)(param_1 + 6));
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00478284,DAT_00478284,*(undefined2 *)(param_1 + 6));
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x143,DAT_00478288,
                 *(undefined1 *)(param_1 + 8));
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047828c,DAT_0047828c,*(undefined1 *)(param_1 + 8));
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x144,DAT_00478290,
                 *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                 *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc),
                 *(undefined1 *)(param_1 + 0xb),*(undefined1 *)(param_1 + 10));
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x11800000,DAT_00478294,DAT_00478294,*(undefined1 *)(param_1 + 0xf),
                        *(undefined1 *)(param_1 + 0xe),*(undefined1 *)(param_1 + 0xd),
                        *(undefined1 *)(param_1 + 0xc),*(undefined1 *)(param_1 + 0xb),
                        *(undefined1 *)(param_1 + 10));
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x145,DAT_00477ab4,
                 ((uint)*(ushort *)(param_1 + 0x10) * 0x4e2) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477ab8,DAT_00477ab8,
                        ((uint)*(ushort *)(param_1 + 0x10) * 0x4e2) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x146,DAT_00477a6c,
                 *(undefined2 *)(param_1 + 0x12));
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477a70,DAT_00477a70,*(undefined2 *)(param_1 + 0x12));
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x147,DAT_00477a74,
                 ((uint)*(ushort *)(param_1 + 0x14) * 10000) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477a78,DAT_00477a78,
                        ((uint)*(ushort *)(param_1 + 0x14) * 10000) / 1000);
  }
  piVar2 = DAT_00477ab0;
  *(undefined2 *)(*DAT_00477ab0 + 0x18) = *(undefined2 *)(param_1 + 0x10);
  *(undefined2 *)(*piVar2 + 0x1a) = *(undefined2 *)(param_1 + 0x12);
  *(undefined2 *)(*piVar2 + 0x1c) = *(undefined2 *)(param_1 + 0x14);
  pcVar1 = DAT_00477aa4;
  cVar3 = _isConnParamsSlow(*piVar2);
  *pcVar1 = cVar3;
  *DAT_00477aa0 = *pcVar1;
  *DAT_00478298 = 1;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar5 = DAT_004782a0;
    if (*pcVar1 == -0x5d) {
      uVar5 = DAT_0047829c;
    }
    FUN_0043d574(4,DAT_00477ad8,DAT_00477ad4,DAT_00478278,0x14e,DAT_004782a4,
                 *(undefined2 *)(param_1 + 0x10),uVar5);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    uVar5 = DAT_004782a0;
    if (*pcVar1 == -0x5d) {
      uVar5 = DAT_0047829c;
    }
    compress_log_output(0x10800000,DAT_004782a8,DAT_004782a8,*(undefined2 *)(param_1 + 0x10),uVar5);
  }
  uVar5 = DAT_004782ac;
  fw_event_loop_remove_delayed(DAT_004782ac);
  iVar4 = settings_get_terminal_mode();
  if (iVar4 == 0) {
    fw_event_loop_push_delayed(uVar5,0xa4,60000);
  }
  return;
}

