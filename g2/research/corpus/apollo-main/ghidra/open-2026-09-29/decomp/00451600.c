
uint FUN_00451600(uint param_1,int param_2)

{
  if (((param_1 & 0x60000000) == 0x20000000) && ((int)(param_1 & 0x9fffffff) < 0x1fffffff)) {
    if ((int)(param_1 & 0x9fffffff) < 0x10000000) {
      param_1 = param_1 & 0x9fffffff;
    }
    else {
      param_1 = 0xfffffff - (param_1 & 0x9fffffff);
    }
    param_1 = (int)(param_2 * param_1) / 100;
  }
  return param_1;
}

