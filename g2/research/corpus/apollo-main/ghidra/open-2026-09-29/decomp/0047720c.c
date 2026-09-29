
void _connectParamReq_impl(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  ushort *puVar5;
  
  iVar3 = dmGetConnParamPtr();
  if (((iVar3 == 0) || (*(char *)(iVar3 + 4) == '\0')) || (3 < *(byte *)(iVar3 + 4))) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0047774c,DAT_00477748,DAT_00477a94,0xed,DAT_00477a90,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00477a98,DAT_00477a98,iVar3);
    }
    *DAT_00477a9c = '\0';
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xf2,DAT_00477aa8,param_1 & 0xff,
                 *DAT_00477aa4,*DAT_00477aa0,param_4);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_00477aac,DAT_00477aac,param_1 & 0xff,*DAT_00477aa4,
                        *DAT_00477aa0);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xf3,DAT_00477ab4,
                 ((uint)*(ushort *)(*DAT_00477ab0 + 0x18) * 0x4e2) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477ab8,DAT_00477ab8,
                        ((uint)*(ushort *)(*DAT_00477ab0 + 0x18) * 0x4e2) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xf4,DAT_00477a6c,
                 *(undefined2 *)(*DAT_00477ab0 + 0x1a));
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477a70,DAT_00477a70,*(undefined2 *)(*DAT_00477ab0 + 0x1a));
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xf5,DAT_00477a74,
                 ((uint)*(ushort *)(*DAT_00477ab0 + 0x1c) * 10000) / 1000);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00477a78,DAT_00477a78,
                        ((uint)*(ushort *)(*DAT_00477ab0 + 0x1c) * 10000) / 1000);
  }
  if ((param_1 & 0xff) == 0xa4) {
    cVar2 = _isConnParamsSlow(*DAT_00477ab0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xf8,DAT_00477abc,param_1 & 0xff,
                   *DAT_00477aa4,cVar2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_00477ac0,DAT_00477ac0,param_1 & 0xff,*DAT_00477aa4,cVar2);
    }
    if (cVar2 == -0x5c) {
      *DAT_00477aa4 = 0xa4;
      return;
    }
  }
  else if ((param_1 & 0xff) == 0xa3) {
    cVar2 = _isConnParamsFast(*DAT_00477ab0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0xff,DAT_00477ac4,param_1 & 0xff,
                   *DAT_00477aa4,cVar2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_00477ac8,DAT_00477ac8,param_1 & 0xff,*DAT_00477aa4,cVar2);
    }
    if (cVar2 == -0x5d) {
      *DAT_00477aa4 = 0xa3;
      *DAT_00477a9c = '\0';
      return;
    }
  }
  pcVar1 = DAT_00477a9c;
  if ((*DAT_00477a9c != '\0') && ((param_1 & 0xff) == (uint)*DAT_00477aa0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0x109,DAT_00477acc,param_1 & 0xff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00477ad0,DAT_00477ad0,param_1 & 0xff);
    }
    *pcVar1 = '\0';
    fw_event_loop_remove_delayed(0x47761d);
    fw_event_loop_push_delayed(0x47761d,param_1,10000);
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477a94,0x110,DAT_004780d8,param_1 & 0xff);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047810c,DAT_0047810c,param_1 & 0xff);
  }
  *pcVar1 = '\x01';
  puVar5 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar5 != (ushort *)0x0) {
    *(char *)(puVar5 + 1) = (char)param_1;
    *puVar5 = (ushort)*(byte *)(iVar3 + 4);
    WsfMsgSend(*DAT_0047826c,puVar5);
  }
  return;
}

