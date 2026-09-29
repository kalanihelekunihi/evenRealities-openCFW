
void FUN_0059b5c4(int param_1,int *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  
  iVar6 = 0;
  piVar5 = param_2 + 2;
  piVar8 = param_2 + 4;
  if (0 < *param_2) {
    do {
      iVar4 = *piVar5;
      iVar3 = *(uint *)(param_1 + 0x20) + 1;
      if (iVar3 < 0x21) {
        *(uint *)(param_1 + 0x1c) =
             (uint)(0 < iVar4) << (*(uint *)(param_1 + 0x20) & 0xff) | *(uint *)(param_1 + 0x1c);
        *(int *)(param_1 + 0x20) = iVar3;
      }
      else {
        FUN_00439b12(param_1,(uint)(0 < iVar4),1);
      }
      iVar3 = DAT_0059b69c;
      if (0 < iVar4) {
        FUN_0059a9c8(param_1,DAT_0059b698 + (uint)*(byte *)(param_2 + 1) * 0x44,iVar4 + -1);
        piVar7 = piVar8;
        do {
          uVar2 = *(uint *)(param_1 + 8) >> 10;
          uVar1 = *(ushort *)(iVar3 + (*piVar7 + 8) * 4) * uVar2 + *(int *)(param_1 + 4);
          uVar2 = *(ushort *)(iVar3 + (*piVar7 + 8) * 4 + 2) * uVar2;
          *(uint *)(param_1 + 8) = uVar2;
          *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | uVar1 >> 0x18;
          *(uint *)(param_1 + 4) = uVar1 & 0xffffff;
          if (uVar2 < 0x10000) {
            FUN_00439b54(param_1);
          }
          iVar3 = iVar3 + 0x44;
          piVar7 = piVar7 + 1;
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
      }
      iVar6 = iVar6 + 1;
      piVar5 = piVar5 + 1;
      piVar8 = piVar8 + 8;
    } while (iVar6 < *param_2);
  }
  return;
}

