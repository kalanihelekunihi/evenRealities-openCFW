
void FUN_005b82e4(int param_1,int param_2)

{
  char *pcVar1;
  int *piVar2;
  int *piVar3;
  undefined *puVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  undefined1 auStack_2c [12];
  undefined1 auStack_20 [12];
  
  FUN_0043c0e4(auStack_20,10,0);
  FUN_0043c0e4(auStack_2c,10,0);
  puVar5 = PTR_DAT_005b89a8;
  puVar4 = PTR_s__1d__1d_005b89a0;
  pcVar1 = DAT_005b8734;
  if (*DAT_005b8734 == '\0') {
    FUN_004b4728(auStack_20,PTR_s__1d__1d_005b89a0,param_1 / 10,param_1 % 10);
    FUN_004b4728(auStack_2c,puVar4,param_2 / 10,param_2 % 10);
  }
  else {
    FUN_004b4728(auStack_20,PTR_DAT_005b89a8,param_1);
    FUN_004b4728(auStack_2c,puVar5,param_2);
  }
  piVar2 = DAT_005b8998;
  if ((*DAT_005b8998 != 0) && (iVar7 = FUN_0043e2ea(*DAT_005b8998), iVar7 == 1)) {
    FUN_0049942e(*piVar2,auStack_20);
  }
  piVar3 = DAT_005b899c;
  if ((*DAT_005b899c != 0) && (iVar7 = FUN_0043e2ea(*DAT_005b899c), iVar7 == 1)) {
    FUN_0049942e(*piVar3,auStack_2c);
  }
  piVar6 = DAT_005b89b0;
  if (*pcVar1 == '\x01') {
    if ((((*DAT_005b89b0 != 0) && (iVar7 = FUN_0043e2ea(*DAT_005b89b0), iVar7 == 1)) &&
        (*piVar2 != 0)) && (iVar7 = FUN_0043e2ea(*piVar2), iVar7 == 1)) {
      FUN_0043f6d6(*piVar6,*piVar2,0x14,6,0);
    }
    if (((*piVar3 != 0) && (iVar7 = FUN_0043e2ea(*piVar3), iVar7 == 1)) &&
       ((*piVar6 != 0 && (iVar7 = FUN_0043e2ea(*piVar6), iVar7 == 1)))) {
      FUN_0043f6d6(*piVar3,*piVar6,0x14,6,0);
    }
  }
  return;
}

