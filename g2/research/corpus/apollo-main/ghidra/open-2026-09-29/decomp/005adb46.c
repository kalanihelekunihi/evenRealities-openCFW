
undefined8 cff_index_access_element(int *param_1,uint param_2,int *param_3,int *param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int local_28;
  int *piStack_24;
  
  local_28 = 0;
  if ((param_1 == (int *)0x0) || ((uint)param_1[3] <= param_2)) {
    local_28 = 6;
  }
  else {
    iVar3 = *param_1;
    uVar2 = 0;
    piStack_24 = param_4;
    if (param_1[7] == 0) {
      local_28 = FT_Stream_Seek(iVar3,*(byte *)(param_1 + 4) * param_2 + param_1[2] + param_1[1]);
      if ((local_28 != 0) || (uVar1 = cff_index_read_offset(param_1,&local_28), local_28 != 0))
      goto LAB_005adc48;
      if (uVar1 != 0) {
        do {
          param_2 = param_2 + 1;
          uVar2 = cff_index_read_offset(param_1,&local_28);
          if (uVar2 != 0) break;
        } while (param_2 < (uint)param_1[3]);
      }
    }
    else {
      uVar1 = *(uint *)(param_1[7] + param_2 * 4);
      if (uVar1 != 0) {
        do {
          param_2 = param_2 + 1;
          uVar2 = *(uint *)(param_1[7] + param_2 * 4);
          if (uVar2 != 0) break;
        } while (param_2 < (uint)param_1[3]);
      }
    }
    if ((*(int *)(iVar3 + 4) + 1U < uVar2) || ((*(int *)(iVar3 + 4) - uVar2) + 1 < (uint)param_1[5])
       ) {
      uVar2 = (*(int *)(iVar3 + 4) - param_1[5]) + 1;
    }
    if ((uVar1 == 0) || (uVar2 <= uVar1)) {
      *param_3 = 0;
      *param_4 = 0;
    }
    else {
      *param_4 = uVar2 - uVar1;
      if (param_1[8] == 0) {
        local_28 = FT_Stream_Seek(iVar3,uVar1 + param_1[5] + -1);
        if (local_28 == 0) {
          local_28 = FT_Stream_ExtractFrame(iVar3,uVar2 - uVar1,param_3);
        }
      }
      else {
        *param_3 = param_1[8] + uVar1 + -1;
      }
    }
  }
LAB_005adc48:
  return CONCAT44(local_28,local_28);
}

