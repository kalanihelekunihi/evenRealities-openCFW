
uint touch_sub_40f6(uint param_1,int param_2)

{
  ushort uVar1;
  bool bVar2;
  uint uVar3;
  int extraout_r1;
  int extraout_r1_00;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int *piVar10;
  uint uVar11;
  bool bVar12;
  
  piVar10 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
  uVar1 = *(ushort *)(*piVar10 + 0xe);
  bVar12 = *(char *)((int)piVar10 + 0x7b) == '\a';
  if (bVar12) {
    iVar8 = *(int *)(param_2 + 0x34);
    uVar5 = 4;
  }
  else {
    iVar8 = *(int *)(param_2 + 0x30);
    uVar5 = 5;
  }
  for (uVar4 = 0; uVar4 < *(ushort *)(piVar10 + 0xe); uVar4 = uVar4 + 1) {
    *(undefined1 *)(piVar10[1] + uVar4 * 10 + 9) = 0xff;
  }
  touch_sub_2bcc(param_1,1,param_2);
  *(undefined2 *)(*piVar10 + 0x10) = *(undefined2 *)(*piVar10 + 0xe);
  uVar4 = touch_sub_2c6a(param_1,0,param_2);
  uVar9 = uVar1 + 1;
  uVar11 = 0;
  do {
    uVar9 = uVar9 - 1;
    iVar7 = *piVar10;
    __aeabi_uidivmod(*(undefined2 *)(iVar7 + 0xe),uVar9);
    if ((extraout_r1 == 0) &&
       (__aeabi_uidivmod(*(undefined2 *)(iVar7 + 0x10),uVar9), extraout_r1_00 == 0)) {
      *(short *)(iVar7 + 0x36) = (short)uVar9;
      touch_sub_2e70(param_1,param_2);
      for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1) {
        if (*(ushort *)(iVar8 + uVar6 * 4) == param_1) {
          uVar3 = touch_sub_3ff8(bVar12,uVar6,param_2);
          uVar11 = uVar11 | uVar3;
          uVar3 = (uint)*(ushort *)(iVar8 + uVar6 * 4 + 2);
          touch_state_2956_cap_enabled_record(param_1,uVar3,param_2);
          uVar3 = (uint)*(ushort *)(piVar10[1] + uVar3 * 10);
          if (*(char *)((int)piVar10 + 0x7a) == '\x01') {
            if (uVar4 < uVar3) {
              bVar2 = true;
              goto LAB_000074de;
            }
          }
          else if (uVar3 <= uVar4) {
            bVar2 = true;
            goto LAB_000074de;
          }
        }
      }
      bVar2 = false;
LAB_000074de:
      if (!bVar2) {
        return uVar11;
      }
    }
    if (uVar9 < 4) {
      return uVar11;
    }
    if (uVar11 != 0) {
      return uVar11;
    }
  } while( true );
}

