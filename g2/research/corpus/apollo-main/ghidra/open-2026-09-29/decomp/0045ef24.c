
void FUN_0045ef24(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_48;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_004503d6(&local_78);
  local_78 = *(undefined4 *)(param_1 + 4);
  cVar1 = *(char *)(param_1 + 10);
  if (cVar1 == '\0') {
    cVar2 = *(char *)(param_1 + 8);
    local_48 = *(undefined4 *)(param_1 + 0xc);
  }
  else {
    cVar2 = *(char *)(param_1 + 9);
    local_48 = *(undefined4 *)(param_1 + 0x10);
  }
  iVar3 = FUN_0045fcd2(*(undefined4 *)(param_1 + 4));
  if (iVar3 != 0) {
    *(undefined1 *)(iVar3 + 0xe8) = 1;
  }
  FUN_0045bbb6();
  if (cVar1 == '\0') {
    if ((param_2 == '\0') && (*(char *)(param_1 + 0xb) == '\x01')) {
      local_68 = DAT_0045f6a0;
    }
    else {
      local_68 = DAT_0045f69c;
    }
    if (cVar2 == '\0') {
      FUN_0044dca2(*(undefined4 *)(param_1 + 4));
      iVar3 = FUN_0043fd9e();
      local_74 = DAT_0045f6a4;
      if (param_2 == '\0') {
        iVar4 = FUN_0043fc70(*(undefined4 *)(param_1 + 4));
        iVar3 = FUN_0043fd9e(*(undefined4 *)(param_1 + 4));
        iVar3 = -iVar3;
      }
      else {
        iVar4 = FUN_0043fd9e(*(undefined4 *)(param_1 + 4));
        iVar4 = -iVar4;
        iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
      }
    }
    else if (cVar2 == '\x01') {
      FUN_0044dca2(*(undefined4 *)(param_1 + 4));
      iVar3 = FUN_0043fdda();
      local_74 = DAT_0045fa74;
      if (param_2 == '\0') {
        iVar4 = FUN_0043fce0(*(undefined4 *)(param_1 + 4));
      }
      else {
        iVar4 = iVar3;
        iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
      }
    }
    else {
      FUN_0044dca2(*(undefined4 *)(param_1 + 4));
      iVar3 = FUN_0043fdda();
      local_74 = DAT_0045fa74;
      if (param_2 == '\0') {
        iVar4 = FUN_0043fce0(*(undefined4 *)(param_1 + 4));
        iVar3 = FUN_0043fdda(*(undefined4 *)(param_1 + 4));
        iVar3 = -iVar3;
      }
      else {
        iVar4 = FUN_0043fdda(*(undefined4 *)(param_1 + 4));
        iVar4 = -iVar4;
        iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
      }
    }
    FUN_004506ce(&local_78,iVar4,iVar3);
  }
  else {
    FUN_0044dca2(*(undefined4 *)(param_1 + 4));
    if (cVar2 == '\0') {
      iVar3 = FUN_0043fd9e();
      iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
    }
    else if (cVar2 == '\x01') {
      iVar3 = FUN_0043fdda();
      iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
    }
    else {
      iVar3 = FUN_0043fdda();
      iVar3 = ((100 - *(short *)(param_1 + 0x14)) * iVar3) / 100;
    }
    if (param_2 == '\0') {
      local_74 = DAT_0045f690;
      FUN_004506ce(&local_78,0xff,0);
      if (*(char *)(param_1 + 0xb) == '\x01') {
        local_68 = DAT_0045f698;
      }
      else {
        local_68 = DAT_0045f69c;
      }
    }
    else {
      if (cVar2 == '\0') {
        FUN_0043f0e0(*(undefined4 *)(param_1 + 4));
      }
      else {
        FUN_0043f142(*(undefined4 *)(param_1 + 4),iVar3);
      }
      FUN_00441488(*(undefined4 *)(param_1 + 4),0,0);
      local_74 = DAT_0045f690;
      FUN_004506ce(&local_78,0,0xff);
      local_68 = DAT_0045f694;
    }
  }
  FUN_00450408(&local_78);
  return;
}

