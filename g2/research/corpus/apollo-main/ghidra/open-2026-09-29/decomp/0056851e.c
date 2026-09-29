
int FUN_0056851e(undefined4 param_1,int *param_2,undefined4 param_3,int param_4,undefined4 *param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  undefined4 local_28;
  
  local_28 = param_1;
  FT_Vector_From_Polar(&local_48,param_3,param_4);
  local_48 = *param_2 + local_48;
  local_44 = param_2[1] + local_44;
  puVar4 = DAT_00569158;
  if (-1 < (int)param_5) {
    puVar4 = &DAT_005a0000;
  }
  while( true ) {
    if (param_5 == (undefined4 *)0x0) {
      return 0;
    }
    if ((int)param_5 < DAT_0056915c) {
      puVar5 = param_5;
      if ((int)param_5 < (int)DAT_00569158) {
        puVar5 = DAT_00569158;
      }
    }
    else {
      puVar5 = &DAT_005a0000;
    }
    local_40 = (int)puVar5 + param_4;
    puVar6 = puVar5;
    if ((int)puVar5 < 0) {
      puVar6 = (undefined4 *)-(int)puVar5;
    }
    FT_Vector_From_Polar(&local_50,param_3,local_40);
    local_50 = *param_2 + local_50;
    local_4c = param_2[1] + local_4c;
    iVar1 = FT_Cos((int)puVar6 >> 1);
    iVar2 = FT_Sin((int)puVar6 >> 1);
    uVar3 = FT_MulDiv(param_3,iVar2 << 2,(iVar1 + 0x10000) * 3);
    FT_Vector_From_Polar(&local_34,uVar3,(int)puVar4 + param_4);
    local_34 = local_48 + local_34;
    local_30 = local_44 + local_30;
    FT_Vector_From_Polar(&local_3c,uVar3,local_40 - (int)puVar4);
    local_3c = local_50 + local_3c;
    local_38 = local_4c + local_38;
    iVar1 = FUN_005684c2(local_28,&local_34,&local_3c,&local_50);
    if (iVar1 != 0) break;
    local_48 = local_50;
    local_44 = local_4c;
    param_5 = (undefined4 *)((int)param_5 - (int)puVar5);
    param_4 = local_40;
  }
  return iVar1;
}

