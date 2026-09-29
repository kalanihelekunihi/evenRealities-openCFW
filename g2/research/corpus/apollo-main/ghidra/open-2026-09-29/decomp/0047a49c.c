
undefined8 FUN_0047a49c(int param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = param_2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_4 = param_2 & 0xff;
    uVar3 = 0x2c5;
    param_3 = DAT_0047ae44;
    FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047ae48,0x2c5,DAT_0047ae44,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047ae4c,DAT_0047ae4c,param_2 & 0xff,uVar3,param_3,param_4);
  }
  *(undefined1 *)(param_1 + 0x30) = 1;
  *(undefined1 *)(param_1 + 0x2f) = 1;
  *(char *)(param_1 + 0x2e) = (char)param_2;
  piVar1 = DAT_0047ae50;
  *DAT_0047ae50 = *DAT_0047ae50 + 1;
  *(int *)(param_1 + 0xc4) = *piVar1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x2cc;
    param_3 = DAT_0047ae54;
    FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047ae48,0x2cc,DAT_0047ae54,param_2 & 0xff);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047ae58,DAT_0047ae58,param_2 & 0xff);
  }
  iVar2 = FUN_00479b74(param_1);
  FUN_0047b730(param_1);
  if (iVar2 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x2d3;
      param_3 = DAT_0047ae5c;
      FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047ae48);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0047ae60,DAT_0047ae60);
    }
  }
  return CONCAT44(param_3,uVar3);
}

