
void case_toggle_lines_three(void)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    case_gpio_pa6_write(1);
    case_gpio_pa7_write(0);
    case_wait_elapsed(200);
    case_gpio_pa6_write(0);
    case_gpio_pa7_write(1);
    case_wait_elapsed(200);
    bVar1 = bVar1 + 1;
  } while (bVar1 < 3);
  case_gpio_pa6_write(0);
  case_gpio_pa7_write(0);
  return;
}

