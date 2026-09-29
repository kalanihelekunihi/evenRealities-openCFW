
void jbd4010_configure_gpio_pins(void)

{
  byte *pbVar1;
  
  pbVar1 = (byte *)FUN_0050938e(1);
  if (*pbVar1 < 3) {
    FUN_00480f0c(0x8f,*DAT_005938d0);
  }
  if (*pbVar1 < 4) {
    FUN_00480f0c(0x80,*DAT_005938d0);
  }
  FUN_00480f0c(0x8e,*DAT_005938d0);
  return;
}

