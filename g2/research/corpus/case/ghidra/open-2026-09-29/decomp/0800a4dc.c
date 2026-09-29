
void case_serial_stop(void)

{
  case_write_selected_mask_alt(0);
  case_write_selected_mask(1);
  case_delay_10();
  case_write_selected_mask_alt(1);
  case_delay_10();
  return;
}

