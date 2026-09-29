
void case_emit_bits_alt(uint param_1,int param_2)

{
  uint uVar1;
  
  if (param_2 == 1) {
    uVar1 = 6;
  }
  else {
    uVar1 = 7;
  }
  do {
    case_route_boolean_alt((param_1 >> (uVar1 & 0xff) & 1) != 0);
    uVar1 = uVar1 - 1;
  } while (-1 < (int)uVar1);
  return;
}

