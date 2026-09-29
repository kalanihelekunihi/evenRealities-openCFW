
undefined8 FUN_0044c834(int param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  int *piVar11;
  undefined4 local_30;
  
  uVar4 = FUN_0044b836(param_3);
  uVar4 = 1 << (uVar4 & 0xff);
  iVar5 = FUN_0044b860(param_2);
  uVar2 = FUN_0044b85c(param_2);
  local_30 = CONCAT22(~uVar2,uVar2);
  uVar3 = *(ushort *)(param_1 + 0x2a);
  uVar9 = 0xffffffff;
  uVar10 = 0;
  while ((uVar10 < (*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4 &&
         (piVar11 = (int *)(*(int *)(param_1 + 0xc) + uVar10 * 8), piVar11[1] << 6 < 0))) {
    if (((uVar3 & 0xf) >> 3 == 0) &&
       (((iVar6 = FUN_0044b860(*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0xffffff),
         iVar6 == iVar5 && ((*(uint *)(*piVar11 + 4) & uVar4) != 0)) &&
        (cVar1 = FUN_0044b7ce(*piVar11,param_3,param_4), cVar1 == '\x01')))) {
      uVar8 = 1;
      goto LAB_0044c96c;
    }
    uVar10 = uVar10 + 1;
  }
  do {
    if ((*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4 <= uVar10) {
      if ((int)uVar9 < 0) {
        uVar8 = 0;
      }
      else {
        uVar8 = 1;
      }
LAB_0044c96c:
      return CONCAT44(local_30,uVar8);
    }
    if ((*(uint *)(*(int *)(*(int *)(param_1 + 0xc) + uVar10 * 8) + 4) & uVar4) != 0) {
      iVar6 = *(int *)(param_1 + 0xc);
      iVar7 = FUN_0044b860(*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0xffffff);
      if (((iVar7 == iVar5) &&
          (uVar3 = FUN_0044b85c(*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0xffffff),
          (uVar3 & ~uVar2) == 0)) &&
         (((int)uVar9 < (int)(uint)uVar3 &&
          (cVar1 = FUN_0044b7ce(*(undefined4 *)(iVar6 + uVar10 * 8),param_3,param_4),
          cVar1 == '\x01')))) {
        if (uVar3 == uVar2) {
          uVar8 = 1;
          goto LAB_0044c96c;
        }
        uVar9 = (uint)uVar3;
      }
    }
    uVar10 = uVar10 + 1;
  } while( true );
}

