
undefined4 even_ai_relayout_dialogs(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  int *piVar4;
  int iVar5;
  
  iVar2 = even_ai_layout_cache_changed();
  iVar1 = DAT_004e74fc;
  if (iVar2 != 0) {
    iVar2 = 0;
    iVar5 = 0;
    for (piVar4 = *(int **)(DAT_004e74fc + 0x10); piVar4 != (int *)0x0; piVar4 = (int *)piVar4[8]) {
      if ((*piVar4 != 0) && (iVar3 = FUN_0043e2ea(*piVar4), iVar3 != 0)) {
        FUN_0043f09a(*piVar4,0,iVar2);
        iVar3 = FUN_0043fdda(*piVar4);
        iVar2 = iVar3 + iVar2;
      }
      if ((piVar4[1] != 0) && (iVar3 = FUN_0043e2ea(piVar4[1]), iVar3 != 0)) {
        if ((*piVar4 != 0) && (iVar3 = FUN_0043e2ea(*piVar4), iVar3 != 0)) {
          iVar2 = iVar2 + 8;
        }
        FUN_0043f09a(piVar4[1],0,iVar2);
        iVar3 = FUN_0043fdda(piVar4[1]);
        iVar2 = iVar3 + iVar2;
      }
      iVar5 = iVar5 + 1;
      if (iVar5 < (int)(uint)*(byte *)(iVar1 + 0x18)) {
        iVar2 = iVar2 + 0x10;
      }
    }
    iVar5 = FUN_0043fdda(*(undefined4 *)(iVar1 + 8));
    iVar3 = FUN_0044e498(*(undefined4 *)(iVar1 + 8));
    iVar2 = iVar2 - iVar5;
    if (iVar2 < 1) {
      if (iVar3 != 0) {
        even_ai_scroll_to(*(undefined4 *)(iVar1 + 8),0,0);
      }
    }
    else if (iVar2 != iVar3) {
      even_ai_scroll_to(*(undefined4 *)(iVar1 + 8),iVar2,0);
    }
    even_ai_layout_cache_update();
  }
  return in_r3;
}

