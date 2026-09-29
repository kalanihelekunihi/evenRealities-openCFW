
void FUN_00568abe(int *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  bool bVar6;
  bool bVar7;
  int local_50;
  int local_4c;
  undefined4 *local_48;
  int *local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  undefined4 uStack_28;
  
  local_44 = param_1 + param_2 * 8 + 0xd;
  uStack_28 = param_4;
  if (*(char *)((int)param_1 + 0x2a) == '\0') {
    FUN_00568870(param_1);
  }
  else {
    iVar3 = 0;
    local_40 = param_1[0xc];
    puVar4 = (undefined4 *)0x0;
    iVar2 = 0;
    uVar5 = 0;
    local_48 = &DAT_005a0000 + param_2 * -0x2d0000;
    bVar6 = *(char *)((int)param_1 + 0x2a) == '\x01';
    bVar7 = *(char *)((int)param_1 + 0x2a) != '\x02';
    if (!bVar6) {
      iVar3 = FT_Angle_Diff(*param_1,param_1[1]);
      if (iVar3 == 0xb40000) {
        iVar2 = *param_1;
        puVar4 = local_48;
      }
      else {
        puVar4 = (undefined4 *)(iVar3 / 2);
        iVar2 = (int)local_48 + (int)puVar4 + *param_1;
      }
      uVar5 = FT_Cos(puVar4);
      iVar3 = FT_MulFix(param_1[0xb],uVar5);
      if ((iVar3 < 0x10000) && ((bVar7 || (iVar1 = FUN_00567fc6(puVar4), 0x39 < iVar1)))) {
        bVar6 = true;
      }
    }
    if (bVar6) {
      if (bVar7) {
        FT_Vector_From_Polar(&local_30,local_40,(int)local_48 + param_1[1]);
        local_30 = param_1[2] + local_30;
        local_2c = param_1[3] + local_2c;
        *(undefined1 *)(local_44 + 4) = 0;
        FUN_005683f2(local_44,&local_30,0);
      }
      else {
        uVar5 = FT_MulFix(local_40,param_1[0xb]);
        FT_Vector_From_Polar(&local_38,uVar5,iVar2);
        local_38 = param_1[2] + local_38;
        local_34 = param_1[3] + local_34;
        FT_Sin(puVar4);
        uVar5 = FUN_00567fc6();
        uVar5 = FT_MulDiv(local_40,0x10000 - iVar3,uVar5);
        FT_Vector_From_Polar(&local_50,uVar5,(int)local_48 + iVar2);
        local_50 = local_38 + local_50;
        local_4c = local_34 + local_4c;
        iVar3 = FUN_005683f2(local_44,&local_50,0);
        if (iVar3 == 0) {
          FT_Vector_From_Polar(&local_50,uVar5,iVar2 - (int)local_48);
          local_50 = local_38 + local_50;
          local_4c = local_34 + local_4c;
          iVar3 = FUN_005683f2(local_44,&local_50,0);
          if ((iVar3 == 0) && (param_3 == 0)) {
            FT_Vector_From_Polar(&local_50,local_40,(int)local_48 + param_1[1]);
            local_50 = param_1[2] + local_50;
            local_4c = param_1[3] + local_4c;
            FUN_005683f2(local_44,&local_50,0);
          }
        }
      }
    }
    else {
      uVar5 = FT_DivFix(param_1[0xc],uVar5);
      FT_Vector_From_Polar(&local_40,uVar5,iVar2);
      local_40 = param_1[2] + local_40;
      local_3c = param_1[3] + local_3c;
      iVar3 = FUN_005683f2(local_44,&local_40,0);
      if ((iVar3 == 0) && (param_3 == 0)) {
        FT_Vector_From_Polar(&local_40,param_1[0xc],(int)local_48 + param_1[1]);
        local_40 = param_1[2] + local_40;
        local_3c = param_1[3] + local_3c;
        FUN_005683f2(local_44,&local_40,0);
      }
    }
  }
  return;
}

