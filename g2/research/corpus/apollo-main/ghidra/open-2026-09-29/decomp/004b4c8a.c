
undefined4 HciVscUpdateNvdsParam(void)

{
  undefined1 *puVar1;
  undefined4 unaff_r7;
  
  puVar1 = DAT_004b4dc0;
  *DAT_004b4dc0 = 0xff;
  puVar1[1] = 0x7c;
  puVar1[2] = 1;
  puVar1[3] = 0xf;
  puVar1[4] = 0xb8;
  puVar1[5] = 0x19;
  HciVendorSpecificCmd(0xfff2,8);
  return unaff_r7;
}

