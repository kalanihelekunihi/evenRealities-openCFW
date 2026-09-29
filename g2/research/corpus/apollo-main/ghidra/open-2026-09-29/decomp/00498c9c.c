
void FUN_00498c9c(undefined4 param_1,int *param_2)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  undefined1 auStack_2c [8];
  undefined1 auStack_24 [16];
  
  iVar3 = FUN_00450286(param_2);
  cVar1 = FUN_004516f8(DAT_004991cc,param_2);
  if (cVar1 == '\x01') {
    iVar4 = *param_2;
    FUN_00498b82(iVar4,auStack_2c);
    if (iVar3 == 0x32) {
      if ((*(byte *)(iVar4 + 0x58) & 3) == 2) {
        FUN_00498680(iVar4,*(undefined4 *)(iVar4 + 0x2c));
      }
      else {
        FUN_00452d42(iVar4);
      }
    }
    else if (iVar3 == 0x1b) {
      piVar5 = (int *)param_2[4];
      if (((*(int *)(iVar4 + 0x44) != 0) || (*(int *)(iVar4 + 0x48) != 0x100)) ||
         (*(int *)(iVar4 + 0x4c) != 0x100)) {
        iVar3 = FUN_0043fd9e(iVar4);
        iVar6 = FUN_0043fdda(iVar4);
        FUN_00488cda(&local_3c,iVar3,iVar6,*(undefined4 *)(iVar4 + 0x44),
                     *(uint *)(iVar4 + 0x48) & 0xffff,*(uint *)(iVar4 + 0x4c) & 0xffff,auStack_2c);
        if (-local_3c < *piVar5) {
          local_3c = *piVar5;
        }
        else {
          local_3c = -local_3c;
        }
        *piVar5 = local_3c;
        if (-local_38 < *piVar5) {
          local_38 = *piVar5;
        }
        else {
          local_38 = -local_38;
        }
        *piVar5 = local_38;
        if (local_34 - iVar3 < *piVar5) {
          local_34 = *piVar5;
        }
        else {
          local_34 = local_34 - iVar3;
        }
        *piVar5 = local_34;
        if (local_30 - iVar6 < *piVar5) {
          local_30 = *piVar5;
        }
        else {
          local_30 = local_30 - iVar6;
        }
        *piVar5 = local_30;
      }
    }
    else if (iVar3 == 0x31) {
      if (((*(uint *)(iVar4 + 0x58) & 0xfff) >> 8 == 0xb) &&
         (((FUN_004992cc(iVar4), *(int *)(iVar4 + 0x44) != 0 || (*(int *)(iVar4 + 0x48) != 0x100))
          || (*(int *)(iVar4 + 0x4c) != 0x100)))) {
        FUN_00452d42(iVar4);
      }
    }
    else if (iVar3 == 0x16) {
      puVar7 = (undefined4 *)param_2[4];
      iVar3 = FUN_0043fd9e(iVar4);
      if (((*(int *)(iVar4 + 0x3c) == iVar3) &&
          (iVar3 = FUN_0043fdda(iVar4), *(int *)(iVar4 + 0x40) == iVar3)) &&
         (((*(int *)(iVar4 + 0x48) != 0x100 ||
           ((*(int *)(iVar4 + 0x4c) != 0x100 || (*(int *)(iVar4 + 0x44) != 0)))) ||
          ((*(int *)(iVar4 + 0x50) != *(int *)(iVar4 + 0x3c) / 2 ||
           (*(int *)(iVar4 + 0x54) != *(int *)(iVar4 + 0x40) / 2)))))) {
        uVar8 = FUN_0043fd9e(iVar4);
        uVar9 = FUN_0043fdda(iVar4);
        FUN_00488cda(&local_4c,uVar8,uVar9,*(undefined4 *)(iVar4 + 0x44),
                     *(uint *)(iVar4 + 0x48) & 0xffff,*(uint *)(iVar4 + 0x4c) & 0xffff,auStack_2c);
        local_4c = *(int *)(iVar4 + 0x14) + local_4c;
        local_48 = *(int *)(iVar4 + 0x18) + local_48;
        local_44 = *(int *)(iVar4 + 0x14) + local_44;
        local_40 = *(int *)(iVar4 + 0x18) + local_40;
        uVar2 = FUN_00450dd4(&local_4c,*puVar7,0);
        *(undefined1 *)(puVar7 + 1) = uVar2;
        return;
      }
      FUN_004408b0(iVar4,auStack_24);
      uVar2 = FUN_00450dd4(auStack_24,*puVar7,0);
      *(undefined1 *)(puVar7 + 1) = uVar2;
    }
    else if (iVar3 == 0x34) {
      puVar7 = (undefined4 *)param_2[4];
      *puVar7 = *(undefined4 *)(iVar4 + 0x3c);
      puVar7[1] = *(undefined4 *)(iVar4 + 0x40);
    }
    else if (((iVar3 == 0x1d) || (iVar3 == 0x20)) || (iVar3 == 0x1a)) {
      FUN_00498ec0(param_2);
    }
  }
  return;
}

