
void glasses_charge_side_select(int param_1)

{
  byte bVar1;
  
  if (((*(char *)(DAT_0800389c + 0x11) == '\0') || (*(char *)(DAT_0800389c + 0x10) == '\0')) &&
     (param_1 == 0)) {
    if (*(char *)(DAT_0800389c + 0x11) != '\0') {
      return;
    }
    if (*(char *)(DAT_0800389c + 0x10) != '\0') {
      return;
    }
    bVar1 = *(byte *)(DAT_0800389c + 1);
  }
  else {
    bVar1 = *(byte *)(DAT_0800389c + 0x32);
    if (*(byte *)(DAT_0800389c + 0x4e) <= *(byte *)(DAT_0800389c + 0x32)) {
      bVar1 = *(byte *)(DAT_0800389c + 0x4e);
    }
  }
  if (bVar1 < 0x5a) {
    case_gpio_pa6_write(1);
    case_gpio_pa7_write(0);
    return;
  }
  case_gpio_pa7_write(1);
  case_gpio_pa6_write(0);
  return;
}

