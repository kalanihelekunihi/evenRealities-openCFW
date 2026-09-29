
int FUN_004cc600(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5,
                short param_6,undefined2 param_7)

{
  int iVar1;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_25;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  iVar1 = FUN_004cc502(param_1,&local_3c);
  if (iVar1 == 0) {
    local_25 = *(undefined1 *)(param_2 + 0x17);
    local_24 = *(undefined4 *)(param_2 + 0x18);
    local_20 = *(undefined4 *)(param_2 + 0x1c);
    iVar1 = FUN_004cc6ca(param_1,&local_3c,param_3,param_4,param_5,param_6,param_7);
    if (-1 < iVar1) {
      *(undefined4 *)(param_2 + 0x18) = local_3c;
      *(undefined4 *)(param_2 + 0x1c) = local_38;
      *(undefined1 *)(param_2 + 0x17) = 1;
      iVar1 = FUN_004cadea(param_2,param_1 + 0x20);
      if ((iVar1 == 0) && (param_6 == 0)) {
        *(undefined4 *)(param_1 + 0x20) = local_3c;
        *(undefined4 *)(param_1 + 0x24) = local_38;
      }
      iVar1 = 0;
    }
  }
  return iVar1;
}

