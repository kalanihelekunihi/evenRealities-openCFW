
undefined4 delay_us_status_check(int param_1,uint *param_2,uint param_3,uint param_4,char param_5)

{
  while( true ) {
    if (param_5 == '\0') {
      if ((*param_2 & param_3) != param_4) {
        return 0;
      }
    }
    else if ((*param_2 & param_3) == param_4) {
      return 0;
    }
    if (param_1 == 0) break;
    delay_us(1);
    param_1 = param_1 + -1;
  }
  return 4;
}

