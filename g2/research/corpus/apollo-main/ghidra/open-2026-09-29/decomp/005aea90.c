
int cff_load_private_dict(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  byte *pbVar4;
  int iVar5;
  undefined1 auStack_4c [40];
  
  iVar3 = 0;
  pbVar4 = (byte *)(param_2 + 0xbc);
  iVar5 = param_1[1];
  *(undefined4 **)(param_2 + 0x230) = param_1;
  *(undefined1 *)(param_2 + 0x22d) = 0;
  if ((*(int *)(param_2 + 0x74) != 0) && (*(int *)(param_2 + 0x78) != 0)) {
    FUN_0043c0e4(pbVar4,0x170,0);
    *(undefined4 *)(param_2 + 0x184) = 7;
    *(undefined4 *)(param_2 + 0x188) = 1;
    *(undefined4 *)(param_2 + 0x208) = 0xffffffff;
    *(undefined4 *)(param_2 + 0x210) = 0xf5c;
    *(undefined4 *)(param_2 + 0x180) = DAT_005af7a4;
    *(int *)(param_2 + 0x228) = param_2;
    *(undefined4 *)(param_2 + 0x248) = param_3;
    *(undefined4 *)(param_2 + 0x24c) = param_4;
    if (*(char *)(param_1 + 8) == '\0') {
      iVar2 = 0x61;
    }
    else {
      iVar2 = param_1[0x185] + 1;
    }
    if (*(char *)(param_1 + 8) == '\0') {
      uVar1 = 0x2000;
    }
    else {
      uVar1 = 0x5000;
    }
    iVar2 = cff_parser_init(auStack_4c,uVar1,pbVar4,*param_1,iVar2,*(undefined2 *)(param_2 + 0xb0),
                            *(undefined2 *)(param_2 + 0xb2));
    if (((iVar2 == 0) &&
        (iVar3 = FT_Stream_Seek(iVar5,*(int *)(param_2 + 0x74) + param_1[3]), iVar3 == 0)) &&
       (iVar3 = FT_Stream_EnterFrame(iVar5,*(undefined4 *)(param_2 + 0x78)), iVar3 == 0)) {
      iVar3 = cff_parser_run(auStack_4c,*(undefined4 *)(iVar5 + 0x20),*(undefined4 *)(iVar5 + 0x24))
      ;
      FT_Stream_ExitFrame(iVar5);
      if (iVar3 == 0) {
        *pbVar4 = *pbVar4 & 0xfe;
        if (*(int *)(param_2 + 0x214) < 0) {
          *(int *)(param_2 + 0x214) = -*(int *)(param_2 + 0x214);
        }
        else if (*(int *)(param_2 + 0x214) == 0) {
          *(undefined4 *)(param_2 + 0x214) = DAT_005af7a8;
        }
        if (1000 < *(uint *)(param_2 + 0x184)) {
          *(undefined4 *)(param_2 + 0x184) = 7;
        }
        if (1000 < *(uint *)(param_2 + 0x188)) {
          *(undefined4 *)(param_2 + 0x188) = 1;
        }
      }
    }
    cff_blend_clear(param_2);
    cff_parser_done(auStack_4c);
  }
  return iVar3;
}

