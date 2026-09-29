
void case_pulse8_extended(void)

{
  case_write_mask8_set();
  case_transition_word4_alt();
  case_write_mask8_set();
  case_busy_delay_alt(0x17);
  case_write_mask8_clear();
  case_busy_delay_alt(0x15e);
  case_write_mask8_set();
  return;
}

