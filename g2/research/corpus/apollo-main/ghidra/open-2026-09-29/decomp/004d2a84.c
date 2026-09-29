
char DmLlAddrType(char param_1)

{
  if (*(char *)(DAT_004d2ae8 + 0x16) != '\0') {
    if (param_1 == '\0') {
      param_1 = '\x02';
    }
    else if (param_1 == '\x01') {
      param_1 = '\x03';
    }
  }
  return param_1;
}

