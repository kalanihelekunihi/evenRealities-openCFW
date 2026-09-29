
void FUN_0055e2a6(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_0055e988 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_0055e984 + param_1) = (char)(param_2 << 4);
  }
  return;
}

