
undefined4 gx8002_app_gpio_resume(undefined4 param_1)

{
  gx8002_printf(PTR_DAT_10208e18,param_1);
  gx8002_padmux_set(6,1);
  gx_gpio_set_direction(6,0);
  gx8002_gpio_enable_trigger(6,1,PTR_gx8002_app_gpio_event_10208e1c,0);
  return 0;
}

