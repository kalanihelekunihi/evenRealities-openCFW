
undefined4 gx8002_notification_poll(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = iRam102097f0;
  if (*(int *)(iRam102097f0 + 0x20) != 0) {
    iVar2 = func_0x10025930();
    if (0x3c < (uint)(iVar2 - *(int *)(iVar1 + 0x20))) {
      gx_gpio_set_level(2,1);
      *(undefined4 *)(iVar1 + 0x20) = 0;
    }
  }
  return 0;
}

