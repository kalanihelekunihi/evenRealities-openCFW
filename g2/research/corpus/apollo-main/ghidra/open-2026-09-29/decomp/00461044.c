
void FUN_00461044(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  char cStack_1c;
  undefined1 uStack_1b;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004615cc,0x243,DAT_004615c8);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004615d0,DAT_004615d0);
  }
  piVar1 = DAT_004615d4;
  if ((*DAT_004615d4 != 0) && (iVar2 = FUN_0043fce0(*DAT_004615d4), iVar2 != 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004611c0,DAT_004611bc,DAT_004615cc,0x249,DAT_004615d8,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004615dc,DAT_004615dc,iVar2);
    }
    FUN_0043f142(*piVar1,0);
  }
  *DAT_004615b0 = 0;
  iVar2 = FUN_004602b6();
  if (iVar2 == 0) {
    FUN_0043c0e4(&cStack_1c,10,0);
    FUN_004602ca(&cStack_1c,5);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004615cc,0x252,DAT_004615b4,cStack_1c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004615b8,DAT_004615b8,cStack_1c);
    }
    if (cStack_1c == '\n') {
      FUN_00461620(2);
    }
    else if (cStack_1c == 'D') {
      FUN_00461620(1);
    }
    else if (cStack_1c == 'E') {
      FUN_00461620(0);
    }
    else if (cStack_1c == 'F') {
      FUN_00462594(uStack_1b);
    }
    else if ((cStack_1c == 'H') && (iVar2 = FUN_0045a568(), iVar2 == 1)) {
      FUN_00464c36(3,0,0,0);
    }
  }
  return;
}

