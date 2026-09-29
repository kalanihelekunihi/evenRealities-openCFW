
undefined8 even_ai_layout_cache_changed(void)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  int *piVar4;
  
  pcVar1 = DAT_004e6558;
  if (*DAT_004e6558 == '\0') {
    uVar2 = 1;
  }
  else if (DAT_004e6558[1] == *(char *)(DAT_004e64a8 + 0x18)) {
    piVar4 = *(int **)(DAT_004e64a8 + 0x14);
    if (piVar4 == (int *)0x0) {
      uVar2 = 1;
    }
    else {
      if ((*piVar4 == 0) || (iVar3 = FUN_0043e2ea(*piVar4), iVar3 == 0)) {
        if (pcVar1[0xc] != '\0') {
          uVar2 = 1;
          goto LAB_004e5f1e;
        }
      }
      else {
        iVar3 = FUN_0043fdda(*piVar4);
        if ((pcVar1[0xc] != '\x01') || (*(int *)(pcVar1 + 4) != iVar3)) {
          uVar2 = 1;
          goto LAB_004e5f1e;
        }
      }
      if ((piVar4[1] == 0) || (iVar3 = FUN_0043e2ea(piVar4[1]), iVar3 == 0)) {
        if (pcVar1[0xd] != '\0') {
          uVar2 = 1;
          goto LAB_004e5f1e;
        }
      }
      else {
        iVar3 = FUN_0043fdda(piVar4[1]);
        if ((pcVar1[0xd] != '\x01') || (*(int *)(pcVar1 + 8) != iVar3)) {
          uVar2 = 1;
          goto LAB_004e5f1e;
        }
      }
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 1;
  }
LAB_004e5f1e:
  return CONCAT44(in_r3,uVar2);
}

