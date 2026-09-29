
void touch_packet_23a4_build_group(int param_1,int *param_2)

{
  undefined1 uVar1;
  undefined1 uVar2;
  char cVar3;
  undefined1 uVar4;
  ushort uVar5;
  undefined1 uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  ushort *puVar11;
  uint uVar12;
  int iVar13;
  int *piVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  int local_3c;
  
  iVar15 = param_2[5];
  iVar10 = param_2[2];
  uVar9 = 0;
  for (uVar7 = 0; uVar7 < *(ushort *)(*param_2 + 0xc); uVar7 = uVar7 + 1) {
    uVar9 = uVar9 | 1 << *(sbyte *)(iVar15 + 5);
    iVar15 = iVar15 + 8;
  }
  iVar15 = param_2[6];
  for (uVar7 = 0; uVar7 < *(byte *)(*param_2 + 0x2c); uVar7 = uVar7 + 1) {
    uVar9 = uVar9 | 1 << *(sbyte *)(iVar15 + 5);
    iVar15 = iVar15 + 8;
  }
  if (*(char *)(iVar10 + 0x75) == '\x02') {
    uVar1 = *(undefined1 *)(iVar10 + 100);
  }
  else if (*(char *)(iVar10 + 0x75) == '\x05') {
    uVar1 = *(undefined1 *)(iVar10 + 0x6d);
  }
  else {
    uVar1 = *(undefined1 *)(iVar10 + 99);
  }
  uVar2 = *(undefined1 *)(iVar10 + 100);
  uVar6 = uVar2;
  if (*(char *)(iVar10 + 0x74) != '\x02') {
    if (*(char *)(iVar10 + 0x74) == '\x04') {
      uVar6 = *(undefined1 *)(iVar10 + 0x6b);
    }
    else {
      uVar6 = *(undefined1 *)(iVar10 + 99);
    }
  }
  if (param_1 == 1) {
    iVar15 = param_2[0xb];
    local_3c = param_2[0xd];
    uVar7 = 4;
  }
  else {
    iVar15 = param_2[10];
    local_3c = param_2[0xc];
    uVar7 = 5;
  }
  for (uVar17 = 0; uVar17 < uVar7; uVar17 = uVar17 + 1) {
    touch_packet_2248_build_entry(param_1,uVar17,iVar15,param_2);
    puVar11 = (ushort *)(uVar17 * 4 + local_3c);
    uVar5 = puVar11[1];
    iVar13 = param_2[3] + (uint)*puVar11 * 0x90;
    cVar3 = *(char *)(iVar13 + 0x7a);
    uVar4 = uVar6;
    if ((cVar3 != '\x01') && (uVar4 = uVar2, cVar3 == '\x02')) {
      uVar4 = uVar1;
    }
    iVar16 = iVar15;
    if (param_1 == 1) {
      iVar16 = iVar15 + 0x14;
    }
    touch_record_1e88_mask3(uVar9,uVar4,iVar16);
    if (*(byte *)(*param_2 + 0x2c) != 0) {
      if (cVar3 == '\x01') {
        uVar4 = *(undefined1 *)(iVar10 + 0x6b);
      }
      uVar8 = 0;
      for (uVar12 = 0; uVar12 < *(byte *)(*param_2 + 0x2c); uVar12 = uVar12 + 1) {
        uVar8 = uVar8 | 1 << *(sbyte *)(param_2[6] + uVar12 * 8 + 5);
      }
      touch_record_1e88_mask3(uVar8,uVar4,iVar16);
    }
    if (cVar3 == '\x01') {
      piVar14 = (int *)(*(int *)(iVar13 + 8) + (uint)uVar5 * 8);
      uVar8 = 0;
      for (uVar12 = 0; uVar12 < *(byte *)((int)piVar14 + 5); uVar12 = uVar12 + 1) {
        uVar8 = uVar8 | 1 << *(sbyte *)(*piVar14 + uVar12 * 8 + 5);
      }
      touch_record_1e88_mask3(uVar8,*(undefined1 *)(iVar10 + 0x68),iVar16);
    }
    iVar15 = iVar16 + 0x18;
    if (param_1 != 1) {
      iVar15 = iVar16 + 0x1c;
    }
  }
  return;
}

