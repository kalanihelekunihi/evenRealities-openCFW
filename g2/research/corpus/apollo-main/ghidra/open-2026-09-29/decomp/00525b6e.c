
int open_face_from_buffer
              (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
              int param_5,int *param_6)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_3c;
  undefined4 local_38 [4];
  undefined4 local_28;
  undefined4 local_24;
  
  local_3c = 0;
  uVar2 = *param_1;
  iVar1 = new_memory_stream(param_1,param_2,param_3,DAT_005267f0,&local_3c);
  if (iVar1 == 0) {
    local_38[0] = 2;
    local_28 = local_3c;
    if (param_5 != 0) {
      local_38[0] = 10;
      local_24 = FT_Get_Module(param_1);
    }
    iVar1 = FT_Open_Face(param_1,local_38,param_4,param_6,0);
    if (iVar1 == 0) {
      *(uint *)(*param_6 + 8) = *(uint *)(*param_6 + 8) & 0xfffffbff;
    }
    else {
      FT_Stream_Close(local_3c);
      ft_mem_free(uVar2,local_3c);
    }
  }
  else {
    ft_mem_free(uVar2,param_2);
  }
  return iVar1;
}

