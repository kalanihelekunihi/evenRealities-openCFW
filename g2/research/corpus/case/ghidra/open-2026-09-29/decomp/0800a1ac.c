
void case_pulse4_short(void)

{
  case_write_mask4_set();
  case_transition_word4();
  case_write_mask4_set();
  case_write_mask4_clear();
  case_busy_delay(0x17);
  case_write_mask4_set();
  return;
}

