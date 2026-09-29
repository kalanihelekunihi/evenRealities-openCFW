
undefined4 case_starts_with_de(char *param_1)

{
  if (((*param_1 == 'd') || (*param_1 == 'D')) && ((param_1[1] == 'e' || (param_1[1] == 'E')))) {
    return 1;
  }
  return 0;
}

