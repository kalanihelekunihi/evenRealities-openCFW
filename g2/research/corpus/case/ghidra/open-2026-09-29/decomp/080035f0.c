
void case_configure_register_sequence(void)

{
  right_channel_transaction_guard(0x13,0x90);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x16,0);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x19,2);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x17,0x28);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x18,1);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x1a,0);
  case_wait_elapsed(2);
  right_channel_transaction_guard(0x1b,1);
  case_wait_elapsed(2);
  return;
}

