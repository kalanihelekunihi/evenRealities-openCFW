
void FUN_00442256(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_00442cd0 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_00442ccc + param_1) = (char)(param_2 << 4);
  }
  return;
}

