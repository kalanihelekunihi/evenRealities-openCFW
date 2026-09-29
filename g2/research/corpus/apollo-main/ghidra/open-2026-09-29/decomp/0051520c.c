
undefined4 FUN_0051520c(int param_1)

{
  byte bVar1;
  char cVar2;
  int *piVar3;
  int iVar4;
  undefined1 *puVar5;
  bool bVar6;
  undefined1 auStack_58 [36];
  undefined1 auStack_34 [40];
  
  piVar3 = DAT_00515300;
  bVar1 = *(byte *)(param_1 + 0xd5);
  if (bVar1 == 1) {
LAB_0051522e:
    iVar4 = *DAT_00515300;
    if ((*(byte *)(param_1 + 0xd4) & 1) != 0) {
      bVar6 = *(char *)(iVar4 + 0x1bc) != '\x01';
      cVar2 = '\x01';
      if (bVar6) {
        cVar2 = *(char *)(iVar4 + 0x1bd);
      }
      if (bVar6 && cVar2 != '\x01') {
        param_1 = param_1 + 0x34;
LAB_005152d6:
        FUN_005226e8(param_1);
        return 0;
      }
      FUN_00561830(auStack_34,iVar4 + 0xec);
      iVar4 = FUN_00561b38(auStack_34);
      if (iVar4 != 0) {
LAB_005152ae:
        FUN_0051778c(0);
        FUN_00517796(0);
        FUN_0051565c(0x40000);
        return 0x40000;
      }
      FUN_00561830(auStack_58,param_1 + 0x34);
      puVar5 = auStack_34;
      goto LAB_005152ec;
    }
    if (-1 < (int)((uint)*(byte *)(iVar4 + 0x90) << 0x1f)) {
      param_1 = param_1 + 0x34;
      goto LAB_005152d6;
    }
    iVar4 = 0x34;
  }
  else {
    if (bVar1 == 0) {
      return 0;
    }
    if (bVar1 == 3) goto LAB_0051522e;
    if (2 < bVar1) {
      return 0;
    }
    iVar4 = *DAT_00515300;
    if ((*(byte *)(param_1 + 0xd4) & 1) != 0) {
      bVar6 = *(char *)(iVar4 + 0x1bc) != '\x01';
      cVar2 = '\x01';
      if (bVar6) {
        cVar2 = *(char *)(iVar4 + 0x1bd);
      }
      if (!bVar6 || cVar2 == '\x01') {
        FUN_00561830(auStack_34,iVar4 + 0xec);
        iVar4 = FUN_00561b38(auStack_34);
        if (iVar4 != 0) goto LAB_005152ae;
        FUN_00561830(auStack_58,param_1 + 8);
        puVar5 = auStack_34;
        goto LAB_005152ec;
      }
LAB_005152d2:
      param_1 = param_1 + 8;
      goto LAB_005152d6;
    }
    if (-1 < (int)((uint)*(byte *)(iVar4 + 0x90) << 0x1f)) goto LAB_005152d2;
    iVar4 = 8;
  }
  FUN_00561830(auStack_58,param_1 + iVar4);
  puVar5 = (undefined1 *)(*piVar3 + 200);
LAB_005152ec:
  FUN_005619f2(auStack_58,puVar5);
  FUN_005226e8(auStack_58);
  return 0;
}

