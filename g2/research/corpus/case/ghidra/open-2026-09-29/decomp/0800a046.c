
int case_start_validated(void)

{
  int iVar1;
  int in_r3;
  int local_8;
  
  local_8 = in_r3;
  iVar1 = case_query_low_byte(&local_8);
  if (iVar1 == 0) {
    if (local_8 == 0xa0) {
      iVar1 = case_verify_selector_bank();
      if ((-1 < iVar1) && ((iVar1 == 0 || (iVar1 = case_program_selector_bank(), -1 < iVar1)))) {
        return 0;
      }
    }
    else {
      iVar1 = -2;
    }
  }
  return iVar1;
}

