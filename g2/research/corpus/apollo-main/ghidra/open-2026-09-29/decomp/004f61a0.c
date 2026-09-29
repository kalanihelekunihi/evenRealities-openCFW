
bool FUN_004f61a0(char param_1)

{
  bool bVar1;
  
  if (*DAT_004f6760 < 0x14) {
    bVar1 = false;
  }
  else if (param_1 == '\x01') {
    bVar1 = *DAT_004f6d20 + 1 < 5;
  }
  else if (param_1 == '\x02') {
    bVar1 = (int)(((uint)*DAT_004f6760 - *DAT_004f6d20) + -1) < 5;
  }
  else {
    bVar1 = false;
  }
  return bVar1;
}

