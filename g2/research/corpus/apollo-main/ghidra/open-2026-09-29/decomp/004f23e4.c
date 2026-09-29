
void FUN_004f23e4(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int local_6c;
  undefined4 local_68;
  undefined4 local_5c;
  undefined4 local_4c;
  undefined4 local_3c;
  undefined4 local_34;
  undefined4 local_30;
  
  piVar1 = DAT_004f27f8;
  if (*DAT_004f27f8 != 0) {
    *DAT_004f2ba4 = 1;
    iVar3 = (((*DAT_004f2b94 - *DAT_004f2b98) + 0x1b) / 0x1c) * -0x1c;
    FUN_004503d6(&local_6c);
    local_6c = *piVar1;
    local_68 = DAT_004f2e98;
    FUN_004506ce(&local_6c,iVar3,iVar3 + -0x20);
    local_3c = 0x96;
    local_4c = DAT_004f2e9c;
    local_30 = 0xb4;
    local_34 = 0;
    *DAT_004f2cd8 = 1;
    local_5c = DAT_004f2ce8;
    FUN_00450408(&local_6c);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f2eac,0x4fc,DAT_004f2ea8,iVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f31b4,DAT_004f31b4,iVar3);
    }
  }
  return;
}

