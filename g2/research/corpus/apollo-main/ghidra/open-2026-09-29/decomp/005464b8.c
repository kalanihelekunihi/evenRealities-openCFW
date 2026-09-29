
undefined4 FUN_005464b8(void)

{
  char *pcVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 in_r3;
  
  pcVar1 = DAT_00546880;
  if (*DAT_00546880 == '\x01') {
    uVar6 = navigation_icon_name_for_code(*(undefined4 *)(DAT_00546880 + 4));
    FUN_00498680(*DAT_00546890,uVar6);
    FUN_0049942e(*DAT_00546894,pcVar1 + 8);
    FUN_0049942e(*DAT_00546898,pcVar1 + 0x48);
    puVar3 = DAT_005468a8;
    FUN_0049942e(*DAT_005468a8,pcVar1 + 0x88);
    puVar2 = DAT_005468a4;
    FUN_0049942e(*DAT_005468a4,pcVar1 + 200);
    puVar5 = DAT_005468fc;
    FUN_0049942e(*DAT_005468fc,pcVar1 + 0x148);
    puVar4 = DAT_005468ac;
    FUN_0049942e(*DAT_005468ac,pcVar1 + 0x108);
    FUN_0043f6b8(*puVar3,3,0,0);
    FUN_0043f6d6(*puVar2,*puVar3,0x11,0xfffffff0,0);
    if (*(int *)(pcVar1 + 0x188) == 1) {
      FUN_0043ded4(*puVar5,1);
    }
    else {
      FUN_0043dfa4(*puVar5,1);
      FUN_0043f6d6(*puVar5,*puVar2,0x11,0xfffffff0,0);
    }
    if (*(int *)(pcVar1 + 0x188) == 1) {
      FUN_0043f6d6(*puVar4,*puVar2,0x11,0xfffffff0,0);
    }
    else {
      FUN_0043f6d6(*puVar4,*puVar5,0x11,0xfffffff0,0);
    }
    puVar2 = DAT_00546900;
    FUN_0049942e(*DAT_00546900,pcVar1 + 0x88);
    puVar3 = DAT_00546904;
    FUN_0049942e(*DAT_00546904,pcVar1 + 200);
    FUN_0043f6b8(*puVar2,3,0,0);
    in_r3 = 0;
    FUN_0043f6d6(*puVar3,*puVar2,0x11,0xfffffff0);
    FUN_0043f66c(*DAT_00546888);
    FUN_0043f66c(*DAT_0054688c);
  }
  return in_r3;
}

