
void timeout_default_1000_if_zero(short *param_1)

{
  if ((param_1 != (short *)0x0) && (*param_1 == 0)) {
    *param_1 = 1000;
  }
  return;
}

