
undefined4 am_devices_jbd4010_QSPI_PartialReflash_async(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_28;
  undefined1 auStack_24 [20];
  undefined4 local_10;
  undefined4 local_c;
  
  uVar2 = 0;
  FUN_00439c04(auStack_24,DAT_005938e0,0x1c);
  local_10 = *DAT_00593300;
  local_c = *DAT_005932f8;
  iVar1 = am_devices_mspi_qspi_write_async(auStack_24);
  if (iVar1 == 0) {
    local_28 = 0;
    iVar1 = jbd4010_write_command(0x97,&local_28,0);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00593320,DAT_0059331c,DAT_005938e4,0x217,DAT_005938d4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005938dc,DAT_005938dc);
      }
      uVar2 = 1;
    }
    osDelay(2);
  }
  return uVar2;
}

