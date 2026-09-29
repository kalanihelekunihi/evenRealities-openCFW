
int Round_None(undefined4 param_1,int param_2,int param_3)

{
  if (param_2 < 0) {
    param_3 = param_2 - param_3;
    if (0 < param_3) {
      param_3 = 0;
    }
  }
  else {
    param_3 = param_3 + param_2;
    if (param_3 < 0) {
      param_3 = 0;
    }
  }
  return param_3;
}

