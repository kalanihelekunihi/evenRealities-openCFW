
void FUN_004f2318(void)

{
  int *piVar1;
  int iVar2;
  int local_68;
  undefined4 local_64;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_38;
  undefined4 local_30;
  undefined4 local_2c;
  
  piVar1 = DAT_004f27f8;
  if (*DAT_004f27f8 != 0) {
    *DAT_004f2ba4 = 1;
    FUN_004503d6(&local_68);
    local_68 = *piVar1;
    local_64 = DAT_004f2e98;
    FUN_004506ce(&local_68,0,0x20);
    local_38 = 0x96;
    local_48 = DAT_004f2e9c;
    local_2c = 0xb4;
    local_30 = 0;
    *DAT_004f2cd8 = 1;
    local_58 = DAT_004f2ce8;
    FUN_00450408(&local_68);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f23e0,DAT_004f23dc,DAT_004f2ea4,0x4e3,DAT_004f2ea0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f3068,DAT_004f3068);
    }
  }
  return;
}

