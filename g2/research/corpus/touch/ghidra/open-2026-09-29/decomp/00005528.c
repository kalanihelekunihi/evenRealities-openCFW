
uint touch_leaf_2228_mode_scale(int param_1,uint param_2,uint param_3)

{
  if ((param_2 & 3) == 2) {
    if ((param_1 == 1) || (param_1 == 10)) {
      param_3 = param_3 >> 2;
    }
    else {
      param_3 = param_3 >> 1;
    }
  }
  return param_3;
}

