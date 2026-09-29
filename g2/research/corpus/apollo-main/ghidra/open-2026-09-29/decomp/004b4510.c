
void FUN_004b4510(uint param_1,char param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5
                 ,undefined1 param_6)

{
  int iVar1;
  uint local_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_004b46f4;
  if ((((param_2 != '\x01') && (param_2 != '\x04')) &&
      (*(char *)((param_1 & 0xff) + DAT_004b46f4 + 0x59) != param_2)) &&
     (*(char *)((param_1 & 0xff) + DAT_004b46f4 + 0x59) = param_2, *(char *)(iVar1 + 0x5d) != -1)) {
    local_14 = param_1;
    uStack_10 = param_3;
    uStack_c = param_4;
    FUN_004b334c(param_1 & 0xff);
    if (*(char *)((local_14 & 0xff) + iVar1 + 0x57) == '\x03') {
      *(undefined1 *)((local_14 & 0xff) + iVar1 + 0x57) = 0;
      FUN_004b42f0(1,&local_14,&uStack_10,&uStack_c,&param_5,param_6);
    }
    else {
      *(undefined1 *)((local_14 & 0xff) + iVar1 + 0x5b) = 1;
      *(undefined1 *)((local_14 & 0xff) + iVar1 + 0x57) = 3;
      DmAdvStop(1,&local_14);
    }
  }
  return;
}

