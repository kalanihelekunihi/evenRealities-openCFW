
int FUN_005beb90(int *param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  byte *pbVar3;
  uint uVar4;
  int iVar5;
  
  if (((param_1 == (int *)0x0) || (param_1[7] == 0)) || (*param_1 == 0)) {
    return -2;
  }
  if (param_2 == 4) {
    iVar5 = -5;
  }
  else {
    iVar5 = 0;
  }
  iVar2 = -5;
LAB_005bebf4:
  while( true ) {
    while (bVar1 = *(byte *)param_1[7], bVar1 == 0) {
      if (param_1[1] == 0) {
        return iVar2;
      }
      param_1[1] = param_1[1] + -1;
      param_1[2] = param_1[2] + 1;
      pbVar3 = (byte *)*param_1;
      *param_1 = (int)(pbVar3 + 1);
      *(uint *)(param_1[7] + 4) = (uint)*pbVar3;
      if ((*(byte *)(param_1[7] + 4) & 0xf) == 8) {
        if ((*(uint *)(param_1[7] + 4) >> 4) + 8 <= *(uint *)(param_1[7] + 0x10)) {
          *(undefined1 *)param_1[7] = 1;
          iVar2 = iVar5;
          goto LAB_005bec6e;
        }
        *(undefined1 *)param_1[7] = 0xd;
        param_1[6] = DAT_005bf09c;
        *(undefined4 *)(param_1[7] + 4) = 5;
        iVar2 = iVar5;
      }
      else {
        *(undefined1 *)param_1[7] = 0xd;
        param_1[6] = DAT_005bf098;
        *(undefined4 *)(param_1[7] + 4) = 5;
        iVar2 = iVar5;
      }
    }
    if (bVar1 == 2) goto LAB_005becca;
    if (1 < bVar1) break;
LAB_005bec6e:
    if (param_1[1] == 0) {
      return iVar2;
    }
    param_1[1] = param_1[1] + -1;
    param_1[2] = param_1[2] + 1;
    pbVar3 = (byte *)*param_1;
    *param_1 = (int)(pbVar3 + 1);
    uVar4 = (uint)*pbVar3;
    if ((uVar4 + *(int *)(param_1[7] + 4) * 0x100) % 0x1f == 0) {
      if ((int)(uVar4 << 0x1a) < 0) {
        *(undefined1 *)param_1[7] = 2;
        iVar2 = iVar5;
LAB_005becca:
        if (param_1[1] == 0) {
          return iVar2;
        }
        param_1[1] = param_1[1] + -1;
        param_1[2] = param_1[2] + 1;
        pbVar3 = (byte *)*param_1;
        *param_1 = (int)(pbVar3 + 1);
        *(uint *)(param_1[7] + 8) = (uint)*pbVar3 << 0x18;
        *(undefined1 *)param_1[7] = 3;
        iVar2 = iVar5;
LAB_005becf6:
        if (param_1[1] == 0) {
          return iVar2;
        }
        param_1[1] = param_1[1] + -1;
        param_1[2] = param_1[2] + 1;
        pbVar3 = (byte *)*param_1;
        *param_1 = (int)(pbVar3 + 1);
        *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3 * 0x10000;
        *(undefined1 *)param_1[7] = 4;
        iVar2 = iVar5;
LAB_005bed28:
        if (param_1[1] == 0) {
          return iVar2;
        }
        param_1[1] = param_1[1] + -1;
        param_1[2] = param_1[2] + 1;
        pbVar3 = (byte *)*param_1;
        *param_1 = (int)(pbVar3 + 1);
        *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3 * 0x100;
        *(undefined1 *)param_1[7] = 5;
        iVar2 = iVar5;
LAB_005bed5a:
        if (param_1[1] == 0) {
          return iVar2;
        }
        param_1[1] = param_1[1] + -1;
        param_1[2] = param_1[2] + 1;
        pbVar3 = (byte *)*param_1;
        *param_1 = (int)(pbVar3 + 1);
        *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3;
        param_1[0xc] = *(int *)(param_1[7] + 8);
        *(undefined1 *)param_1[7] = 6;
        return 2;
      }
      *(undefined1 *)param_1[7] = 7;
      iVar2 = iVar5;
    }
    else {
      *(undefined1 *)param_1[7] = 0xd;
      param_1[6] = DAT_005bf0a0;
      *(undefined4 *)(param_1[7] + 4) = 5;
      iVar2 = iVar5;
    }
  }
  if (bVar1 == 4) goto LAB_005bed28;
  if (bVar1 < 4) goto LAB_005becf6;
  if (bVar1 == 6) {
    *(undefined1 *)param_1[7] = 0xd;
    param_1[6] = DAT_005bf0a4;
    *(undefined4 *)(param_1[7] + 4) = 0;
    return -2;
  }
  if (bVar1 < 6) goto LAB_005bed5a;
  if (bVar1 == 8) {
LAB_005bee02:
    if (param_1[1] == 0) {
      return iVar2;
    }
    param_1[1] = param_1[1] + -1;
    param_1[2] = param_1[2] + 1;
    pbVar3 = (byte *)*param_1;
    *param_1 = (int)(pbVar3 + 1);
    *(uint *)(param_1[7] + 8) = (uint)*pbVar3 << 0x18;
    *(undefined1 *)param_1[7] = 9;
    iVar2 = iVar5;
LAB_005bee2a:
    if (param_1[1] == 0) {
      return iVar2;
    }
    param_1[1] = param_1[1] + -1;
    param_1[2] = param_1[2] + 1;
    pbVar3 = (byte *)*param_1;
    *param_1 = (int)(pbVar3 + 1);
    *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3 * 0x10000;
    *(undefined1 *)param_1[7] = 10;
    iVar2 = iVar5;
LAB_005bee58:
    if (param_1[1] == 0) {
      return iVar2;
    }
    param_1[1] = param_1[1] + -1;
    param_1[2] = param_1[2] + 1;
    pbVar3 = (byte *)*param_1;
    *param_1 = (int)(pbVar3 + 1);
    *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3 * 0x100;
    *(undefined1 *)param_1[7] = 0xb;
    iVar2 = iVar5;
  }
  else {
    if (bVar1 < 8) {
      iVar2 = FUN_005be0a0(*(undefined4 *)(param_1[7] + 0x14),param_1,iVar2);
      if (iVar2 == -3) {
        *(undefined1 *)param_1[7] = 0xd;
        *(undefined4 *)(param_1[7] + 4) = 0;
        iVar2 = -3;
      }
      else {
        if (iVar2 == 0) {
          iVar2 = iVar5;
        }
        if (iVar2 != 1) {
          return iVar2;
        }
        FUN_005bdfca(*(undefined4 *)(param_1[7] + 0x14),param_1,param_1[7] + 4);
        if (*(int *)(param_1[7] + 0xc) == 0) {
          *(undefined1 *)param_1[7] = 8;
          iVar2 = iVar5;
          goto LAB_005bee02;
        }
        *(undefined1 *)param_1[7] = 0xc;
        iVar2 = iVar5;
      }
      goto LAB_005bebf4;
    }
    if (bVar1 == 10) goto LAB_005bee58;
    if (bVar1 < 10) goto LAB_005bee2a;
    if (bVar1 == 0xc) {
      return 1;
    }
    if (0xb < bVar1) {
      if (bVar1 != 0xd) {
        return -2;
      }
      return -3;
    }
  }
  if (param_1[1] == 0) {
    return iVar2;
  }
  param_1[1] = param_1[1] + -1;
  param_1[2] = param_1[2] + 1;
  pbVar3 = (byte *)*param_1;
  *param_1 = (int)(pbVar3 + 1);
  *(uint *)(param_1[7] + 8) = *(int *)(param_1[7] + 8) + (uint)*pbVar3;
  if (*(int *)(param_1[7] + 4) == *(int *)(param_1[7] + 8)) {
    *(undefined1 *)param_1[7] = 0xc;
    return 1;
  }
  *(undefined1 *)param_1[7] = 0xd;
  param_1[6] = DAT_005bf0a8;
  *(undefined4 *)(param_1[7] + 4) = 5;
  iVar2 = iVar5;
  goto LAB_005bebf4;
}

