
undefined4 FUN_0046ca14(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = *DAT_0046cabc + *DAT_0046cab8;
  uVar2 = *DAT_0046cac0 + *DAT_0046cab4;
  if (0x40 < uVar1) {
    uVar1 = 0x40;
  }
  if ((int)(uVar1 << 0x1f) < 0) {
    uVar1 = uVar1 - 1;
  }
  if (0xc0 < uVar2) {
    uVar2 = 0xc0;
  }
  if ((int)(uVar2 << 0x1f) < 0) {
    uVar2 = uVar2 - 1;
  }
  buffer_sync_to_fb(*DAT_0046cac8,DAT_0046cac4,0x280,0x1e0,0x240,0x120,uVar1,uVar2);
  return 0;
}

