
undefined4 callback_mgr_is_registered(int *param_1,int param_2)

{
  if ((param_1 != (int *)0x0) && (param_2 != 0)) {
    for (param_1 = (int *)*param_1; param_1 != (int *)0x0; param_1 = (int *)param_1[1]) {
      if (*param_1 == param_2) {
        return 1;
      }
    }
  }
  return 0;
}

