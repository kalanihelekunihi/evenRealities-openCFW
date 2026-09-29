
int FUN_004544ae(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  int local_18;
  undefined4 uStack_14;
  
  cVar1 = *(char *)(param_1 + 0x3c);
  uStack_14 = param_4;
  uVar2 = FUN_0048aad8(param_2,cVar1);
  if (cVar1 == '\a') {
    iVar3 = 2;
  }
  else if (cVar1 == '\b') {
    iVar3 = 4;
  }
  else if (cVar1 == '\t') {
    iVar3 = 0x10;
  }
  else if (cVar1 == '\n') {
    iVar3 = 0x100;
  }
  else {
    iVar3 = 0;
  }
  if (uVar2 == 0) {
    FUN_0044d25c(2,DAT_00454640,0x4c9,DAT_0045463c,DAT_00454638);
    local_18 = 0;
  }
  else {
    uVar2 = (uint)(*(int *)(*(int *)(param_1 + 0x24) + 0xc) + iVar3 * -4) / uVar2;
    if ((int)param_3 < (int)uVar2) {
      uVar2 = param_3;
    }
    local_24 = 0;
    local_1c = 0;
    local_20 = 0;
    uVar4 = uVar2;
    do {
      local_18 = uVar4 - 1;
      FUN_0044fdbe(*(undefined4 *)(DAT_00454634 + 0x10),0x35,&local_24);
      iVar3 = FUN_004515a4(&local_24);
      if (iVar3 <= (int)uVar2) break;
      uVar4 = uVar4 - 1;
    } while (0 < (int)uVar4);
    if ((int)uVar4 < 1) {
      FUN_0044d25c(2,DAT_00454640,0x4e5,DAT_0045463c,DAT_00454644);
      local_18 = 0;
    }
    else {
      local_18 = local_18 + 1;
    }
  }
  return local_18;
}

