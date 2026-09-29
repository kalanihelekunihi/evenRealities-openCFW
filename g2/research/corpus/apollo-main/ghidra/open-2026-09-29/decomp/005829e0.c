
void FUN_005829e0(undefined2 *param_1,uint param_2,int param_3,uint param_4)

{
  if ((param_1 != (undefined2 *)0x0) && (param_2 != 0)) {
    if ((param_3 == 0) || ((int)param_4 < 1)) {
      *param_1 = 0;
    }
    else {
      if (param_2 < param_4) {
        param_4 = param_2;
      }
      if (param_4 != 0) {
        FUN_00439be4(param_1 + 1,param_3,param_4);
      }
      *param_1 = (short)param_4;
    }
  }
  return;
}

