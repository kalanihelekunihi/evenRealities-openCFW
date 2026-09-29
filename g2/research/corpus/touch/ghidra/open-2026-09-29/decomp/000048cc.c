
void touch_select_15cc_peak(undefined4 *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  uVar8 = (uint)*(ushort *)(param_2 + 0x38);
  if (uVar8 < 3) {
    uVar8 = 3;
  }
  uVar4 = *(uint *)(param_2 + 0x30);
  if ((uVar4 & 3) == 1) {
    iVar7 = *(int *)(param_2 + 4);
    uVar1 = 0;
    iVar2 = iVar7;
    for (uVar5 = 0; uVar5 < uVar8; uVar5 = uVar5 + 1) {
      if (uVar1 < *(ushort *)(iVar2 + 4)) {
        uVar1 = (uint)*(ushort *)(iVar2 + 4);
      }
      iVar2 = iVar2 + 10;
    }
    iVar2 = 0;
    uVar5 = 0;
    uVar11 = DAT_000049d0;
    for (uVar6 = 0; uVar6 < uVar8; uVar6 = uVar6 + 1) {
      if (*(ushort *)(iVar7 + 4) == uVar1) {
        if (uVar6 == 0) {
          uVar9 = 0;
        }
        else {
          uVar9 = (uint)*(ushort *)(iVar7 + -6);
        }
        if (uVar6 < uVar8 - 1) {
          uVar10 = (uint)*(ushort *)(iVar7 + 0xe);
        }
        else {
          uVar10 = 0;
        }
        uVar3 = *(ushort *)(iVar7 + 4) + uVar9 + uVar10;
        if (uVar5 < uVar3) {
          iVar2 = uVar10 - uVar9;
          uVar5 = uVar3;
          uVar11 = uVar6;
        }
      }
      iVar7 = iVar7 + 10;
    }
    if ((uVar11 == DAT_000049d0) || (uVar5 == 0)) {
      *(undefined1 *)(param_1 + 1) = 0;
    }
    else {
      iVar7 = (uint)*(ushort *)(param_2 + 0x34) << 8;
      uVar1 = uVar4 & 0x100;
      if ((uVar4 & 0x100) == 0) {
        uVar8 = __aeabi_uidiv(iVar7,uVar8 - 1);
      }
      else {
        uVar8 = __aeabi_uidiv(iVar7,uVar8);
        uVar1 = uVar8 >> 1;
      }
      iVar2 = __aeabi_idiv(uVar8 * iVar2,uVar5);
      *(undefined1 *)(param_1 + 1) = 1;
      *(short *)*param_1 = (short)(iVar2 + uVar8 * uVar11 + uVar1 + 0x7f >> 8);
    }
  }
  return;
}

