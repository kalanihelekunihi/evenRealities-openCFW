
undefined8 FUN_0055f654(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  byte bVar7;
  int aiStack_30 [3];
  
  aiStack_30[0] = param_2;
  aiStack_30[1] = param_3;
  aiStack_30[2] = param_4;
  iVar3 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),0x511,aiStack_30,10);
  iVar2 = DAT_0055f730;
  if (iVar3 == DAT_0055f730) {
    for (bVar7 = 0; iVar3 = iVar2, bVar7 < 8; bVar7 = bVar7 + 1) {
      uVar4 = FUN_0055f2f4(bVar7);
      uVar5 = FUN_0055f2da(bVar7);
      uVar6 = FUN_0055f304(bVar7);
      bVar1 = *(byte *)((int)aiStack_30 + (uVar4 & 0xff));
      uVar4 = FUN_0055f30e(bVar7);
      iVar3 = FUN_0055f4b8(param_1,bVar7,
                           (int)(uVar6 & 0xff & (uint)bVar1) >> (uVar4 & 0xff) & 0xffffU |
                           (uint)*(byte *)((int)aiStack_30 + (uVar5 & 0xff)) << 2,
                           param_2 + (uint)bVar7 * 4);
      if ((iVar3 != iVar2) && (iVar3 != DAT_0055f734)) break;
    }
  }
  return CONCAT44(aiStack_30[0],iVar3);
}

