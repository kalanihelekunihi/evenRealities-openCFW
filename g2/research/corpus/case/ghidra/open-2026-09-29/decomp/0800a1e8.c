
void case_pulse4_long(void)

{
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_write_mask4_clear();
  case_busy_delay(0x5a);
  case_write_mask4_set();
  return;
}

