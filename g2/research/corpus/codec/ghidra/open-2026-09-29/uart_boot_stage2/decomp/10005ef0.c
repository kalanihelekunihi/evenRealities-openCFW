
undefined4
FUN_10005ef0(int param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5,int param_6)

{
  int iVar1;
  undefined1 *puVar2;
  undefined *puVar3;
  undefined *puVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  undefined4 *puVar10;
  int iVar11;
  undefined4 *puVar12;
  int iVar13;
  undefined1 *puVar14;
  
  puVar4 = PTR_s__s____s_10006010;
  puVar3 = PTR_s_Unknown_command___s____try__help_1000600c;
  puVar14 = &stack0xffffffd4;
  if (param_5 != 1) {
    if (param_5 < 2) {
      uVar6 = 0;
    }
    else {
      puVar10 = (undefined4 *)(param_6 + 4);
      iVar11 = 1;
      do {
        while (puVar5 = (undefined4 *)FUN_10005e74(*puVar10,param_1,param_2),
              puVar5 != (undefined4 *)0x0) {
          iVar11 = iVar11 + 1;
          FUN_100061a4(puVar4,*puVar5,puVar5[4]);
          puVar10 = puVar10 + 1;
          if (param_5 == iVar11) goto LAB_10005f4a;
        }
        iVar11 = iVar11 + 1;
        FUN_100061a4(puVar3,*puVar10);
        puVar10 = puVar10 + 1;
      } while (param_5 != iVar11);
LAB_10005f4a:
      uVar6 = 1;
    }
    return uVar6;
  }
  iVar11 = param_2 + -1;
  puVar2 = &stack0xffffffd4;
  for (uVar8 = param_2 * 4 + 4; 0x1000 < uVar8; uVar8 = uVar8 - 0x1000) {
    puVar14 = puVar2 + -0x1000;
    *(undefined1 **)(puVar2 + -0x1000) = puVar2 + -0x1000;
    puVar2 = puVar2 + -0x1000;
  }
  iVar1 = -uVar8;
  if (param_2 < 1) {
    if (iVar11 < 1) {
      return 0;
    }
  }
  else {
    iVar9 = 0;
    do {
      *(int *)(puVar14 + iVar9 * 4 + iVar1) = param_1;
      iVar9 = iVar9 + 1;
      param_1 = param_1 + 0x14;
    } while (param_2 != iVar9);
    if (iVar11 < 1) goto LAB_10005fc8;
  }
  do {
    iVar13 = 0;
    iVar9 = 0;
    puVar10 = (undefined4 *)(puVar14 + iVar1);
    do {
      puVar5 = (undefined4 *)*puVar10;
      puVar12 = (undefined4 *)puVar10[1];
      iVar9 = iVar9 + 1;
      iVar7 = gx8002_stage2_strcmp(*puVar5,*puVar12);
      if (0 < iVar7) {
        *puVar10 = puVar12;
        puVar10[1] = puVar5;
        iVar13 = iVar13 + 1;
      }
      puVar10 = puVar10 + 1;
    } while (iVar9 < iVar11);
  } while ((iVar13 != 0) && (iVar11 = iVar11 + -1, iVar11 != 0));
  if (param_2 < 1) {
    return 0;
  }
LAB_10005fc8:
  puVar3 = PTR_s____s___s_10006014;
  iVar11 = 0;
  do {
    puVar10 = *(undefined4 **)(puVar14 + iVar11 * 4 + iVar1);
    iVar13 = puVar10[4];
    iVar9 = FUN_10005a7c();
    if (iVar9 != 0) {
      return 1;
    }
    if (iVar13 != 0) {
      FUN_100061a4(puVar3,8,*puVar10,iVar13);
    }
    iVar11 = iVar11 + 1;
  } while (iVar11 < param_2);
  return 0;
}

