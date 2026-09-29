
int touch_sub_2f62(uint param_1,int param_2)

{
  return 1 << ((param_1 & 3) + param_2 + 1 & 0xff);
}

