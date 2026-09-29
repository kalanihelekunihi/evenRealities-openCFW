
int FUN_0047a6b4(char param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  
  iVar1 = 0;
  uVar3 = 0xffffffff;
  iVar2 = DAT_0047ae64;
  for (bVar4 = 0; bVar4 < 10; bVar4 = bVar4 + 1) {
    if ((((*(char *)(iVar2 + 0x2f) != '\0') && (*(char *)(iVar2 + 0x30) != '\0')) &&
        (*(char *)(iVar2 + 0xc3) == param_1)) && (*(uint *)(iVar2 + 0xc4) < uVar3)) {
      uVar3 = *(uint *)(iVar2 + 0xc4);
      iVar1 = iVar2;
    }
    iVar2 = iVar2 + 200;
  }
  return iVar1;
}

