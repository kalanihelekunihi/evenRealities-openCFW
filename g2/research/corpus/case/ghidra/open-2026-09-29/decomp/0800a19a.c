
void case_route_boolean_alt(int param_1)

{
  if (param_1 != 0) {
    case_pulse8_long();
    return;
  }
  case_pulse8_short();
  return;
}

