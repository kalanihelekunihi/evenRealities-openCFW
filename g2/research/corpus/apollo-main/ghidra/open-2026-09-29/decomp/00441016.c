
int FUN_00441016(uint param_1)

{
  return (param_1 >> 8 & 0xff) * 0x100 + (param_1 & 0xff) + (param_1 >> 0x10 & 0xff) * 0x10000;
}

