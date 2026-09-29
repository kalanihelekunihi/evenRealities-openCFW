
void right_indicator_sequence(void)

{
  case_update_cached_byte(5,3);
  case_update_cached_byte(6,0xc1);
  case_update_cached_byte(4,0xa6);
  osDelay(0x1e);
  case_update_cached_byte(7,5);
  return;
}

