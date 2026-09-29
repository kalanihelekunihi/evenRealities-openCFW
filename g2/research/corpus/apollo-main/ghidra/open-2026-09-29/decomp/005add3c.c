
undefined8 CFF_Load_FD_Select(char *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  local_18 = FT_Stream_Seek(param_3,param_4);
  if ((local_18 != 0) || (cVar1 = FT_Stream_ReadChar(param_3,&local_18), local_18 != 0))
  goto LAB_005addb4;
  *param_1 = cVar1;
  param_1[0x14] = '\0';
  param_1[0x15] = '\0';
  param_1[0x16] = '\0';
  param_1[0x17] = '\0';
  if (cVar1 == '\0') {
    *(undefined4 *)(param_1 + 0xc) = param_2;
  }
  else {
    if (cVar1 != '\x03') {
      local_18 = 3;
      goto LAB_005addb4;
    }
    iVar2 = FT_Stream_ReadUShort(param_3,&local_18);
    if (local_18 != 0) goto LAB_005addb4;
    if (iVar2 == 0) {
      local_18 = 3;
      goto LAB_005addb4;
    }
    *(int *)(param_1 + 0xc) = iVar2 * 3 + 2;
  }
  local_18 = FT_Stream_ExtractFrame(param_3,*(undefined4 *)(param_1 + 0xc),param_1 + 8);
LAB_005addb4:
  return CONCAT44(local_18,local_18);
}

