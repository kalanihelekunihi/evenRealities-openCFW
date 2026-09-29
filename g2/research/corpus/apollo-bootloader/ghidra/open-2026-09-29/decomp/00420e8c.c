
void FUN_00420e8c(void)

{
  int iVar1;
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined2 local_18;
  undefined1 local_14;
  undefined1 local_d;
  
  FUN_004156ac(local_1c,DAT_004210a4,0x18);
  local_14 = 0x10;
  local_18 = 0x6c;
  local_1c[0] = 8;
  local_d = 1;
  iVar1 = FUN_00420e08(local_1c);
  if (iVar1 == 0) {
    FUN_0041ff34(1);
    local_20[0] = 0x10;
    iVar1 = am_hal_mspi_control(*DAT_00421010,0x18,local_20);
    if (iVar1 != 0) {
      elog_output(2,DAT_00421034,DAT_00421030,DAT_004210ac,0x5b5,DAT_004210b0);
    }
  }
  else {
    elog_output(2,DAT_00421034,DAT_00421030,DAT_004210ac,0x5ae,DAT_004210a8);
  }
  return;
}

