
undefined4 gx8002_app_gpio_event(void)

{
  int iVar1;
  
  iVar1 = DAT_10208e40;
  gx8002_printf(PTR_s__YW_APP__s__d___10208e48,PTR_s_gpio_callback_10208e44,0x7c);
  gx8002_power_lock(*(undefined4 *)(iVar1 + 8));
  *(undefined4 *)(iVar1 + 0xc) = 2000;
  return 0;
}

