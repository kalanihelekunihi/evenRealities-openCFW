
undefined8 FUN_00464344(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  
  iVar1 = DAT_004646b8;
  iVar10 = DAT_004646b8 + 0x74;
  if (*(char *)(DAT_004646b8 + 0x88) == '\0') {
    *(undefined1 *)(DAT_004646b8 + 0x88) = 1;
    if (*(char *)(iVar1 + 0x80) == '\0') {
      *(undefined1 *)(iVar1 + 0x88) = 0;
      uVar3 = 1;
    }
    else {
      FUN_0049acba();
      iVar4 = FUN_00473482();
      if ((iVar4 == 0) &&
         (*(int *)(iVar1 + 0x98) = *(int *)(iVar1 + 0x98) + 1, 100 < *(uint *)(iVar1 + 0x98))) {
        *(undefined4 *)(iVar1 + 0x98) = 0;
        param_3 = DAT_004646bc;
        FUN_0044d25c(2,DAT_004646c4,0x59,DAT_004646c0,DAT_004646bc,param_4);
      }
      do {
        *(undefined1 *)(iVar1 + 0x82) = 0;
        *(undefined1 *)(iVar1 + 0x83) = 0;
        iVar5 = FUN_00482cd8(iVar10);
        while (iVar9 = iVar5, iVar9 != 0) {
          iVar5 = FUN_00482cf0(iVar10,iVar9);
          iVar6 = FUN_00464604(iVar9);
          if ((iVar6 != 0) &&
             ((*(char *)(iVar1 + 0x83) != '\0' || (*(char *)(iVar1 + 0x82) != '\0')))) break;
        }
      } while (iVar9 != 0);
      uVar3 = 0xffffffff;
      for (iVar5 = FUN_00482cd8(iVar10); iVar5 != 0; iVar5 = FUN_00482cf0(iVar10,iVar5)) {
        if ((-1 < (int)((uint)*(byte *)(iVar5 + 0x14) << 0x1f)) &&
           (uVar7 = FUN_0046467c(iVar5), uVar7 < uVar3)) {
          uVar3 = uVar7;
        }
      }
      iVar10 = FUN_004734a0(iVar4);
      *(int *)(iVar1 + 0x90) = iVar10 + *(int *)(iVar1 + 0x90);
      uVar7 = FUN_004734a0(*(undefined4 *)(iVar1 + 0x94));
      if (499 < uVar7) {
        *(char *)(iVar1 + 0x81) = (char)((uint)(*(int *)(iVar1 + 0x90) * 100) / uVar7);
        if (*(byte *)(iVar1 + 0x81) < 0x65) {
          cVar2 = 'd' - *(char *)(iVar1 + 0x81);
        }
        else {
          cVar2 = '\0';
        }
        *(char *)(iVar1 + 0x81) = cVar2;
        *(undefined4 *)(iVar1 + 0x90) = 0;
        uVar8 = FUN_00473482();
        *(undefined4 *)(iVar1 + 0x94) = uVar8;
      }
      *(uint *)(iVar1 + 0x84) = uVar3;
      *(undefined1 *)(iVar1 + 0x88) = 0;
      FUN_0049acc4();
    }
  }
  else {
    uVar3 = 1;
  }
  return CONCAT44(param_3,uVar3);
}

