
int FUN_005d3068(undefined4 *param_1,int param_2,int param_3)

{
  char cVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  undefined4 uVar7;
  char local_5c;
  char local_5b [3];
  int local_58;
  undefined4 local_54;
  int local_50;
  undefined1 auStack_4c [4];
  int local_48;
  int local_44;
  int local_40;
  undefined1 auStack_3c [12];
  undefined1 auStack_30 [12];
  
  local_58 = 0;
  cVar1 = *(char *)(param_1 + 0xc);
  if ((cVar1 == '\0') || (param_1[0x86] != 0)) {
    uVar7 = *param_1;
    puVar6 = *(undefined4 **)param_1[0x87];
    if (*(int *)param_1[0x87] == 0) {
      *(undefined4 *)(param_1[0x87] + 4) = DAT_005d3234;
      uVar5 = ft_mem_alloc(uVar7,0x228,&local_58);
      *(undefined4 *)param_1[0x87] = uVar5;
      if (local_58 != 0) {
        return 0x40;
      }
      puVar6 = *(undefined4 **)param_1[0x87];
      *puVar6 = uVar7;
      if (cVar1 == '\0') {
        puVar6[0x89] = *(undefined4 *)(param_1[0x85] + 0xc10);
      }
      FUN_005d2fee(puVar6 + 0x24,*puVar6,puVar6 + 1);
    }
    puVar6[0x2c] = param_1;
    puVar6[0x2b] = param_1;
    iVar4 = *(int *)(param_1[1] + 0x60);
    cVar2 = *(char *)(iVar4 + 0x20);
    cVar3 = *(char *)(*(int *)(param_1[1] + 0x80) + 0x38);
    local_50 = param_3;
    FUN_0043c0e4(auStack_4c,0x10,0);
    local_44 = param_2 + local_50;
    local_48 = param_2;
    local_40 = param_2;
    FUN_0043c0e4(auStack_3c,0x18,0);
    FUN_005d3018(param_1,auStack_3c,auStack_30,local_5b,&local_5c);
    if (cVar1 == '\0') {
      *(undefined1 *)((int)puVar6 + 9) = *(undefined1 *)(param_1[1] + 0x2b8);
    }
    else {
      *(undefined1 *)((int)puVar6 + 9) = 0;
    }
    *(char *)(puVar6 + 2) = cVar1;
    puVar6[3] = 0;
    if (local_5b[0] != '\0') {
      puVar6[3] = puVar6[3] | 1;
    }
    if ((local_5c != '\0') && ((cVar3 == '\0' || ((cVar3 < '\0' && (cVar2 == '\0')))))) {
      puVar6[3] = puVar6[3] | 2;
    }
    puVar6[0x2f] = *(undefined4 *)(iVar4 + 0x24);
    puVar6[0x30] = *(undefined4 *)(iVar4 + 0x28);
    puVar6[0x31] = *(undefined4 *)(iVar4 + 0x2c);
    puVar6[0x32] = *(undefined4 *)(iVar4 + 0x30);
    puVar6[0x33] = *(undefined4 *)(iVar4 + 0x34);
    puVar6[0x34] = *(undefined4 *)(iVar4 + 0x38);
    puVar6[0x35] = *(undefined4 *)(iVar4 + 0x3c);
    puVar6[0x36] = *(undefined4 *)(iVar4 + 0x40);
    uVar7 = FUN_005d3060(param_1);
    puVar6[0x21] = uVar7;
    if ((local_5c == '\0') || (iVar4 = FUN_005d2ea8(auStack_3c,puVar6[0x21]), iVar4 == 0)) {
      iVar4 = FUN_005d2e0c(puVar6,auStack_4c,auStack_3c,&local_54);
      if (iVar4 == 0) {
        FUN_005d2ee4(puVar6 + 0x24,local_54);
        iVar4 = 0;
      }
      else {
        iVar4 = 3;
      }
    }
  }
  else {
    iVar4 = 8;
  }
  return iVar4;
}

