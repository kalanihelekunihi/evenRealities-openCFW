
undefined4 gx8002_flash_otp_get_current_region(uint *param_1)

{
  *param_1 = *(uint *)(*(int *)(*(int *)(DAT_10023b74 + 0xc) + 0x14) + 0x10) & 7;
  return 0;
}

