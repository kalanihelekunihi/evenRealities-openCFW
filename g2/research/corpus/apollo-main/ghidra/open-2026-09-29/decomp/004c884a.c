
uint FUN_004c884a(uint param_1,byte param_2)

{
  uint uVar1;
  byte bVar2;
  
  uVar1 = param_1;
  bVar2 = param_2;
  if ((param_1 & 0xff) == 0) {
    uVar1 = 0;
  }
  else {
    for (; bVar2 < 8; bVar2 = param_2 + bVar2) {
      uVar1 = uVar1 | (param_1 & 0xff) << (uint)(byte)(8 - bVar2);
    }
    uVar1 = uVar1 & 0xff;
  }
  return uVar1;
}

