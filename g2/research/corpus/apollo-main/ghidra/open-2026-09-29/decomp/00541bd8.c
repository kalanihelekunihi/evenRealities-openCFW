
undefined8 FUN_00541bd8(char *param_1,undefined4 *param_2,uint param_3,undefined4 *param_4)

{
  char cVar1;
  ulonglong uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  char *pcVar12;
  char *pcVar13;
  char *pcVar14;
  bool bVar15;
  bool bVar16;
  longlong lVar17;
  char local_40;
  
  pcVar12 = param_1;
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = 0;
  }
  while (iVar4 = FUN_004d58ae(*pcVar12), iVar3 = DAT_00541cb8, iVar4 != 0) {
    pcVar12 = pcVar12 + 1;
  }
  cVar1 = *pcVar12;
  if (cVar1 == '-' || cVar1 == '+') {
    local_40 = *pcVar12;
    pcVar12 = pcVar12 + 1;
    cVar1 = local_40;
  }
  else {
    local_40 = '+';
  }
  if ((((int)param_3 < 0) || (param_3 == 1)) || (0x24 < (int)param_3)) {
    if (param_2 != (undefined4 *)0x0) {
      *param_2 = param_1;
    }
  }
  else {
    pcVar13 = pcVar12;
    if ((int)param_3 < 1) {
      if (*pcVar12 == '0') {
        if ((byte)(pcVar12[1] | 0x20U) == 0x78) {
          param_3 = 0x10;
          goto LAB_00541c76;
        }
        param_3 = 8;
      }
      else {
        param_3 = 10;
      }
    }
    else {
      bVar15 = param_3 == 0x10;
      if (bVar15) {
        cVar1 = *pcVar12;
      }
      bVar16 = bVar15 && cVar1 == '0';
      if (bVar15 && cVar1 == '0') {
        bVar16 = (byte)(pcVar12[1] | 0x20U) == 0x78;
      }
      if (bVar16) {
LAB_00541c76:
        pcVar12 = pcVar12 + 2;
        pcVar13 = pcVar12;
      }
    }
    for (; *pcVar12 == '0'; pcVar12 = pcVar12 + 1) {
    }
    cVar1 = (char)DAT_00541cb8;
    uVar11 = 0;
    uVar9 = 0;
    uVar10 = 0;
    uVar6 = 0;
    uVar7 = 0;
    pcVar14 = pcVar12;
    while( true ) {
      uVar5 = FUN_004d58c2(*pcVar14);
      iVar4 = FUN_004d40e0(iVar3 + 0x541ce0,uVar5,param_3);
      if (iVar4 == 0) break;
      uVar11 = iVar4 - (uint)(byte)(cVar1 - 0x20) & 0xff;
      uVar2 = (ulonglong)uVar6;
      uVar8 = (uint)(param_3 * uVar2);
      iVar4 = ((int)param_3 >> 0x1f) * uVar6;
      pcVar14 = pcVar14 + 1;
      uVar9 = uVar6;
      uVar10 = uVar7;
      uVar6 = uVar8 + uVar11;
      uVar7 = iVar4 + param_3 * uVar7 + (int)(param_3 * uVar2 >> 0x20) + (uint)CARRY4(uVar8,uVar11);
    }
    if (pcVar13 != pcVar14) {
      if ((int)(pcVar14 + (-(uint)*(byte *)((int)&DAT_00541cb8 + param_3 + iVar3) - (int)pcVar12)) <
          0) {
LAB_00541d64:
        if (local_40 == '-') {
          bVar15 = uVar6 != 0;
          uVar6 = -uVar6;
          uVar7 = -uVar7 - (uint)bVar15;
        }
      }
      else {
        if ((int)(pcVar14 + (-(uint)*(byte *)((int)&DAT_00541cb8 + param_3 + iVar3) - (int)pcVar12))
            < 1) {
          uVar8 = uVar7 - (uVar6 < uVar11);
          if (((uVar8 <= uVar7) && ((uVar8 < uVar7 || (uVar6 - uVar11 <= uVar6)))) &&
             (lVar17 = FUN_0047cc60(), lVar17 == CONCAT44(uVar10,uVar9))) goto LAB_00541d64;
        }
        FUN_00439cb2();
        if (param_4 != (undefined4 *)0x0) {
          *param_4 = 1;
        }
        uVar6 = 0xffffffff;
        uVar7 = 0xffffffff;
      }
      if (param_2 != (undefined4 *)0x0) {
        *param_2 = pcVar14;
      }
      goto LAB_00541d7e;
    }
    if (param_2 != (undefined4 *)0x0) {
      *param_2 = param_1;
    }
  }
  uVar6 = 0;
  uVar7 = 0;
LAB_00541d7e:
  return CONCAT44(uVar7,uVar6);
}

