
uint FUN_004cff18(int param_1,uint param_2)

{
  if ((param_2 & param_2 - 1) != 0) {
    FUN_004d09b4(DAT_004d0804,DAT_004d06ac,0x1e5);
  }
  return (param_2 + param_1) - 1 & ~(param_2 - 1);
}

