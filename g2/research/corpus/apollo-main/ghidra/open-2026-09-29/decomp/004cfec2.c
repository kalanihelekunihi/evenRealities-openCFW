
undefined8 FUN_004cfec2(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  if ((param_2 & param_2 - 1) != 0) {
    FUN_004d09b4(DAT_004d0804,DAT_004d06ac,0x1d7);
  }
  return CONCAT44(param_4,(param_2 + param_1) - 1 & ~(param_2 - 1));
}

