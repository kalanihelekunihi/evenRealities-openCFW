
int * buffer_skip_whitespace(int *param_1)

{
  if ((param_1 == (int *)0x0) || (*param_1 == 0)) {
    param_1 = (int *)0x0;
  }
  else {
    while ((param_1 != (int *)0x0 &&
           (((uint)param_1[2] < (uint)param_1[1] && (*(byte *)(*param_1 + param_1[2]) < 0x21))))) {
      param_1[2] = param_1[2] + 1;
    }
    if (param_1[2] == param_1[1]) {
      param_1[2] = param_1[2] + -1;
    }
  }
  return param_1;
}

