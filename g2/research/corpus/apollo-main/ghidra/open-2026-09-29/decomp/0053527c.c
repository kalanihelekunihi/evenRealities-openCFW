
void AttsCalculateDbHash(void)

{
  short sVar1;
  ushort uVar2;
  undefined1 *puVar3;
  int iVar4;
  undefined4 in_r3;
  undefined4 *puVar5;
  int iVar6;
  short sVar7;
  ushort uVar8;
  int *piVar9;
  undefined1 *puVar10;
  byte bVar11;
  undefined1 auStack_38 [16];
  undefined4 uStack_28;
  
  iVar4 = DAT_00535448;
  sVar7 = 0;
  uStack_28 = in_r3;
  for (puVar5 = *(undefined4 **)(DAT_00535448 + 600); puVar5 != (undefined4 *)0x0;
      puVar5 = (undefined4 *)*puVar5) {
    iVar6 = puVar5[1];
    for (uVar8 = (*(short *)((int)puVar5 + 0x12) - *(short *)(puVar5 + 4)) + 1; (uVar8 & 0xff) != 0;
        uVar8 = uVar8 - 1) {
      sVar1 = attsIsHashableAttr(iVar6);
      sVar7 = sVar1 + sVar7;
      iVar6 = iVar6 + 0x10;
    }
  }
  puVar3 = (undefined1 *)WsfBufAlloc(sVar7);
  if (puVar3 != (undefined1 *)0x0) {
    puVar5 = *(undefined4 **)(iVar4 + 600);
    FUN_0043c0e4(auStack_38,0x10,0);
    puVar10 = puVar3;
    for (; puVar5 != (undefined4 *)0x0; puVar5 = (undefined4 *)*puVar5) {
      piVar9 = (int *)puVar5[1];
      for (uVar8 = *(ushort *)(puVar5 + 4); uVar8 <= *(ushort *)((int)puVar5 + 0x12);
          uVar8 = uVar8 + 1) {
        bVar11 = 2;
        uVar2 = attsIsHashableAttr(piVar9);
        if (uVar2 != 0) {
          *puVar10 = (char)uVar8;
          puVar10[1] = (char)(uVar8 >> 8);
          if ((int)((uint)*(byte *)((int)piVar9 + 0xe) << 0x1f) < 0) {
            FUN_00439be4(puVar10 + 2,*piVar9,0x10);
            puVar10 = puVar10 + 0x12;
            bVar11 = 0x10;
          }
          else {
            iVar4 = (uint)*(byte *)(*piVar9 + 1) * 0x100 + (uint)*(byte *)*piVar9;
            puVar10[2] = (char)iVar4;
            puVar10[3] = (char)((uint)iVar4 >> 8);
            puVar10 = puVar10 + 4;
          }
          if ((uint)uVar2 - (uint)bVar11 != 2) {
            FUN_00439be4(puVar10,piVar9[1],*(undefined2 *)piVar9[2]);
            puVar10 = puVar10 + *(ushort *)piVar9[2];
          }
        }
        piVar9 = piVar9 + 4;
      }
    }
    AttsHashDatabaseString(auStack_38,puVar3,sVar7);
  }
  return;
}

