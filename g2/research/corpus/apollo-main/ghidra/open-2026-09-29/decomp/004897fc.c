
uint FUN_004897fc(char *param_1,uint param_2,int param_3,undefined4 param_4,int param_5,int *param_6
                 ,uint param_7)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  uint local_34;
  undefined1 local_30 [4];
  int local_2c;
  undefined4 uStack_28;
  
  if (param_6 != (int *)0x0) {
    *param_6 = 0;
  }
  if (param_1 == (char *)0x0) {
    local_34 = 0;
  }
  else if (*param_1 == '\0') {
    local_34 = 0;
  }
  else if (param_3 == 0) {
    local_34 = 0;
  }
  else {
    iVar4 = 0;
    if ((param_7 & 3) == 0) {
      if ((int)(param_7 << 0x1f) < 0) {
        param_5 = 0x1fffffff;
      }
      local_30[0] = 0;
      local_34 = 0;
      uStack_28 = param_4;
      do {
        if (((param_2 <= local_34) || (param_1[local_34] == '\0')) || (param_5 < 1))
        goto LAB_00489902;
        uVar3 = param_7;
        if (local_34 == 0) {
          uVar3 = param_7 | 4;
        }
        local_2c = 0;
        iVar1 = FUN_00489698(param_1 + local_34,param_3,param_4,param_5,uVar3 & 0xff,&local_2c,
                             local_30);
        param_5 = param_5 - local_2c;
        iVar4 = local_2c + iVar4;
        if (((iVar1 == 0) || (local_34 = iVar1 + local_34, *param_1 == '\n')) || (*param_1 == '\r'))
        goto LAB_00489902;
      } while ((param_1[local_34] != '\n') && (param_1[local_34] != '\r'));
      local_34 = local_34 + 1;
LAB_00489902:
      if ((local_34 == 0) &&
         (uVar2 = (*(code *)*DAT_00489eac)(param_1,&local_34), param_6 != (int *)0x0)) {
        iVar4 = FUN_004d57f4(param_3,uVar2,0);
      }
      if (param_6 != (int *)0x0) {
        *param_6 = iVar4;
      }
    }
    else {
      for (local_34 = 0;
          (((local_34 < param_2 && (param_1[local_34] != '\n')) && (param_1[local_34] != '\r')) &&
          (param_1[local_34] != '\0')); local_34 = local_34 + 1) {
      }
      if ((local_34 < param_2) && (param_1[local_34] != '\0')) {
        local_34 = local_34 + 1;
      }
      if (param_6 != (int *)0x0) {
        *param_6 = -1;
      }
    }
  }
  return local_34;
}

