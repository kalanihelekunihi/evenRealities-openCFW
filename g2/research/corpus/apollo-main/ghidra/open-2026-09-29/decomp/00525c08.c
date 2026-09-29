
undefined8
ft_lookup_PS_in_sfnt_stream
          (undefined4 param_1,int param_2,int *param_3,int *param_4,undefined1 *param_5)

{
  bool bVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_30;
  int *local_2c;
  int *piStack_28;
  
  *param_3 = 0;
  *param_4 = 0;
  *param_5 = 0;
  local_30 = param_2;
  local_2c = param_3;
  piStack_28 = param_4;
  iVar3 = FT_Stream_ReadULong(param_1,&local_30);
  iVar5 = local_30;
  if (local_30 == 0) {
    if (iVar3 == DAT_005267f4) {
      uVar2 = FT_Stream_ReadUShort(param_1,&local_30);
      local_2c = (int *)CONCAT22(local_2c._2_2_,uVar2);
      iVar5 = local_30;
      if ((local_30 == 0) && (local_30 = FT_Stream_Skip(param_1,6), iVar5 = local_30, local_30 == 0)
         ) {
        iVar3 = -1;
        *param_5 = 0;
        for (iVar6 = 0; iVar6 < (int)((uint)local_2c & 0xffff); iVar6 = iVar6 + 1) {
          iVar4 = FT_Stream_ReadULong(param_1,&local_30);
          if ((local_30 == 0) && (local_30 = FT_Stream_Skip(param_1,4), local_30 == 0)) {
            iVar5 = FT_Stream_ReadULong(param_1,&local_30);
            *param_3 = iVar5;
            if (local_30 != 0) goto LAB_00525cf6;
            iVar5 = FT_Stream_ReadULong(param_1,&local_30);
            *param_4 = iVar5;
            if (local_30 != 0) goto LAB_00525cf6;
            bVar1 = false;
          }
          else {
LAB_00525cf6:
            bVar1 = true;
          }
          iVar5 = local_30;
          if (bVar1) goto LAB_00525d2e;
          if (iVar4 == DAT_005267f8) {
            iVar3 = iVar3 + 1;
            *param_3 = *param_3 + 0x16;
            *param_4 = *param_4 + -0x16;
            *param_5 = 1;
            if (param_2 < 0) {
              iVar5 = 0;
              goto LAB_00525d2e;
            }
          }
          else if (iVar4 == DAT_005267fc) {
            iVar3 = iVar3 + 1;
            *param_3 = *param_3 + 0x18;
            *param_4 = *param_4 + -0x18;
            *param_5 = 0;
            if (param_2 < 0) {
              iVar5 = 0;
              goto LAB_00525d2e;
            }
          }
          if ((-1 < param_2) && (iVar3 == param_2)) {
            iVar5 = 0;
            goto LAB_00525d2e;
          }
        }
        iVar5 = 0x8e;
      }
    }
    else {
      iVar5 = 2;
    }
  }
LAB_00525d2e:
  return CONCAT44(local_30,iVar5);
}

