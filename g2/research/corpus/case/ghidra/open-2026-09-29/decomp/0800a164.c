
void case_route_parity(void)

{
  int iVar1;
  
  iVar1 = case_parity8();
  case_route_boolean(iVar1 == 1);
  return;
}

