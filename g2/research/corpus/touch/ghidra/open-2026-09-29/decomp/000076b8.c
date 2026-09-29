
uint touch_sub_43b8(int param_1,int param_2)

{
  char cVar1;
  bool bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  ushort *puVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  
  iVar9 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
  cVar1 = *(char *)(iVar9 + 0x7a);
  uVar3 = touch_sub_2c6a(param_1,0,param_2);
  bVar2 = false;
  uVar8 = 0;
  uVar7 = 0;
  do {
    if (*(ushort *)(iVar9 + 0x38) <= uVar8) {
      return uVar7;
    }
    if (cVar1 == '\x01') {
      bVar2 = true;
    }
    puVar6 = (ushort *)(*(int *)(iVar9 + 4) + uVar8 * 10);
    *(undefined1 *)((int)puVar6 + 9) = 0;
    touch_sub_2bcc(param_1,0,param_2);
    for (uVar5 = 0x80; uVar5 != 0; uVar5 = uVar5 >> 1) {
      *(byte *)((int)puVar6 + 9) = *(byte *)((int)puVar6 + 9) | (byte)uVar5;
      touch_sub_2bcc(param_1,2,param_2);
      uVar4 = touch_sub_422e(param_1,param_2);
      uVar7 = uVar7 | uVar4;
      touch_state_2902_cap_enabled_object(param_1,param_2);
      if (uVar7 != 0) break;
      if (((bVar2) && (*puVar6 < uVar3)) || ((!bVar2 && (uVar3 <= *puVar6)))) {
        *(byte *)((int)puVar6 + 9) = ~(byte)uVar5 & *(byte *)((int)puVar6 + 9);
      }
    }
    uVar8 = uVar8 + 1;
  } while( true );
}

