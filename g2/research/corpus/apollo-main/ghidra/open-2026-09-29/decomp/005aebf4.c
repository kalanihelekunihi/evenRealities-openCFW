
int cff_subfont_load(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4,
                    int param_5,int param_6,undefined4 *param_7,int param_8)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  int local_64;
  undefined4 *local_60;
  int local_5c;
  int local_58;
  undefined1 auStack_54 [40];
  undefined4 *puStack_2c;
  int local_28;
  
  local_64 = 0;
  local_60 = param_1 + 0x2f;
  local_58 = *(int *)(param_8 + 0x22c);
  if ((param_6 == 0x3000) || (param_6 == 0x4000)) {
    cVar4 = '\x01';
  }
  else {
    cVar4 = '\0';
  }
  if (cVar4 == '\0') {
    uVar1 = 0x60;
  }
  else {
    uVar1 = 0x201;
  }
  puStack_2c = param_1;
  local_28 = param_2;
  iVar2 = cff_parser_init(auStack_54,param_6,param_1,*param_7,uVar1,0,0);
  if (iVar2 == 0) {
    FUN_0043c0e4(param_1,0xbc,0);
    param_1[8] = DAT_005af7ac;
    param_1[9] = 0x320000;
    param_1[0xb] = 2;
    param_1[0xc] = 0x10000;
    param_1[0xf] = 0x10000;
    param_1[0x27] = 0x2210;
    *param_1 = 0xffff;
    param_1[1] = 0xffff;
    param_1[2] = 0xffff;
    param_1[3] = 0xffff;
    param_1[4] = 0xffff;
    param_1[5] = 0xffff;
    param_1[0x20] = 0xffff;
    param_1[0x21] = 0xffff;
    param_1[0x22] = 0xffff;
    param_1[0x2b] = 0xffff;
    if (cVar4 == '\0') {
      uVar1 = 0x30;
    }
    else {
      uVar1 = 0x201;
    }
    param_1[0x2e] = uVar1;
    if (*(int *)(local_28 + 0xc) == 0) {
      iVar2 = FT_Stream_Seek(param_4,*(undefined4 *)(local_28 + 0x14));
      if ((iVar2 != 0) ||
         (iVar2 = FT_Stream_ExtractFrame(param_4,*(undefined4 *)(local_28 + 0x18),&local_64),
         iVar2 != 0)) goto LAB_005aee1a;
      local_5c = *(int *)(local_28 + 0x18);
    }
    else {
      iVar2 = cff_index_access_element(local_28,param_3,&local_64,&local_5c);
    }
    if (iVar2 == 0) {
      iVar2 = cff_parser_run(auStack_54,local_64,local_64 + local_5c);
    }
    if (*(int *)(local_28 + 0xc) == 0) {
      FT_Stream_ReleaseFrame(param_4,&local_64);
    }
    else {
      cff_index_forget_element(local_28,&local_64);
    }
    if (((iVar2 == 0) && (param_1[0x21] == 0xffff)) &&
       (iVar2 = cff_load_private_dict(param_7,param_1,0,0), iVar2 == 0)) {
      if (cVar4 == '\0') {
        if (*(int *)(*(int *)(param_8 + 0x80) + 0x3c) == -1) {
          iVar3 = *(int *)(param_8 + 0x60);
          param_1[0xa2] = *(undefined4 *)(iVar3 + 0x44);
          if (*(int *)(iVar3 + 0x44) != 0) {
            do {
              uVar1 = (**(code **)(local_58 + 0x14))(*(undefined4 *)(iVar3 + 0x44));
              *(undefined4 *)(iVar3 + 0x44) = uVar1;
            } while (*(int *)(iVar3 + 0x44) < 0);
          }
        }
        else {
          param_1[0xa2] = *(undefined4 *)(*(int *)(param_8 + 0x80) + 0x3c);
          if (*(int *)(*(int *)(param_8 + 0x80) + 0x3c) != 0) {
            do {
              uVar1 = (**(code **)(local_58 + 0x14))
                                (*(undefined4 *)(*(int *)(param_8 + 0x80) + 0x3c));
              *(undefined4 *)(*(int *)(param_8 + 0x80) + 0x3c) = uVar1;
            } while (*(int *)(*(int *)(param_8 + 0x80) + 0x3c) < 0);
          }
        }
        if (param_1[0xa2] == 0) {
          param_1[0xa2] = local_60[0x56];
        }
      }
      if (((local_60[0x57] != 0) &&
          (iVar2 = FT_Stream_Seek(param_4,local_60[0x57] + param_1[0x1d] + param_5), iVar2 == 0)) &&
         (iVar2 = cff_index_init(param_1 + 0x98,param_4,1,cVar4), iVar2 == 0)) {
        iVar2 = cff_index_get_pointers(param_1 + 0x98,param_1 + 0xa1,0,0);
      }
    }
  }
LAB_005aee1a:
  cff_parser_done(auStack_54);
  return iVar2;
}

