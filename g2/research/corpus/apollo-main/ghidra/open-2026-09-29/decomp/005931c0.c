
longlong jbd4010_clear_display(void)

{
  undefined4 in_r3;
  uint uVar1;
  
  if (*DAT_005932fc != 0) {
    (*(code *)*DAT_005932fc)(0,0,0,0x280,0x1e0,in_r3);
  }
  uVar1 = 0x280;
  am_devices_jbd4010_QSPI_PartialReflash_async(0,0,0,0,0x280,0x1e0);
  return (ulonglong)uVar1 << 0x20;
}

