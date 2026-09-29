
undefined4 hciCoreReadMaxDataLen(void)

{
  undefined4 unaff_r7;
  
  if (((int)((uint)*(byte *)(DAT_00569d28 + 0x88) << 0x1a) < 0) &&
     ((int)((uint)*DAT_00569d2c << 0x1a) < 0)) {
    HciLeReadMaxDataLen();
  }
  else {
    HciLeRandCmd();
  }
  return unaff_r7;
}

