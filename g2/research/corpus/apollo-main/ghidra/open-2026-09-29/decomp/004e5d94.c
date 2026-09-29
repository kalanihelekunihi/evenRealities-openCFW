
undefined8 even_ai_dialog_height_exceeds_window(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 in_r3;
  int *piVar5;
  int iVar6;
  
  iVar1 = DAT_004e64a8;
  if ((*(int *)(DAT_004e64a8 + 8) == 0) ||
     (iVar2 = FUN_0043e2ea(*(undefined4 *)(DAT_004e64a8 + 8)), iVar2 == 0)) {
    uVar3 = 0;
  }
  else {
    iVar2 = 0;
    iVar6 = 0;
    piVar5 = *(int **)(iVar1 + 0x10);
    do {
      if (piVar5 == (int *)0x0) {
        uVar3 = 0;
        goto LAB_004e5e10;
      }
      if ((*piVar5 != 0) && (iVar4 = FUN_0043e2ea(*piVar5), iVar4 != 0)) {
        iVar4 = FUN_0043fdda(*piVar5);
        iVar2 = iVar4 + iVar2;
      }
      if ((piVar5[1] != 0) && (iVar4 = FUN_0043e2ea(piVar5[1]), iVar4 != 0)) {
        if ((*piVar5 != 0) && (iVar4 = FUN_0043e2ea(*piVar5), iVar4 != 0)) {
          iVar2 = iVar2 + 8;
        }
        iVar4 = FUN_0043fdda(piVar5[1]);
        iVar2 = iVar4 + iVar2;
      }
      iVar6 = iVar6 + 1;
      if (iVar6 < (int)(uint)*(byte *)(iVar1 + 0x18)) {
        iVar2 = iVar2 + 0x10;
      }
      piVar5 = (int *)piVar5[8];
    } while (iVar2 < 0xc9);
    uVar3 = 1;
  }
LAB_004e5e10:
  return CONCAT44(in_r3,uVar3);
}

