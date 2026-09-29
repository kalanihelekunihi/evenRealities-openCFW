
int IMU_AIDStateUpdate(char param_1,char param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 uStack_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_12;
  
  FUN_0043c0e4(&uStack_20,0xf,0);
  if ((param_1 == '\x06') && (param_2 == '\x06')) {
    local_12 = 1;
    local_1f = 0;
    local_1e = 0;
    if (*DAT_004a537c == '\0') {
      *DAT_004a537c = '\x01';
      FUN_0047243a();
    }
  }
  else {
    local_12 = 1;
    local_1f = 1;
    local_1e = 0;
    if (*DAT_004a537c == '\x01') {
      *DAT_004a537c = '\0';
      FUN_0047243a();
    }
  }
  uVar1 = DAT_004a5380;
  iVar2 = FUN_005062c8(DAT_004a5380);
  if (iVar2 == 0) {
    iVar2 = FUN_0050637c(uVar1,0,&uStack_20);
    if (iVar2 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a5378,DAT_004a5374,DAT_004a5484,0x39e,DAT_004a5384,DAT_004a5484,0x39e)
        ;
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,DAT_004a5484,0x39e);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a5378,DAT_004a5374,DAT_004a5484,0x39c,DAT_004a5384,DAT_004a5484,0x39c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,DAT_004a5484,0x39c);
    }
  }
  return iVar2;
}

