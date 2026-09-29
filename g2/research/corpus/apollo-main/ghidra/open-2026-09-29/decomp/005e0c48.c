
int FUN_005e0c48(int param_1,undefined1 *param_2,undefined1 *param_3,int param_4,int param_5,
                int param_6)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  ushort uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  ushort uVar9;
  int iVar10;
  byte *pbVar11;
  byte *pbVar12;
  undefined1 *puVar13;
  uint uVar14;
  char cVar15;
  int iVar16;
  
  iVar10 = 0;
  uVar2 = *(undefined2 *)(*(int *)(param_1 + 0xc) + 4);
  cVar15 = (char)*(undefined2 *)(*(int *)(param_1 + 0xc) + 6);
  uVar3 = *(ushort *)(*(int *)(param_1 + 0xc) + 8);
  uVar4 = *(undefined2 *)(*(int *)(param_1 + 0xc) + 10);
  uVar5 = *(undefined2 *)(*(int *)(param_1 + 0xc) + 0xc);
  uVar9 = *(ushort *)(*(int *)(param_1 + 0xc) + 0xe);
  if (param_2 + 2 <= param_3) {
    puVar13 = param_2 + 2;
    uVar6 = *param_2;
    uVar7 = param_2[1];
    if (puVar13 + (uint)CONCAT11(uVar6,uVar7) * 4 <= param_3) {
      iVar16 = param_4;
      for (uVar14 = 0; uVar14 < CONCAT11(uVar6,uVar7); uVar14 = uVar14 + 1) {
        pbVar11 = puVar13 + 2;
        uVar8 = *puVar13;
        puVar1 = puVar13 + 1;
        pbVar12 = puVar13 + 3;
        puVar13 = puVar13 + 4;
        iVar10 = FUN_005e0eb4(param_1,CONCAT11(uVar8,*puVar1),param_4 + (uint)*pbVar11,
                              param_5 + (uint)*pbVar12,param_6 + 1,0,cVar15,param_4,iVar16);
        if (iVar10 != 0) break;
      }
      *(short *)(*(int *)(param_1 + 0xc) + 4) = (short)(char)uVar2;
      *(short *)(*(int *)(param_1 + 0xc) + 6) = (short)cVar15;
      *(ushort *)(*(int *)(param_1 + 0xc) + 8) = uVar3 & 0xff;
      *(short *)(*(int *)(param_1 + 0xc) + 10) = (short)(char)uVar4;
      *(short *)(*(int *)(param_1 + 0xc) + 0xc) = (short)(char)uVar5;
      *(ushort *)(*(int *)(param_1 + 0xc) + 0xe) = uVar9 & 0xff;
      *(ushort *)(*(int *)(param_1 + 0xc) + 2) =
           (ushort)*(undefined4 *)(*(int *)(param_1 + 8) + 4) & 0xff;
      **(ushort **)(param_1 + 0xc) = (ushort)**(undefined4 **)(param_1 + 8) & 0xff;
      return iVar10;
    }
  }
  return 3;
}

