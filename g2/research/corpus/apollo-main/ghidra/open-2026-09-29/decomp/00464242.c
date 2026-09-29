
void FUN_00464242(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_50;
  undefined4 local_40;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_6c = DAT_00464324;
    local_70 = 0x1ef;
    FUN_0043d574(4,DAT_004642cc,DAT_004642c8,DAT_00464328);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0046432c);
  }
  FUN_004503d6(&local_70);
  local_70 = param_1;
  FUN_004506ce(&local_70,0xff,0);
  local_6c = DAT_00464318;
  local_50 = DAT_0046431c;
  local_40 = param_2;
  FUN_00450408(&local_70);
  return;
}

