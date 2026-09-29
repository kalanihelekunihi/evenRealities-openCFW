
char * FUN_10006774(char *param_1,uint param_2,int param_3)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  char *pcVar7;
  uint uVar8;
  uint local_24;
  int iStack_20;
  
  local_24 = param_2;
  iStack_20 = param_3;
  if ((param_3 == 0) && (param_2 < 100000)) {
LAB_10006854:
    uVar3 = (local_24 & 0x7f) >> 4;
    uVar4 = (local_24 & 0x7ff) >> 8;
    uVar6 = local_24 >> 0xc;
    iVar2 = (local_24 & 0xf) + (uVar3 + uVar4 + uVar6) * 6;
    uVar8 = (uint)(iVar2 * 0xcd) >> 0xb;
    *param_1 = (char)iVar2 + (char)uVar8 * -10 + '0';
    iVar2 = uVar3 + uVar6 * 9 + uVar4 * 5 + uVar8;
    if (iVar2 == 0) {
      return param_1 + 1;
    }
    uVar3 = (uint)(iVar2 * 0xcd) >> 0xb;
    param_1[1] = (char)iVar2 + (char)uVar3 * -10 + '0';
    iVar2 = uVar3 + uVar4 * 2;
    if ((iVar2 == 0) && (uVar6 == 0)) {
      return param_1 + 2;
    }
    uVar3 = (uint)(iVar2 * 0xd) >> 7;
    param_1[2] = (char)iVar2 + (char)uVar3 * -10 + '0';
    iVar2 = uVar6 * 4 + uVar3;
    if (iVar2 == 0) {
      return param_1 + 3;
    }
    uVar3 = (uint)(iVar2 * 0xcd) >> 0xb;
    cVar1 = (char)uVar3;
    param_1[3] = (char)iVar2 + cVar1 * -10 + '0';
    if (uVar3 == 0) {
      return param_1 + 4;
    }
    param_1[4] = cVar1 + '0';
    return param_1 + 5;
  }
  do {
    if (iStack_20 == 0) goto LAB_1000679a;
    uVar3 = FUN_100065e4(&local_24,100000);
    pcVar7 = param_1;
    while( true ) {
      uVar6 = (uVar3 & 0x7ff) >> 8;
      uVar4 = (uVar3 & 0x7f) >> 4;
      uVar8 = uVar3 >> 0xc;
      iVar2 = (uVar3 & 0xf) + (uVar4 + uVar6 + uVar8) * 6;
      uVar3 = (uint)(iVar2 * 0xcd) >> 0xb;
      *pcVar7 = (char)iVar2 + (char)uVar3 * -10 + '0';
      iVar2 = uVar3 + uVar4 + uVar8 * 9 + uVar6 * 5;
      uVar3 = (uint)(iVar2 * 0xcd) >> 0xb;
      iVar5 = uVar3 + uVar6 * 2;
      uVar4 = (uint)(iVar5 * 0xd) >> 7;
      pcVar7[1] = (char)iVar2 + (char)uVar3 * -10 + '0';
      iVar2 = uVar4 + uVar8 * 4;
      pcVar7[2] = (char)iVar5 + (char)uVar4 * -10 + '0';
      cVar1 = (char)((uint)(iVar2 * 0xcd) >> 0xb);
      pcVar7[3] = (char)iVar2 + cVar1 * -10 + '0';
      param_1 = pcVar7 + 5;
      pcVar7[4] = cVar1 + '0';
      if (iStack_20 != 0) break;
      if (local_24 < 100000) goto LAB_10006854;
LAB_1000679a:
      uVar3 = local_24 % 100000;
      pcVar7 = param_1;
      local_24 = local_24 / 100000;
    }
  } while( true );
}

