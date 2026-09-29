
undefined4 APP_MasterRingMacIsSet(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  char local_14;
  char local_13;
  char local_12;
  char local_11;
  char local_10;
  char local_f;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  iVar1 = FUN_00466010();
  FUN_00439be4(&local_14,iVar1 + 0xc,6);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3534,0x5fb,DAT_004a3530,local_f,local_10,
                 local_11);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_004a304c;
  }
  compress_log_output(0xcc00000,DAT_004a3538,DAT_004a3538,local_f,local_10,local_11);
LAB_004a304c:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3534,0x5fc,DAT_004a353c,local_12,local_13,
                 local_14);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xcc00000,DAT_004a3540,DAT_004a3540,local_12,local_13,local_14);
  }
  if (((((local_f == -1) && (local_10 == -1)) && (local_11 == -1)) &&
      ((local_12 == -1 && (local_13 == -1)))) && (local_14 == -1)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004a315c,DAT_004a3158,DAT_004a3534,0x601,DAT_004a3544);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__ble_master__Ring__RingMacIsSet__004a3548,
                          PTR_s__ble_master__Ring__RingMacIsSet__004a3548);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

