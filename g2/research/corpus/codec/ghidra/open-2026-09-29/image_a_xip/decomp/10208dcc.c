
undefined4 gx8002_app_gpio_suspend(undefined4 param_1)

{
  gx8002_printf(uRam10208de8,param_1);
  gx8002_gpio_disable_trigger(6);
  gx8002_padmux_set(6,0);
  return 0;
}

