
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
hw_context_initialize_42e8d0(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  puVar1 = _DAT_0042f150;
  if (param_1 == 0) {
    if (param_2 == (int *)0x0) {
      uVar5 = 6;
    }
    else if ((int)(*_DAT_0042f150 << 7) < 0) {
      uVar5 = 7;
    }
    else {
      *_DAT_0042f150 = *_DAT_0042f150 | 0x1000000;
      *puVar1 = *puVar1 & 0xff000000 | 0xafafaf;
      puVar1[1] = 0;
      *_DAT_0042f154 = 0;
      *param_2 = (int)puVar1;
      piVar4 = _DAT_0042f160;
      piVar3 = _DAT_0042f15c;
      iVar2 = _DAT_0042f158;
      if (*_DAT_0042f15c == _DAT_0042f158) {
        *_DAT_0042f160 = _DAT_0042f15c[0xe];
        piVar4[1] = piVar3[0xf];
        piVar4[2] = piVar3[0x10];
        uVar6 = 0;
      }
      else {
        uVar8 = FUN_00421548(1,0x240,1,_DAT_0042f160);
        uVar7 = FUN_00421548(1,0x241,1,piVar4 + 1);
        uVar6 = FUN_00421548(1,0x242,1,piVar4 + 2);
        uVar6 = uVar6 | uVar8 | uVar7;
      }
      piVar4 = _DAT_0042f160;
      if ((((*_DAT_0042f160 == 0) || (_DAT_0042f160[1] == 0)) || (_DAT_0042f160[2] == 0)) ||
         (uVar6 != 0)) {
        *_DAT_0042f160 = _DAT_0042f164;
        piVar4[1] = _DAT_0042f168;
        piVar4[2] = _DAT_0042f16c;
        *(undefined1 *)(piVar4 + 3) = 0;
      }
      else {
        *(undefined1 *)(_DAT_0042f160 + 3) = 1;
      }
      piVar4 = _DAT_0042f170;
      if (*piVar3 == iVar2) {
        _DAT_0042f170[1] = piVar3[0x12];
        *piVar4 = piVar3[0x13];
        uVar7 = 0;
      }
      else {
        uVar8 = FUN_00421548(1,0x24a,1,_DAT_0042f170 + 1);
        uVar7 = FUN_00421548(1,0x24b,1,piVar4);
        uVar7 = uVar7 | uVar8;
      }
      *_DAT_0042f174 = *_DAT_0042f174 & 0xfffffffe;
      if (((_DAT_0042f170[1] == 0) || (*_DAT_0042f170 == 0)) || (uVar7 != 0)) {
        *_DAT_0042f178 = 0;
      }
      else {
        *_DAT_0042f178 = 1;
      }
      uVar5 = 0;
    }
  }
  else {
    uVar5 = 5;
  }
  return CONCAT44(param_4,uVar5);
}

