
void FUN_004f18ac(void)

{
  int *piVar1;
  int iVar2;
  int local_68;
  undefined4 local_64;
  undefined4 local_60;
  int local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_48;
  undefined4 local_38;
  
  piVar1 = DAT_004f1a74;
  if (*DAT_004f1a74 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_64 = DAT_004f23d4;
      local_68 = 0x3aa;
      FUN_0043d574(2,DAT_004f23e0,DAT_004f23dc,DAT_004f23d8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f24c4,DAT_004f24c4);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_54 = *DAT_004f1a4c;
      local_58 = *DAT_004f1a48;
      local_5c = *DAT_004f1a44;
      local_60 = *DAT_004f1a3c;
      local_64 = DAT_004f24c8;
      local_68 = 0x3af;
      FUN_0043d574(3,DAT_004f23e0,DAT_004f23dc,DAT_004f23d8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_60 = *DAT_004f1a4c;
      local_64 = *DAT_004f1a48;
      local_68 = *DAT_004f1a44;
      compress_log_output(0xd000000,DAT_004f2520,DAT_004f2520,*DAT_004f1a3c);
    }
    FUN_0044d878(*piVar1);
    *DAT_004f1a78 = 0;
    *DAT_004f1a7c = 0;
    *DAT_004f1a80 = 0;
    *DAT_004f19f8 = 1;
    *DAT_004f1a60 = 1;
    FUN_004503d6(&local_68);
    local_68 = *piVar1;
    local_64 = DAT_004f23d0;
    FUN_004506ce(&local_68,1000,0);
    local_38 = 300;
    local_48 = DAT_004f1a34;
    local_58 = DAT_004f2524;
    FUN_00450408(&local_68);
  }
  return;
}

