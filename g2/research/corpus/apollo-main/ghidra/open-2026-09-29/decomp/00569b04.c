
undefined4 hciCoreReadResolvingListSize(void)

{
  undefined4 unaff_r7;
  
  if (((int)((uint)*(byte *)(DAT_00569d28 + 0x88) << 0x19) < 0) &&
     ((int)((uint)*DAT_00569d2c << 0x19) < 0)) {
    HciLeReadResolvingListSize();
  }
  else {
    *(undefined1 *)(DAT_00569d28 + 0x91) = 0;
    hciCoreReadMaxDataLen();
  }
  return unaff_r7;
}

