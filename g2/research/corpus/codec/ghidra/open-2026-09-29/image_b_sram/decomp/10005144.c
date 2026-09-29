
/* WARNING: Restarted to delay deadcode elimination for space: register */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

void FUN_10005144(uint param_1,uint param_2)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = FUN_10005070();
  uVar4 = param_2;
  if (uVar2 + 1 == 0) {
    uVar4 = param_2 + 1;
  }
  lVar1 = CONCAT44(uVar4,uVar2 + 1) + (ulonglong)param_1;
  uVar4 = (uint)((ulonglong)lVar1 >> 0x20);
  if (uVar4 <= param_2) goto LAB_10005186;
  do {
    do {
      iVar3 = 0x32;
      do {
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      uVar2 = FUN_10005070(uVar2);
    } while (param_2 < uVar4);
LAB_10005186:
  } while ((uVar4 == param_2) && (uVar2 < (uint)lVar1));
  return;
}

