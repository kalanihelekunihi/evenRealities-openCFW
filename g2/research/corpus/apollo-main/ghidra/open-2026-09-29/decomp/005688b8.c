
int FUN_005688b8(int *param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  
  iVar1 = 0;
  if (*(char *)((int)param_1 + 0x29) == '\x01') {
    *param_1 = param_2;
    param_1[1] = param_2 + 0xb40000;
    iVar1 = FUN_00568870(param_1,param_3);
  }
  else if (*(char *)((int)param_1 + 0x29) == '\x02') {
    iVar2 = param_1[0xc];
    FT_Vector_From_Polar(&local_20,iVar2,(int)(&DAT_005a0000 + param_3 * -0x2d0000) + param_2);
    FT_Vector_From_Polar(&local_28,iVar2,param_2);
    local_28 = local_20 + param_1[2] + local_28;
    local_24 = local_1c + param_1[3] + local_24;
    iVar1 = FUN_005683f2(param_1 + param_3 * 8 + 0xd,&local_28,0);
    if (iVar1 == 0) {
      FT_Vector_From_Polar(&local_20,iVar2,param_2 - (int)(&DAT_005a0000 + param_3 * -0x2d0000));
      FT_Vector_From_Polar(&local_28,iVar2,param_2);
      local_28 = param_1[2] + local_20 + local_28;
      local_24 = param_1[3] + local_1c + local_24;
      iVar1 = FUN_005683f2(param_1 + param_3 * 8 + 0xd,&local_28,0);
    }
  }
  else if (*(char *)((int)param_1 + 0x29) == '\0') {
    iVar2 = param_1[0xc];
    FT_Vector_From_Polar(&local_30,iVar2,(int)(&DAT_005a0000 + param_3 * -0x2d0000) + param_2);
    local_30 = param_1[2] + local_30;
    local_2c = param_1[3] + local_2c;
    iVar1 = FUN_005683f2(param_1 + param_3 * 8 + 0xd,&local_30,0);
    if (iVar1 == 0) {
      FT_Vector_From_Polar(&local_30,iVar2,param_2 - (int)(&DAT_005a0000 + param_3 * -0x2d0000));
      local_30 = param_1[2] + local_30;
      local_2c = param_1[3] + local_2c;
      iVar1 = FUN_005683f2(param_1 + param_3 * 8 + 0xd,&local_30,0);
    }
  }
  return iVar1;
}

