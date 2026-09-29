
uint touch_sub_4538(int param_1,int *param_2)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  ushort *puVar9;
  uint uVar10;
  uint uVar11;
  uint local_30;
  
  iVar7 = param_2[3] + param_1 * 0x90;
  cVar1 = *(char *)(iVar7 + 0x7b);
  local_30 = 0;
  for (uVar10 = (uint)*(ushort *)(iVar7 + 0x80);
      uVar10 < (uint)*(ushort *)(iVar7 + 0x80) + (uint)*(ushort *)(iVar7 + 0x82);
      uVar10 = uVar10 + 1) {
    uVar8 = touch_sub_3ff8(cVar1 == '\a',uVar10,param_2);
    local_30 = local_30 | uVar8;
  }
  touch_state_2902_cap_enabled_object(param_1,param_2);
  if (local_30 == 0) {
    iVar3 = 0;
    if (*(char *)(iVar7 + 0x7a) == '\x01') {
      uVar10 = (uint)*(byte *)(param_2[2] + 0x57);
      uVar8 = (uint)*(byte *)(*param_2 + 0x30);
      if (uVar8 < uVar10) {
        iVar3 = uVar10 - uVar8;
      }
    }
    else {
      local_30 = 1;
      uVar10 = 0;
      uVar8 = 0;
    }
    uVar10 = uVar10 + uVar8;
    if (100 < uVar10) {
      uVar10 = 100;
    }
    iVar5 = param_2[4] + param_1 * 0x3c;
    uVar6 = (uint)*(ushort *)(iVar5 + 4);
    puVar9 = *(ushort **)(iVar7 + 4);
    uVar8 = 0;
    if (*(char *)(iVar7 + 0x7a) == '\x01') {
      for (; uVar11 = (uint)*(byte *)(iVar7 + 0x3a), uVar8 < uVar11; uVar8 = uVar8 + 1) {
        uVar2 = *puVar9;
        uVar4 = __aeabi_uidiv(iVar3 * uVar6,100);
        if ((uVar2 < uVar4) || (uVar4 = __aeabi_uidiv(uVar10 * uVar6,100), uVar4 < uVar2)) {
          local_30 = local_30 | 0x400;
          break;
        }
        puVar9 = puVar9 + 5;
      }
      uVar8 = (uint)*(ushort *)(iVar5 + 6);
      for (; uVar11 < *(ushort *)(iVar7 + 0x38); uVar11 = uVar11 + 1) {
        uVar2 = *puVar9;
        uVar6 = __aeabi_uidiv(iVar3 * uVar8,100);
        if ((uVar2 < uVar6) || (uVar6 = __aeabi_uidiv(uVar10 * uVar8,100), uVar6 < uVar2)) {
          return local_30 | 0x400;
        }
        puVar9 = puVar9 + 5;
      }
    }
    else {
      local_30 = local_30 | 1;
    }
  }
  return local_30;
}

