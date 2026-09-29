
uint FUN_0050c8cc(void)

{
  bool bVar1;
  int iVar2;
  int *piVar3;
  undefined4 *puVar4;
  char cVar5;
  int iVar6;
  uint uVar7;
  
  FUN_0050c3c0();
  iVar2 = DAT_0050c97c;
  if (*(int *)(DAT_0050c97c + 0xc0) != 0) {
    for (uVar7 = 0; puVar4 = DAT_0050c9b8, (int)uVar7 < *(int *)(iVar2 + 0xc0); uVar7 = uVar7 + 1) {
      osMutexAcquire(*DAT_0050c9b8,0xffffffff);
      piVar3 = DAT_0050c9a8;
      cVar5 = FUN_0050b19a(DAT_0050c9a8,uVar7 & 0xffff);
      osMutexRelease(*puVar4);
      if (cVar5 != '\0') {
        bVar1 = false;
        for (iVar6 = 0; iVar6 < 4; iVar6 = iVar6 + 1) {
          if ((*(char *)(iVar6 * 0x30 + iVar2 + 0x29) != '\0') &&
             (*(int *)(iVar2 + iVar6 * 0x30 + 0x1c) == *piVar3)) {
            bVar1 = true;
            break;
          }
        }
        if (!bVar1) {
          return uVar7;
        }
      }
    }
  }
  return 0xffffffff;
}

