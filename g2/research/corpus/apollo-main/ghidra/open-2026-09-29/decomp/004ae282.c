
uint als_function_30(uint param_1,uint param_2,uint param_3)

{
  if (param_2 < param_1) {
    if (param_2 < 100 - param_3) {
      if (param_3 + param_2 <= param_1) {
        param_1 = param_3 + param_2;
      }
    }
    else if (100 < param_1) {
      param_1 = 100;
    }
  }
  else if (((param_1 < param_2) && (param_3 <= param_2)) && (param_1 <= param_2 - param_3)) {
    param_1 = param_2 - param_3;
  }
  return param_1;
}

