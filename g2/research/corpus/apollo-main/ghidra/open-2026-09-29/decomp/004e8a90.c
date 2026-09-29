
void FUN_004e8a90(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_38;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004e9370,DAT_004e936c,DAT_004e9368,0x505,DAT_004e9364);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004e9374,DAT_004e9374);
  }
  FUN_004503d6(&local_68);
  if (*DAT_004e8bb8 == 1) {
    FUN_0043ded4(*DAT_004e9378,1);
    FUN_0043ded4(*DAT_004e937c,1);
    puVar1 = DAT_004e8db4;
    iVar2 = FUN_0043e2ea(*DAT_004e8db4);
    if (iVar2 == 1) {
      local_68 = *puVar1;
    }
    else {
      local_68 = *DAT_004e9380;
    }
  }
  else {
    local_68 = *DAT_004e9380;
  }
  FUN_004506ce(&local_68,0xff,0);
  local_38 = 0xfa;
  local_64 = DAT_004e9384;
  local_48 = DAT_004e9388;
  local_58 = DAT_004e938c;
  *DAT_004e9390 = 1;
  FUN_00450408(&local_68);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004e9370,DAT_004e936c,DAT_004e9368,0x52b,DAT_004e9394);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004e9398,DAT_004e9398);
  }
  return;
}

