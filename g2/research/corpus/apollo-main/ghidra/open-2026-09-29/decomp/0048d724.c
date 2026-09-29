
uint FUN_0048d724(char *param_1,undefined4 *param_2,uint param_3,undefined4 *param_4)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  char cVar7;
  char *pcVar8;
  char *pcVar9;
  char *pcVar10;
  uint uVar11;
  uint uVar12;
  uint unaff_r11;
  bool bVar13;
  bool bVar14;
  
  pcVar8 = param_1;
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = 0;
  }
  while (iVar4 = FUN_004d58ae(*pcVar8), iVar2 = DAT_0048d7dc, iVar4 != 0) {
    pcVar8 = pcVar8 + 1;
  }
  cVar1 = *pcVar8;
  if (cVar1 == '-' || cVar1 == '+') {
    cVar7 = *pcVar8;
    pcVar8 = pcVar8 + 1;
  }
  else {
    cVar7 = '+';
  }
  if ((((int)param_3 < 0) || (param_3 == 1)) || (0x24 < (int)param_3)) {
    if (param_2 == (undefined4 *)0x0) {
      return 0;
    }
    *param_2 = param_1;
    return 0;
  }
  pcVar9 = pcVar8;
  if ((int)param_3 < 1) {
    if (*pcVar8 != '0') {
      param_3 = 10;
      goto LAB_0048d7ba;
    }
    if ((byte)(pcVar8[1] | 0x20U) != 0x78) {
      param_3 = 8;
      goto LAB_0048d7ba;
    }
    param_3 = 0x10;
  }
  else {
    bVar13 = param_3 == 0x10;
    if (bVar13) {
      cVar1 = *pcVar8;
    }
    bVar14 = bVar13 && cVar1 == '0';
    if (bVar13 && cVar1 == '0') {
      bVar14 = (byte)(pcVar8[1] | 0x20U) == 0x78;
    }
    if (!bVar14) goto LAB_0048d7ba;
  }
  pcVar8 = pcVar8 + 2;
  pcVar9 = pcVar8;
LAB_0048d7ba:
  for (; *pcVar8 == '0'; pcVar8 = pcVar8 + 1) {
  }
  iVar4 = (int)&DAT_0048d7dc + DAT_0048d7dc;
  pcVar10 = pcVar8;
  uVar3 = 0;
  uVar12 = 0;
  while( true ) {
    uVar11 = uVar3;
    uVar5 = FUN_004d58c2(*pcVar10);
    iVar6 = FUN_004d40e0(iVar2 + 0x48d804,uVar5,param_3);
    if (iVar6 == 0) break;
    unaff_r11 = iVar6 - (uint)(byte)((char)iVar4 + 0x28) & 0xff;
    pcVar10 = pcVar10 + 1;
    uVar3 = param_3 * uVar11 + unaff_r11;
    uVar12 = uVar11;
  }
  if (pcVar9 == pcVar10) {
    if (param_2 != (undefined4 *)0x0) {
      *param_2 = param_1;
    }
    return 0;
  }
  if (((int)(pcVar10 + (-(uint)*(byte *)(iVar4 + param_3) - (int)pcVar8)) < 0) ||
     ((((int)(pcVar10 + (-(uint)*(byte *)(iVar4 + param_3) - (int)pcVar8)) < 1 &&
       (unaff_r11 <= uVar11)) && ((uVar11 - unaff_r11) / param_3 == uVar12)))) {
    if (cVar7 == '-') {
      uVar11 = -uVar11;
    }
  }
  else {
    FUN_00439cb2();
    if (param_4 != (undefined4 *)0x0) {
      *param_4 = 1;
    }
    uVar11 = 0xffffffff;
  }
  if (param_2 != (undefined4 *)0x0) {
    *param_2 = pcVar10;
    return uVar11;
  }
  return uVar11;
}

