
undefined8 FUN_0055d94c(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  puVar1 = DAT_0055e1cc;
  if (param_1 == 0) {
    if (param_2 == (int *)0x0) {
      uVar5 = 6;
    }
    else if ((int)(*DAT_0055e1cc << 7) < 0) {
      uVar5 = 7;
    }
    else {
      *DAT_0055e1cc = *DAT_0055e1cc | 0x1000000;
      *puVar1 = *puVar1 & 0xff000000 | 0xafafaf;
      puVar1[1] = 0;
      *DAT_0055e1d0 = 0;
      *param_2 = (int)puVar1;
      piVar4 = DAT_0055e1dc;
      piVar3 = DAT_0055e1d8;
      iVar2 = DAT_0055e1d4;
      if (*DAT_0055e1d8 == DAT_0055e1d4) {
        *DAT_0055e1dc = DAT_0055e1d8[0xe];
        piVar4[1] = piVar3[0xf];
        piVar4[2] = piVar3[0x10];
        uVar6 = 0;
      }
      else {
        uVar8 = FUN_004d3f3c(1,0x240,1,DAT_0055e1dc);
        uVar7 = FUN_004d3f3c(1,0x241,1,piVar4 + 1);
        uVar6 = FUN_004d3f3c(1,0x242,1,piVar4 + 2);
        uVar6 = uVar6 | uVar8 | uVar7;
      }
      piVar4 = DAT_0055e1dc;
      if ((((*DAT_0055e1dc == 0) || (DAT_0055e1dc[1] == 0)) || (DAT_0055e1dc[2] == 0)) ||
         (uVar6 != 0)) {
        *DAT_0055e1dc = DAT_0055e1e0;
        piVar4[1] = DAT_0055e1e4;
        piVar4[2] = DAT_0055e1e8;
        *(undefined1 *)(piVar4 + 3) = 0;
      }
      else {
        *(undefined1 *)(DAT_0055e1dc + 3) = 1;
      }
      piVar4 = DAT_0055e1ec;
      if (*piVar3 == iVar2) {
        DAT_0055e1ec[1] = piVar3[0x12];
        *piVar4 = piVar3[0x13];
        uVar7 = 0;
      }
      else {
        uVar8 = FUN_004d3f3c(1,0x24a,1,DAT_0055e1ec + 1);
        uVar7 = FUN_004d3f3c(1,0x24b,1,piVar4);
        uVar7 = uVar7 | uVar8;
      }
      *DAT_0055e1f0 = *DAT_0055e1f0 & 0xfffffffe;
      if (((DAT_0055e1ec[1] == 0) || (*DAT_0055e1ec == 0)) || (uVar7 != 0)) {
        *DAT_0055e1f4 = 0;
      }
      else {
        *DAT_0055e1f4 = 1;
      }
      uVar5 = 0;
    }
  }
  else {
    uVar5 = 5;
  }
  return CONCAT44(param_4,uVar5);
}

