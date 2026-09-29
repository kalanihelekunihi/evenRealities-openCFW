
char FUN_0048a750(byte param_1)

{
  char cVar1;
  
  if (param_1 - 0x30 < 10) {
    cVar1 = param_1 - 0x30;
  }
  else {
    if (0x60 < param_1) {
      param_1 = param_1 - 0x20;
    }
    if (param_1 - 0x41 < 6) {
      cVar1 = param_1 - 0x37;
    }
    else {
      cVar1 = '\0';
    }
  }
  return cVar1;
}

