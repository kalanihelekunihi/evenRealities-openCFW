
uint touch_sub_4684(uint param_1,int param_2)

{
  ushort uVar1;
  undefined1 uVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  uint uVar8;
  
  if (param_2 == 0) {
    uVar8 = 1;
  }
  else if (param_1 < 3) {
    iVar3 = touch_sub_4ade();
    if (iVar3 == 0) {
      uVar8 = 1;
    }
    else {
      piVar4 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
      iVar3 = *piVar4;
      uVar1 = *(ushort *)((int)piVar4 + 0x8e);
      uVar8 = (uint)uVar1;
      *(uint *)(*(int *)(param_2 + 4) + 8) = *(uint *)(*(int *)(param_2 + 4) + 8) | 0x2000;
      if ((uVar8 & 3) != 1) {
        *(undefined1 *)(iVar3 + 0x2e) = 0;
        *(undefined1 *)(iVar3 + 0x2f) = 0;
      }
      if ((uVar8 & 0xc) != 4) {
        *(undefined1 *)(iVar3 + 0x30) = 0;
        *(undefined1 *)(iVar3 + 0x31) = 0;
      }
      if ((uVar8 & 0x30) != 0x10) {
        for (uVar7 = 0; uVar7 < *(ushort *)(piVar4 + 0xe); uVar7 = uVar7 + 1) {
          *(undefined1 *)(piVar4[1] + uVar7 * 10 + 9) = 0;
        }
      }
      touch_sub_2bcc(param_1,2,param_2);
      touch_sub_2b64(param_1,param_2);
      if ((int)(uVar8 << 0x1e) < 0) {
        uVar7 = touch_sub_437c(param_1,param_2);
        touch_sub_2b64(param_1,param_2);
      }
      else {
        uVar7 = 0;
      }
      if ((int)(uVar8 << 0x1c) < 0) {
        uVar5 = touch_sub_439a(param_1,param_2);
        uVar7 = uVar7 | uVar5;
        touch_sub_2b64(param_1,param_2);
      }
      if ((uVar1 & 10) != 0) {
        uVar5 = touch_sub_449e(param_1,param_2);
        uVar7 = uVar7 | uVar5;
      }
      uVar6 = uVar1 >> 8 & 7;
      uVar2 = __aeabi_uidiv(*(undefined1 *)(iVar3 + 0x2e),uVar6);
      *(undefined1 *)(iVar3 + 0x2e) = uVar2;
      uVar2 = __aeabi_uidiv(*(undefined1 *)(iVar3 + 0x2f),uVar6);
      *(undefined1 *)(iVar3 + 0x2f) = uVar2;
      touch_sub_2b64(param_1,param_2);
      if ((int)(uVar8 << 0x18) < 0) {
        uVar5 = touch_sub_40f6(param_1,param_2);
        uVar7 = uVar7 | uVar5;
      }
      if ((int)(uVar8 << 0x1a) < 0) {
        uVar8 = touch_sub_43b8(param_1,param_2);
        uVar7 = uVar7 | uVar8;
      }
      touch_sub_2bcc(param_1,2,param_2);
      if ((uVar1 & 0xaa) != 0) {
        uVar8 = touch_sub_4538(param_1,param_2);
        uVar7 = uVar7 | uVar8;
      }
      uVar8 = 0;
      if (uVar7 != 0) {
        uVar8 = uVar7 | 0x100;
      }
      *(uint *)(*(int *)(param_2 + 4) + 8) = *(uint *)(*(int *)(param_2 + 4) + 8) & DAT_00007b10;
      event_dispatcher(0,param_2);
    }
  }
  else {
    uVar8 = 1;
  }
  return uVar8;
}

