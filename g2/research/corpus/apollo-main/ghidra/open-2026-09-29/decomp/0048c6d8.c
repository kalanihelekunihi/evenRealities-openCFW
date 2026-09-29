
void FUN_0048c6d8(byte param_1,int param_2,int param_3,int param_4,int *param_5,int *param_6)

{
  if ((param_4 < 2) && (param_1 - 3 < 2)) {
    param_1 = 2;
  }
  if (param_1 == 1) {
    *param_6 = 0;
    *param_5 = (param_2 + *param_5) - param_3;
    return;
  }
  if (param_1 != 0) {
    if (param_1 == 3) {
      *param_6 = (param_2 - param_3) / (param_4 + 1);
      *param_5 = *param_6 + *param_5;
      return;
    }
    if (param_1 < 3) {
      *param_6 = 0;
      *param_5 = (param_2 - param_3) / 2 + *param_5;
      return;
    }
    if (param_1 == 5) {
      if (param_4 < 2) {
        return;
      }
      *param_6 = (param_2 - param_3) / (param_4 + -1);
      return;
    }
    if (param_1 < 5) {
      *param_6 = (param_2 - param_3) / param_4 + *param_6;
      *param_5 = *param_6 / 2 + *param_5;
      return;
    }
  }
  *param_6 = 0;
  return;
}

