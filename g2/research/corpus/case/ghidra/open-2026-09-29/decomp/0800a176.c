
void case_route_parity_alt(void)

{
  int iVar1;
  
  iVar1 = case_parity8_alt();
  case_route_boolean_alt(iVar1 == 1);
  return;
}

