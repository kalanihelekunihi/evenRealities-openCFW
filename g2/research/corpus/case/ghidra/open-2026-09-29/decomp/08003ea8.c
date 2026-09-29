
uint case_flash_status_classify(void)

{
  uint uVar1;
  
  uVar1 = *(uint *)(DAT_08003ebc + 0x20) & 0xff;
  if ((uVar1 != 0xaa) && (uVar1 != 0xcc)) {
    uVar1 = 0xbb;
  }
  return uVar1;
}

