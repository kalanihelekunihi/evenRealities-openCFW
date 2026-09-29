
uint case_flash_status_masked(void)

{
  return *(uint *)(DAT_08003ecc + 0x20) & DAT_08003ed0;
}

