
void FUN_004e7a74(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_38;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_64 = DAT_004e8448;
    local_68 = 0x1d8;
    FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e844c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004e8450,DAT_004e8450);
  }
  FUN_004503d6(&local_68);
  local_68 = *DAT_004e8454;
  uVar2 = FUN_0043fce0(*DAT_004e8454);
  FUN_004506ce(&local_68,uVar2,*DAT_004e8458);
  local_38 = *DAT_004e842c;
  local_64 = DAT_004e845c;
  local_48 = DAT_004e8460;
  local_58 = DAT_004e8464;
  FUN_00450408(&local_68);
  return;
}

