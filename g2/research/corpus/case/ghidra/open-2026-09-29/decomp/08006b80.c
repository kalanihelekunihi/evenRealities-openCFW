
void case_gpio_pa6_write(int param_1)

{
  case_register_write_channel(0x50000000,0x40,param_1 != 0);
  return;
}

