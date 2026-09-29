
void FUN_004f11c0(void)

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
  
  piVar1 = DAT_004f1a20;
  if (*DAT_004f1a20 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_64 = DAT_004f1a24;
      local_68 = 0x2c8;
      FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,DAT_004f1a28);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f1a2c,DAT_004f1a2c);
    }
    FUN_004503d6(&local_68);
    local_68 = *piVar1;
    local_64 = DAT_004f1a30;
    FUN_004506ce(&local_68,0,0x20);
    local_38 = 200;
    local_48 = DAT_004f1a34;
    local_2c = 200;
    local_30 = 0;
    local_58 = DAT_004f1a38;
    *DAT_004f19f8 = 1;
    FUN_00450408(&local_68);
  }
  return;
}

