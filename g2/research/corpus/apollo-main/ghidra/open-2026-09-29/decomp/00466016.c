
longlong FUN_00466016(void)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  undefined2 uVar6;
  uint in_r3;
  int iVar7;
  int iVar8;
  
  iVar7 = DAT_004667f0;
  iVar5 = DAT_004667ec;
  iVar8 = *(int *)(DAT_004667f0 + 0x14);
  uVar6 = FUN_0049acd4(DAT_004667ec,0x12,0);
  *(undefined2 *)(iVar5 + 0x12) = uVar6;
  sVar1 = *(short *)(iVar8 + 0x12);
  sVar2 = *(short *)(iVar5 + 0x12);
  iVar8 = *(int *)(iVar7 + 0xc);
  uVar6 = FUN_0049acd4(iVar5 + 0x14,8,0);
  *(undefined2 *)(iVar5 + 0x1c) = uVar6;
  sVar3 = *(short *)(iVar8 + 8);
  sVar4 = *(short *)(iVar5 + 0x1c);
  iVar7 = *(int *)(iVar7 + 0x10);
  uVar6 = FUN_0049acd4(iVar5 + 0x20,8,0);
  *(undefined2 *)(iVar5 + 0x28) = uVar6;
  if (*(short *)(iVar7 + 8) != *(short *)(iVar5 + 0x28) || (sVar3 != sVar4 || sVar1 != sVar2)) {
    FUN_00448e34();
  }
  return (ulonglong)in_r3 << 0x20;
}

