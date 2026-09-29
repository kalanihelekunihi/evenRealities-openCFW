
byte FUN_00452f8c(char *param_1)

{
  byte bVar1;
  
  if (param_1 == (char *)0x0) {
    bVar1 = 0;
  }
  else if ((*param_1 == '\x01') || (*param_1 == '\x03')) {
    bVar1 = param_1[0xa8] & 0xf;
  }
  else {
    bVar1 = 0;
  }
  return bVar1;
}

