
int FUN_0044a43c(uint *param_1)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar2 = param_1;
  while (((uint)puVar2 & 3) != 0) {
    puVar1 = (uint *)((int)puVar2 + 1);
    uVar4 = *puVar2;
    puVar2 = puVar1;
    if ((char)uVar4 == '\0') goto LAB_0044a46e;
  }
  uVar4 = *puVar2;
  while( true ) {
    uVar4 = uVar4 + 0xfefefeff & ~uVar4;
    uVar3 = uVar4 & 0x80808080;
    if (uVar3 != 0) break;
    puVar2 = puVar2 + 1;
    uVar4 = *puVar2;
  }
  puVar1 = (uint *)((int)puVar2 +
                   ((uint)LZCOUNT((uVar4 & 0x80) << 0x18 | (uVar3 >> 8 & 0xff) << 0x10 |
                                  (uVar3 >> 0x10 & 0xff) << 8 | uVar3 >> 0x18) >> 3) + 1);
LAB_0044a46e:
  return (int)puVar1 - (int)((int)param_1 + 1);
}

