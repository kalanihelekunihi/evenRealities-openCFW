
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __NVIC_SetPriority(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + _DAT_0057b6b4 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(_DAT_0057b6b0 + param_1) = (char)(param_2 << 4);
  }
  return;
}

