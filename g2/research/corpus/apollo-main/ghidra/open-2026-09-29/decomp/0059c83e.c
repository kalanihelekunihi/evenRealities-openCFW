
void NVIC_SetPriority(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_0059d160 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_0059d15c + param_1) = (char)(param_2 << 4);
  }
  return;
}

