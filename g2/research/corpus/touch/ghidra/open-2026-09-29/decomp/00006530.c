
void touch_sub_3230(uint param_1,int param_2,int *param_3)

{
  char cVar1;
  ushort uVar2;
  undefined1 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  short *psVar7;
  int iVar8;
  int *piVar9;
  short sVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  
  iVar6 = param_3[1];
  psVar7 = (short *)param_3[0xe];
  iVar8 = **(int **)(*param_3 + 8);
  uVar4 = *(uint *)(iVar8 + DAT_00006600);
  if (*(int *)(iVar8 + DAT_00006604) < 0) {
    *(undefined1 *)(iVar6 + 0x1c) = 1;
  }
  else {
    *(undefined1 *)(iVar6 + 0x1c) = 3;
  }
  *(char *)(iVar6 + 0x18) = (char)param_1;
  *(char *)(iVar6 + 0x19) = (char)param_2;
  uVar3 = __aeabi_uidiv(uVar4 & 0x7ff);
  *(undefined1 *)(iVar6 + 0x1a) = uVar3;
  for (uVar4 = 0; uVar12 = param_1, uVar4 < *(byte *)(iVar6 + 0x1a); uVar4 = uVar4 + 1) {
    for (; uVar12 <= (param_1 + param_2) - 1; uVar12 = uVar12 + 1) {
      uVar11 = *(uint *)(iVar8 + 0x3200);
      sVar10 = (short)uVar11;
      uVar13 = (uint)*(ushort *)(param_3[0xd] + uVar12 * 4);
      iVar5 = touch_sub_4ade(uVar13,param_3);
      if (iVar5 != 0) {
        piVar9 = (int *)(param_3[3] + uVar13 * 0x90);
        cVar1 = *(char *)((int)piVar9 + 0x7a);
        if ((cVar1 == '\x02') || (cVar1 == '\n')) {
          uVar2 = *(ushort *)(*piVar9 + 4);
          if ((uVar11 & 0xffff) < (uint)uVar2) {
            sVar10 = uVar2 - sVar10;
          }
          else {
            sVar10 = 0;
          }
        }
        *psVar7 = sVar10;
      }
      psVar7 = psVar7 + 1;
    }
  }
  return;
}

