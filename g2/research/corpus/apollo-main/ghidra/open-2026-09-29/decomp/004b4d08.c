
undefined4 HciVscUpdateBDAddress(void)

{
  undefined4 unaff_r7;
  
  HciVendorSpecificCmd(0xfc43,6,DAT_004b4d98);
  return unaff_r7;
}

