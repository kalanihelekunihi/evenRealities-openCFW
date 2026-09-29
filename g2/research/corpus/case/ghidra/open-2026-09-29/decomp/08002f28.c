
bool case_query_command_a2_is_one(void)

{
  uint in_r3;
  uint local_8;
  
  local_8 = in_r3 & 0xffffff00;
  case_run_guarded(0xa2,&local_8,1);
  return (local_8 & 0xff) == 1;
}

