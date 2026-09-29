
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0057e898(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  char acStack_148 [8];
  undefined1 auStack_140 [256];
  undefined1 auStack_40 [52];
  
  uVar1 = _DAT_0057f3c0;
  if (*_DAT_0057f270 == 1) {
    iVar2 = FUN_004cfc66(_DAT_0057f3c0,auStack_40,_DAT_0057f3c4);
    if (-1 < iVar2) {
      while (iVar2 = FUN_004cfd02(uVar1,auStack_40,acStack_148), -1 < iVar2) {
        if (iVar2 == 0) {
          FUN_004cfcf8(uVar1,auStack_40);
          return 0;
        }
        iVar2 = FUN_0046cacc(auStack_140,0x57eb84);
        if ((iVar2 != 0) && (iVar2 = FUN_0046cacc(auStack_140,0x57eb88), iVar2 != 0)) {
          if (acStack_148[0] == '\x02') {
            uVar3 = 0x57eb8c;
          }
          else {
            uVar3 = 0x57eb90;
          }
          FUN_004733ee(_DAT_0057f52c,auStack_140,uVar3);
        }
      }
      FUN_004cfcf8(uVar1,auStack_40);
    }
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}

