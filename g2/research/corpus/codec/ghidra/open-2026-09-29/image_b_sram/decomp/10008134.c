
char gx_analog_get_ldo_dig_ctrl(void)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(iRam10008150 + 0x58) & 0xff;
  cVar1 = '\0';
  if ((uVar2 >> 2 & 1) != 0) {
    cVar1 = ((uVar2 >> 1 & 1) != 0) + '\x01';
  }
  return cVar1;
}

