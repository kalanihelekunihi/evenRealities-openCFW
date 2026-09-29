
void FUN_1000aad0(void)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = DAT_1000ab04;
  piVar1 = DAT_1000ab00;
  if (*DAT_1000ab00 == DAT_1000ab04) {
    FUN_10009934(PTR_s_boot_from_first_firmware_1000ab0c);
    *piVar1 = 0;
  }
  else {
    FUN_10009934(PTR_s_boot_from_second_firmware_1000ab08);
    *piVar1 = iVar2;
  }
  gx8002_dcache_clean_range(DAT_1000ab00,0x10);
  FUN_10008868();
  return;
}

