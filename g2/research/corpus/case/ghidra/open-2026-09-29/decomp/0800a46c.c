
void case_serial_write_byte(uint param_1)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    case_write_selected_mask_alt((int)(param_1 << 0x18) < 0);
    case_delay_10();
    case_write_selected_mask(1);
    case_delay_10();
    case_write_selected_mask(0);
    case_delay_10();
    if (bVar1 == 7) {
      case_write_selected_mask_alt(1);
      case_delay_10();
    }
    bVar1 = bVar1 + 1;
    param_1 = (param_1 & 0x7f) << 1;
  } while (bVar1 < 8);
  return;
}

