
void FUN_0041b64c(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_0041b824 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_0041b820 + param_1) = (char)(param_2 << 4);
  }
  return;
}

