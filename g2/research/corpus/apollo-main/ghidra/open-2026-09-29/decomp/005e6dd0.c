
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e6dd0(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  char cVar2;
  char cVar3;
  undefined4 uVar4;
  
  iVar1 = _DAT_005e7268;
  if (*(int *)(_DAT_005e7268 + 500) != 0) {
    uVar4 = FUN_005e4e06(param_2);
    cVar2 = FUN_005e4e0a(param_2);
    cVar3 = FUN_005e4e10(param_2,*(undefined1 *)(iVar1 + 0x278));
    if (*(char *)(iVar1 + 0x278) != cVar3) {
      *(char *)(iVar1 + 0x278) = cVar3;
      func_0x005ec190();
    }
    if (cVar2 != '\0') {
      FUN_0044ea04(*(undefined4 *)(iVar1 + 500),uVar4,1);
    }
  }
  return (ulonglong)param_4 << 0x20;
}

