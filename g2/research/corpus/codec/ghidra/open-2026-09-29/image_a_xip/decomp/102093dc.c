
void gx8002_notification_stamp(void)

{
  undefined4 uVar1;
  
  gx_gpio_set_level(2,0);
  uVar1 = func_0x10025930();
  *(undefined4 *)(iRam102093f0 + 0x20) = uVar1;
  return;
}

