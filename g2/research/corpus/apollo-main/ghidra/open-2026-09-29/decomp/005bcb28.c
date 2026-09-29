
longlong driver_a6ng_clear_framebuffer(void)

{
  undefined4 in_r3;
  uint uVar1;
  
  if (*DAT_005bd2fc != 0) {
    (*(code *)*DAT_005bd2fc)(0,0,0,0x280,0x1e0,in_r3);
  }
  uVar1 = 0x280;
  am_devices_hongshi_QSPI_PartialReflash_async(0,0,0,0,0x280,0x1e0);
  return (ulonglong)uVar1 << 0x20;
}

