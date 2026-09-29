
void left_indicator_sequence(void)

{
  case_update_cached_byte(5,3);
  case_update_cached_byte(6,0xc1);
  case_update_cached_byte(3,0xa6);
  osDelay(0x1e);
  case_update_cached_byte(7,3);
  return;
}

