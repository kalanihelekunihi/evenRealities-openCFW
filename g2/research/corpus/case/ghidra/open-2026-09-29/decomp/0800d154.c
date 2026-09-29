
void aging_indicator_apply(void)

{
  case_update_cached_byte(3,0xae);
  case_update_cached_byte(4,0xae);
  case_update_cached_byte(5,3);
  case_update_cached_byte(6,0x81);
  return;
}

