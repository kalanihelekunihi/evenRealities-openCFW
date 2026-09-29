
int FUN_005cd412(int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,
                int param_6,int param_7,int param_8,int param_9)

{
  byte *pbVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  byte *pbVar9;
  undefined1 auStack_38 [4];
  int local_34;
  int iStack_30;
  int local_2c;
  undefined4 local_28;
  
  iVar4 = param_9 + param_8 + *(int *)(param_3 + 0xc);
  uVar5 = *(int *)(param_1 + 0x2c) * param_2;
  iVar7 = 0;
  uVar6 = uVar5;
  iStack_30 = param_2;
  local_2c = param_3;
  local_28 = param_4;
  do {
    if (*(int *)(param_1 + 0x2c) + uVar5 <= uVar6) {
      return iVar4;
    }
    pbVar1 = *(byte **)(*(int *)(param_1 + 0x34) + uVar6 * 4);
    iVar2 = FUN_005ccba6(pbVar1);
    if (iVar2 == 0) {
      iVar8 = *(int *)(*(int *)(param_1 + 0x3c) + iVar7 * 4);
      for (iVar2 = 0; (uint)(iVar7 + iVar2) < *(int *)(param_1 + 0x2c) - 1U; iVar2 = iVar2 + 1) {
        pbVar9 = *(byte **)(*(int *)(param_1 + 0x34) + (iVar2 + uVar6) * 4);
        iVar3 = FUN_005ccba6(pbVar9);
        if ((iVar3 != 0) || (-1 < (int)((uint)*pbVar9 << 0x1f))) break;
        iVar8 = *(int *)(*(int *)(param_1 + 0x3c) + (iVar2 + iVar7) * 4 + 4) + iVar8;
      }
      if ((int)((uint)*pbVar1 << 0x1e) < 0) {
        if (iVar4 < param_9 + param_8 + *(int *)(local_2c + 0xc)) {
          iVar4 = param_9 + param_8 + *(int *)(local_2c + 0xc);
        }
      }
      else {
        FUN_00489546(auStack_38,*(int *)(*(int *)(param_1 + 0x34) + uVar6 * 4) + 8,local_2c,local_28
                     ,param_5,(iVar8 - param_6) - param_7,0);
        if (iVar4 < param_9 + param_8 + local_34) {
          iVar4 = param_9 + param_8 + local_34;
        }
        uVar6 = iVar2 + uVar6;
        iVar7 = iVar2 + iVar7;
      }
    }
    uVar6 = uVar6 + 1;
    iVar7 = iVar7 + 1;
  } while( true );
}

