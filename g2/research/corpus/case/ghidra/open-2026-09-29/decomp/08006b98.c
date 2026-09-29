
void case_gpio_pa7_write(int param_1)

{
  case_register_write_channel(0x50000000,0x80,param_1 != 0);
  return;
}

