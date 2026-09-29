
void FUN_0053a430(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_0053a65c + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_0053a658 + param_1) = (char)(param_2 << 4);
  }
  return;
}

