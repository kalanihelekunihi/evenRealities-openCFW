
bool case_serial_ack_sample(void)

{
  int iVar1;
  
  case_write_selected_mask_alt(1);
  case_write_selected_mask(1);
  case_delay_10();
  iVar1 = case_select_mask();
  case_write_selected_mask(0);
  case_delay_10();
  return iVar1 != 0;
}

