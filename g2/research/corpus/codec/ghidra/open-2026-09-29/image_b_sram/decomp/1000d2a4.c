
undefined4 FUN_1000d2a4(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  short *psVar4;
  uint uVar5;
  int iVar6;
  short *psVar7;
  int iVar8;
  undefined2 uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  short sStack_2e;
  
  iVar10 = *(int *)(param_1 + 0xc);
  iVar12 = *(int *)(param_1 + 4);
  param_3 = param_3 - *(int *)(param_1 + 8) * (param_3 / *(int *)(param_1 + 8));
  iVar8 = *(int *)(param_1 + 0x18);
  iVar11 = *(int *)(param_1 + 0x14);
  psVar7 = *(short **)(param_1 + 0x84);
  sStack_2e = 0;
  FUN_1000f134(param_2,&sStack_2e,iVar10 * iVar12);
  uVar5 = (uint)sStack_2e;
  if ((uVar5 >> 0xe & 1) == 1) {
    uVar9 = 0;
  }
  else {
    uVar9 = 1;
    if ((uVar5 >> 0xd & 1) != 1) {
      if ((uVar5 >> 0xc & 1) == 1) {
        uVar9 = 2;
      }
      else if ((uVar5 >> 0xb & 1) == 1) {
        uVar9 = 3;
      }
      else if ((uVar5 >> 10 & 1) == 1) {
        uVar9 = 4;
      }
      else if ((uVar5 >> 9 & 1) == 1) {
        uVar9 = 5;
      }
      else if ((uVar5 >> 8 & 1) == 1) {
        uVar9 = 6;
      }
      else if ((uVar5 >> 7 & 1) == 1) {
        uVar9 = 7;
      }
      else if ((uVar5 >> 6 & 1) == 1) {
        uVar9 = 8;
      }
      else if ((uVar5 >> 5 & 1) == 1) {
        uVar9 = 9;
      }
      else if ((uVar5 >> 4 & 1) == 1) {
        uVar9 = 10;
      }
      else if ((uVar5 >> 3 & 1) == 1) {
        uVar9 = 0xb;
      }
      else if ((uVar5 >> 2 & 1) == 1) {
        uVar9 = 0xc;
      }
      else if ((uVar5 >> 1 & 1) == 1) {
        uVar9 = 0xd;
      }
      else if ((uVar5 & 1) == 0) {
        uVar9 = 0xf;
      }
      else {
        uVar9 = 0xe;
      }
    }
  }
  *(undefined2 *)(*(int *)(param_1 + 0x94) + param_3 * 2) = uVar9;
  uVar1 = DAT_1000d468;
  if (0 < iVar12) {
    iVar14 = 0;
    do {
      if (iVar14 == 0) {
        iVar6 = *(int *)(param_1 + 0x78);
      }
      else {
        iVar6 = *(int *)(param_1 + 0x7c);
      }
      FUN_1000f0c0(param_2,(char)uVar9,psVar7,iVar10);
      iVar13 = *(int *)(param_1 + 0xc);
      if (0 < iVar13) {
        piVar3 = *(int **)(param_1 + 0x70);
        psVar4 = psVar7;
        do {
          iVar2 = *piVar3;
          piVar3 = piVar3 + 1;
          *psVar4 = (short)(iVar2 * *psVar4 >> 0xf);
          psVar4 = psVar4 + 1;
        } while (psVar4 != psVar7 + iVar13);
      }
      FUN_1000f1ac(0,psVar7 + iVar10,iVar11 - iVar10);
      iVar14 = iVar14 + 1;
      gx8002_backup_rfft(uVar1,psVar7,iVar6 + param_3 * iVar8 * 4);
      param_2 = param_2 + iVar10 * 2;
    } while (iVar12 != iVar14);
  }
  return 0;
}

