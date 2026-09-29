
undefined4 FUN_10006f04(void)

{
  short sVar1;
  byte bVar2;
  int iVar3;
  int *piVar4;
  undefined4 *puVar5;
  byte *pbVar6;
  int iVar7;
  byte bStack_d;
  
  iVar7 = DAT_10006fa8;
  piVar4 = *(int **)(*(int *)(DAT_10006fa8 + 0xc) + 0x10);
  if ((piVar4 != (int *)0x0) && (*piVar4 != 0)) {
    do {
      FUN_10006c30(5,&bStack_d,1);
    } while ((bStack_d & 1) != 0);
    sVar1 = *(short *)(*(int *)(iVar7 + 0xc) + 6);
    if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
      FUN_10006c30(5,&bStack_d,1);
      bVar2 = bStack_d;
      FUN_10006c30(0x35,&bStack_d,1);
      puVar5 = *(undefined4 **)(*(int *)(iVar7 + 0xc) + 0x10);
      iVar7 = puVar5[1];
      if (iVar7 != 0) {
        pbVar6 = (byte *)*puVar5;
        iVar3 = 0;
        do {
          if ((*pbVar6 == (pbVar6[1] & bVar2)) && ((pbVar6[3] & bStack_d) == pbVar6[2])) {
            return *(undefined4 *)(pbVar6 + 4);
          }
          iVar3 = iVar3 + 1;
          pbVar6 = pbVar6 + 8;
        } while (iVar3 != iVar7);
      }
    }
  }
  return 0xffffffff;
}

