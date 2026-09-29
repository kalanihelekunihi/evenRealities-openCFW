
uint gx8002_memmove(uint param_1,uint param_2,int param_3)

{
  if (param_1 < param_2) {
    func_0x10025738();
  }
  else {
    param_3 = param_3 + -1;
    while (param_3 = param_3 + -1, param_3 != -2) {
      *(undefined1 *)(param_1 + param_3 + 1) = *(undefined1 *)(param_2 + param_3 + 1);
    }
  }
  return param_1;
}

