
void case_configure_record_and_stop(void)

{
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  FUN_080001e6(&local_18,0x14);
  local_18 = 0x18;
  local_14 = 0x11;
  local_10 = 0;
  FUN_08004d30(DAT_080028b0,&local_18);
  case_serial_stop();
  return;
}

