
int attsCcbByHandle(undefined2 param_1,uint param_2)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = DmConnIdByHandle(param_1);
  if (bVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = DAT_00535448 + (uint)bVar1 * 0xc0 + (param_2 & 0xff) * 0x40 + -0xc0;
  }
  return iVar2;
}

