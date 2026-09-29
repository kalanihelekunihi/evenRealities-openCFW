
undefined4 HciDrvRadioBoot(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined1 uVar3;
  char cVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 local_60;
  undefined4 local_5c;
  undefined1 auStack_58 [5];
  undefined1 auStack_53 [3];
  undefined1 auStack_50 [56];
  undefined4 uStack_18;
  
  puVar2 = DAT_004b4d74;
  local_60 = DAT_004b4d70;
  local_5c = 0x40;
  uStack_18 = param_4;
  uVar5 = FUN_0052dd94(6,&local_60,DAT_004b4d74,DAT_004b4d78);
  uVar3 = FUN_0052deee();
  FUN_004733ee(DAT_004b4d7c,uVar5,uVar3);
  FUN_00491102(100);
  iVar6 = FUN_0052deee();
  if (iVar6 != 0) {
    FUN_004733ee(DAT_004b4d80);
    *DAT_004b4d6c = '\x01';
  }
  FUN_0052f38c();
  puVar1 = DAT_004b4d60;
  iVar6 = FUN_0052fcfc(DAT_004b4d60);
  if (iVar6 != 0) {
    uVar7 = FUN_0052dee6();
    cVar4 = FUN_004b47cc(uVar7,*puVar1);
    if ((cVar4 != '\0') || (*DAT_004b4d6c != '\0')) {
      FUN_0052fb58();
      FUN_0052f38c();
      FUN_004b480a(*puVar2);
      FUN_0052f38c();
      FUN_0052fc04();
      *DAT_004b4d6c = '\0';
    }
  }
  *DAT_004b4d84 = 0;
  *DAT_004b4d88 = 0;
  FUN_0053006c(DAT_004b4d90,DAT_004b4d8c,0x104,0x820);
  *DAT_004b4d94 = 0;
  if (param_1 != '\0') {
    FUN_00480d72(1,auStack_58);
    iVar6 = DAT_004b4d98;
    auStack_53._0_2_ = auStack_53._1_2_;
    FUN_00439be4(DAT_004b4d98,auStack_50,4);
    *(char *)(iVar6 + 4) = (char)auStack_53._0_2_;
    *(char *)(iVar6 + 5) = SUB21(auStack_53._0_2_,1);
    *(byte *)(iVar6 + 5) = *(byte *)(iVar6 + 5) & 0xfc;
  }
  FUN_0048162c(0,0x75,0x4b4a99,0);
  FUN_0052dd58();
  FUN_004b4786(0x3b,4);
  FUN_004b4768(0x3b);
  return uVar5;
}

