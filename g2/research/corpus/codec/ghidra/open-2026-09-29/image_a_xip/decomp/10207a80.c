
void gx8002_multiboot_switch(void)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = DAT_10207ab4;
  piVar1 = DAT_10207ab0;
  if (*DAT_10207ab0 == DAT_10207ab4) {
    gx8002_printf(PTR_s_boot_from_first_firmware_10207ab8);
    *piVar1 = 0;
  }
  else {
    gx8002_printf(PTR_s_boot_from_second_firmware_10207abc);
    *piVar1 = iVar2;
  }
  func_0x10025664(DAT_10207ab0,0x10);
  gx8002_reboot();
  return;
}

