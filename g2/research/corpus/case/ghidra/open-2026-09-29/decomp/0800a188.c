
void case_route_boolean(int param_1)

{
  if (param_1 != 0) {
    case_pulse4_long();
    return;
  }
  case_pulse4_short();
  return;
}

