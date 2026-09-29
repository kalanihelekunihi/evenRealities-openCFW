
int IsMacResource(undefined4 *param_1,undefined4 param_2,undefined4 param_3,int param_4,
                 undefined4 *param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_30;
  int local_2c;
  undefined4 local_28;
  undefined4 local_24;
  int iStack_20;
  
  uVar2 = *param_1;
  iStack_20 = param_4;
  iVar1 = FT_Raccess_Get_HeaderInfo(param_1,param_2,param_3,&local_24,&local_28);
  if (iVar1 == 0) {
    iVar1 = FT_Raccess_Get_DataOffsets
                      (param_1,param_2,local_24,local_28,DAT_0052680c,1,&local_30,&local_2c);
    if (iVar1 == 0) {
      iVar1 = Mac_Read_POST_Resource(param_1,param_2,local_30,local_2c,param_4,param_5);
      ft_mem_free(uVar2,local_30);
      if (iVar1 == 0) {
        *(undefined4 *)*param_5 = 1;
      }
    }
    else {
      iVar1 = FT_Raccess_Get_DataOffsets
                        (param_1,param_2,local_24,local_28,DAT_00526810,0,&local_30,&local_2c);
      if (iVar1 == 0) {
        iVar1 = Mac_Read_sfnt_Resource
                          (param_1,param_2,local_30,local_2c,
                           param_4 - local_2c * (param_4 / local_2c),param_5);
        ft_mem_free(uVar2,local_30);
        if (iVar1 == 0) {
          *(int *)*param_5 = local_2c;
        }
      }
    }
  }
  return iVar1;
}

