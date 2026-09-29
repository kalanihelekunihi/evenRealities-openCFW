
int FUN_0048eb90(void)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 in_r3;
  int iVar10;
  int iVar11;
  uint uVar12;
  int local_68;
  undefined4 local_64 [16];
  undefined4 uStack_24;
  
  uStack_24 = in_r3;
  if (*DAT_0048ed88 == '\0') {
    FUN_0048eac8();
  }
  uVar4 = FUN_0047dce4();
  pcVar2 = DAT_0048ed98;
  if (*DAT_0048ed98 == '\0') {
    *DAT_0048ed98 = '\x01';
    *DAT_0048ed94 = 0;
    pcVar3 = DAT_0048ed9c;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar4 & 1) == 1);
    }
    if (*DAT_0048ed9c == '\0') {
      iVar6 = FUN_0047dfec();
      if (iVar6 != 0) {
        *DAT_0048eda4 = *DAT_0048eda4 + 1;
        *pcVar2 = '\0';
        return iVar6;
      }
      *pcVar3 = '\x01';
    }
    iVar5 = 0;
    uVar4 = FUN_0047dce4();
    iVar6 = DAT_0048ed78;
    local_68 = *(int *)(DAT_0048ed78 + 0x14);
    *(undefined4 *)(DAT_0048ed78 + 0x14) = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar4 & 1) == 1);
    }
    if (local_68 != 0) {
      FUN_0048ea66(DAT_0048eda0,1,&local_68);
    }
    do {
      piVar7 = (int *)FUN_0047dce4();
      iVar10 = *(int *)(iVar6 + 0x10);
      iVar11 = *(int *)(iVar6 + 8);
      for (uVar4 = 0;
          (uVar4 + iVar10 != iVar11 && (iVar8 = FUN_0048e8f0(uVar4 + iVar10), iVar8 + uVar4 < 0x41))
          ; uVar4 = iVar8 + uVar4) {
      }
      for (uVar12 = 0; uVar12 < uVar4; uVar12 = uVar12 + 4) {
        uVar9 = FUN_0048e8e2(uVar12 + iVar10);
        *(undefined4 *)((int)local_64 + uVar12) = uVar9;
      }
      *(uint *)(iVar6 + 0x10) = uVar4 + iVar10;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(((uint)piVar7 & 1) == 1);
      }
      if (uVar4 == 0) goto LAB_0048ec8e;
      iVar5 = FUN_0047e178(local_64,uVar4);
      piVar7 = DAT_0048eda4;
    } while (iVar5 == 0);
    *DAT_0048eda4 = *DAT_0048eda4 + 1;
LAB_0048ec8e:
    FUN_0047e220(piVar7);
    *pcVar2 = '\0';
  }
  else {
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar4 & 1) == 1);
    }
    iVar5 = -0x10;
  }
  return iVar5;
}

