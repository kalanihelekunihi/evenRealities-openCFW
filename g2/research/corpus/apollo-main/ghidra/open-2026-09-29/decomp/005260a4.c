
undefined8
Mac_Read_sfnt_Resource
          (undefined4 *param_1,char *param_2,int param_3,int param_4,uint param_5,undefined4 param_6
          )

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  char *pcVar7;
  int local_28;
  
  uVar5 = *param_1;
  if ((int)param_5 < 0) {
    param_5 = ~param_5;
  }
  pcVar7 = param_2;
  if ((int)param_5 < param_4) {
    iVar6 = *(int *)(param_3 + param_5 * 4);
    local_28 = param_4;
    local_28 = FT_Stream_Seek(param_2,iVar6);
    if ((local_28 == 0) && (uVar2 = FT_Stream_ReadULong(param_2,&local_28), local_28 == 0)) {
      if ((int)uVar2 < 1) {
        local_28 = 1;
      }
      else if (uVar2 < 0x1000000) {
        pcVar7 = (char *)0x0;
        iVar3 = open_face_PS_from_sfnt_stream(param_1,param_2,param_5,0,0,param_6);
        local_28 = 0;
        if (((iVar3 != 0) &&
            (local_28 = iVar3, local_28 = FT_Stream_Seek(param_2,iVar6 + 4), local_28 == 0)) &&
           (uVar4 = ft_mem_alloc(uVar5,uVar2,&local_28), local_28 == 0)) {
          local_28 = FT_Stream_Read(param_2,uVar4,uVar2);
          if (local_28 == 0) {
            if (((int)uVar2 < 5) || (iVar6 = FUN_004751c8(uVar4,DAT_00526804,4), iVar6 != 0)) {
              bVar1 = false;
            }
            else {
              bVar1 = true;
            }
            pcVar7 = DAT_00526808;
            if (bVar1) {
              pcVar7 = s_stibltuopmoccff_0052628c + 0xc;
            }
            local_28 = open_face_from_buffer(param_1,uVar4,uVar2,0,pcVar7,param_6);
          }
          else {
            ft_mem_free(uVar5,uVar4);
          }
        }
      }
      else {
        local_28 = 9;
      }
    }
  }
  else {
    local_28 = 1;
  }
  return CONCAT44(pcVar7,local_28);
}

