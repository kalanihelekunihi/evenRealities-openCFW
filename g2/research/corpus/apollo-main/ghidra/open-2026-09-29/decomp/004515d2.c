
uint FUN_004515d2(uint param_1)

{
  if ((int)param_1 < 0) {
    if ((int)param_1 < DAT_004515f8) {
      param_1 = DAT_004515fc;
    }
    param_1 = 0xfffffff - param_1;
  }
  else if (0xffffffe < (int)param_1) {
    param_1 = 0xfffffff;
  }
  return param_1 | 0x20000000;
}

