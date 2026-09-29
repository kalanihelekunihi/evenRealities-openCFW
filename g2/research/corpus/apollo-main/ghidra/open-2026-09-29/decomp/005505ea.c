
void FUN_005505ea(void)

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
    local_64 = DAT_00551000;
    local_68 = 0x30c;
    FUN_0043d574(3,DAT_00550958,DAT_00550954,DAT_00551004);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00551008,DAT_00551008);
  }
  FUN_004503d6(&local_68);
  local_68 = *(undefined4 *)(DAT_00550ff4 + 0x3c);
  uVar2 = FUN_0043fce0(*(undefined4 *)(DAT_00550ff4 + 0x3c));
  FUN_004506ce(&local_68,uVar2,*DAT_0055100c);
  local_38 = *DAT_00550ff0;
  local_64 = DAT_00551010;
  local_48 = DAT_00551014;
  local_58 = DAT_00551308;
  FUN_00450408(&local_68);
  return;
}

