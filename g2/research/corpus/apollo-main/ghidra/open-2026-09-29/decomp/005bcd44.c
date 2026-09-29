
undefined4 am_devices_hongshi_QSPI_PartialReflash_async(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_14;
  int local_10;
  
  piVar1 = DAT_005bd304;
  if (*DAT_005bd304 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_24 = DAT_005bd30c;
      local_28 = 0x339;
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,DAT_005bd320);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005bd314,DAT_005bd314);
    }
    uVar3 = 0xffffffff;
  }
  else {
    FUN_00439c04(&local_28,PTR_DAT_005bd324,0x1c);
    local_14 = *DAT_005bd318;
    local_10 = *piVar1;
    am_devices_mspi_qspi_write_async(&local_28);
    uVar3 = 0;
  }
  return uVar3;
}

