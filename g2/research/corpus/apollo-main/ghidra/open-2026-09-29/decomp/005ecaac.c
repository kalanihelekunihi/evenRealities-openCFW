
int FUN_005ecaac(void)

{
  short sVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar2 = td_active_session();
  if (iVar2 == 0) {
    iVar2 = -1;
  }
  else {
    uVar3 = FUN_005eca48();
    for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1) {
      if (*(int *)(uVar4 * 0x90 + iVar2 + 0x9c) == *(int *)(iVar2 + 4)) {
        return (int)(short)uVar4;
      }
    }
    iVar2 = td_has_active_session();
    if (iVar2 == 0) {
      sVar1 = -2;
    }
    else {
      sVar1 = -1;
    }
    iVar2 = (int)sVar1;
  }
  return iVar2;
}

