
undefined8
FUN_004513c8(int param_1,uint param_2,int param_3,int param_4,int param_5,int *param_6,char param_7)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int local_2c;
  
  local_2c = param_3;
  if (((param_3 != 0) || (param_4 != 0x100)) || (param_5 != 0x100)) {
    for (uVar7 = 0; uVar7 < param_2; uVar7 = uVar7 + 1) {
      *(int *)(param_1 + uVar7 * 8) = *(int *)(param_1 + uVar7 * 8) - *param_6;
      *(int *)(param_1 + uVar7 * 8 + 4) = *(int *)(param_1 + uVar7 * 8 + 4) - param_6[1];
    }
    if (param_3 == 0) {
      for (uVar7 = 0; uVar7 < param_2; uVar7 = uVar7 + 1) {
        *(int *)(param_1 + uVar7 * 8) = *param_6 + (param_4 * *(int *)(param_1 + uVar7 * 8) >> 8);
        *(int *)(param_1 + uVar7 * 8 + 4) =
             param_6[1] + (param_5 * *(int *)(param_1 + uVar7 * 8 + 4) >> 8);
      }
    }
    else {
      if (0xe10 < param_3) {
        param_3 = param_3 + -0xe10;
      }
      if (param_3 < 0) {
        param_3 = param_3 + 0xe10;
      }
      local_2c = param_3 / 10 + 1;
      iVar6 = param_3 % 10;
      sVar1 = (short)(param_3 / 10);
      iVar2 = FUN_004885f0((int)sVar1);
      iVar3 = FUN_004885f0((int)(short)local_2c);
      iVar4 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      iVar5 = FUN_004885f0((int)(short)((short)local_2c + 0x5a));
      iVar2 = ((10 - iVar6) * iVar2 + iVar6 * iVar3) / 10 >> 5;
      iVar3 = ((10 - iVar6) * iVar4 + iVar6 * iVar5) / 10 >> 5;
      for (uVar7 = 0; uVar7 < param_2; uVar7 = uVar7 + 1) {
        iVar4 = *(int *)(param_1 + uVar7 * 8);
        iVar5 = *(int *)(param_1 + uVar7 * 8 + 4);
        if ((param_4 == 0x100) && (param_5 == 0x100)) {
          *(int *)(param_1 + uVar7 * 8) = *param_6 + (iVar4 * iVar3 - iVar5 * iVar2 >> 10);
          *(int *)(param_1 + uVar7 * 8 + 4) = param_6[1] + (iVar4 * iVar2 + iVar5 * iVar3 >> 10);
        }
        else if (param_7 == '\0') {
          *(int *)(param_1 + uVar7 * 8) =
               *param_6 + (param_4 * (iVar4 * iVar3 - iVar5 * iVar2) >> 0x12);
          *(int *)(param_1 + uVar7 * 8 + 4) =
               param_6[1] + (param_5 * (iVar4 * iVar2 + iVar5 * iVar3) >> 0x12);
        }
        else {
          *(int *)(param_1 + uVar7 * 8) =
               *param_6 + (param_4 * iVar4 * iVar3 - param_5 * iVar5 * iVar2 >> 0x12);
          *(int *)(param_1 + uVar7 * 8 + 4) =
               param_6[1] + (param_4 * iVar4 * iVar2 + param_5 * iVar5 * iVar3 >> 0x12);
        }
      }
    }
  }
  return CONCAT44(local_2c,param_2);
}

