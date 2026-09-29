
int attcCcbByHandle(undefined2 param_1,uint param_2)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = DmConnIdByHandle(param_1);
  if (bVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = (uint)bVar1 * 0x84 + DAT_00531bac + (param_2 & 0xff) * 0x2c + -0x84;
  }
  return iVar2;
}

