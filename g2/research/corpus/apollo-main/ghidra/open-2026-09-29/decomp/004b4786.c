
void FUN_004b4786(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_004b4d38 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_004b4d34 + param_1) = (char)(param_2 << 4);
  }
  return;
}

