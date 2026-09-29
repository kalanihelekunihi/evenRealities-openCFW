
char FUN_00544d60(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 local_48;
  undefined4 local_44;
  char local_40 [4];
  undefined1 auStack_3c [4];
  undefined4 local_38;
  uint local_34;
  undefined4 local_30;
  byte local_2c [4];
  int local_28;
  
  local_40[0] = '\0';
  iVar4 = *(int *)(param_2 + 0x14);
  uVar2 = FUN_0044a43c(param_3);
  if (uVar2 < 0x41) {
    FUN_0043c0e4(auStack_3c,0x18,0xff);
    local_38 = DAT_0054554c;
    local_2c[0] = FUN_0044a43c(param_3);
    local_28 = param_5;
    local_34 = param_5 + (uint)local_2c[0] + 0x18;
    if (param_1[3] - 0x10 < local_34) {
      FUN_004733ee(DAT_00545534);
      uVar3 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00545538,*param_1,uVar3);
      FUN_004733ee(DAT_00545550);
      cVar1 = '\a';
    }
    else if ((iVar4 == -1) && (iVar4 = FUN_00544af2(param_1,param_2,local_34), iVar4 == -1)) {
      cVar1 = '\a';
    }
    else {
      cVar1 = FUN_005446b8(param_1,param_2,local_34,local_40);
      if (cVar1 == '\0') {
        local_48 = CONCAT31(local_48._1_3_,0xff);
        local_30 = 0;
        local_30 = FUN_00585840(0,local_2c,4);
        local_30 = FUN_00585840(local_30,&local_28,4);
        local_30 = FUN_00585840(local_30,param_3,local_2c[0]);
        iVar5 = 0;
        while (iVar5 != 0) {
          local_30 = FUN_00585840(local_30,&local_48,1);
          iVar5 = iVar5 + -1;
        }
        local_30 = FUN_00585840(local_30,param_4,local_28);
        iVar5 = 0;
        while (iVar5 != 0) {
          local_30 = FUN_00585840(local_30,&local_48,1);
          iVar5 = iVar5 + -1;
        }
        cVar1 = FUN_005445b2(param_1,iVar4,auStack_3c);
      }
      if (cVar1 == '\0') {
        cVar1 = FUN_00544cf6(param_1,iVar4 + 0x18,param_3,local_2c[0]);
        if (local_40[0] == '\0') {
          FUN_00543cec(param_1,*(undefined4 *)(param_2 + 4),
                       local_28 + iVar4 + (uint)local_2c[0] + 0x18);
        }
        FUN_00543d1c(param_1,param_3,local_2c[0],iVar4);
      }
      if (cVar1 == '\0') {
        cVar1 = FUN_00544cf6(param_1,iVar4 + (uint)local_2c[0] + 0x18,param_4,local_28);
      }
      if (cVar1 == '\0') {
        local_44 = 1;
        local_48 = 2;
        cVar1 = FUN_005858d8(param_1,iVar4,auStack_3c,6);
      }
      if ((cVar1 == '\0') && (local_40[0] != '\0')) {
        *(undefined1 *)(param_1 + 0xc) = 1;
      }
    }
  }
  else {
    FUN_004733ee(DAT_00545534);
    uVar3 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00545538,*param_1,uVar3);
    FUN_004733ee(DAT_00545548,0x40);
    cVar1 = '\x05';
  }
  return cVar1;
}

