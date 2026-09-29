
void case_pulse4_extended(void)

{
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_busy_delay(0x17);
  case_write_mask4_clear();
  case_busy_delay(0x15e);
  case_write_mask4_set();
  return;
}

