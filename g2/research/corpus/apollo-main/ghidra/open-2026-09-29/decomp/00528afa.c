
undefined8 FT_Stream_ReadChar(int *param_1,undefined4 *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint local_18;
  undefined4 uStack_14;
  
  local_18 = param_3 & 0xffffff00;
  *param_2 = 0;
  if (param_1[5] == 0) {
    if ((uint)param_1[2] < (uint)param_1[1]) {
      local_18 = CONCAT31((int3)(param_3 >> 8),*(undefined1 *)(*param_1 + param_1[2]));
      goto LAB_00528b3a;
    }
  }
  else {
    uStack_14 = param_4;
    iVar1 = (*(code *)param_1[5])(param_1,param_1[2],&local_18,1);
    if (iVar1 == 1) {
LAB_00528b3a:
      param_1[2] = param_1[2] + 1;
      iVar1 = (int)(char)local_18;
      goto LAB_00528b26;
    }
  }
  *param_2 = 0x55;
  iVar1 = 0;
LAB_00528b26:
  return CONCAT44(local_18,iVar1);
}

