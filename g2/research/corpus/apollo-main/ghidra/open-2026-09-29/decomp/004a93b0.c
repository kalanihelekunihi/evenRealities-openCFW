
void ui_onboarding_main_sub_004A93B0
               (undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  byte bVar4;
  int iVar5;
  undefined4 uVar6;
  double dVar7;
  undefined1 auStack_2c [12];
  undefined1 auStack_20 [12];
  undefined4 uStack_14;
  
  puVar1 = DAT_004a9e40;
  uStack_14 = param_4;
  if (param_2 != 0) {
    FUN_0043c0e4(DAT_004a9e40,0x38,0);
    FUN_00439be4(puVar1,param_1,0x38);
    puVar2 = DAT_004a9e44;
    uVar6 = puVar1[1];
    *DAT_004a9e44 = *puVar1;
    puVar2[1] = uVar6;
    *(undefined2 *)(puVar2 + 2) = *(undefined2 *)(puVar1 + 2);
    *(undefined2 *)((int)puVar2 + 10) = *(undefined2 *)((int)puVar1 + 10);
    if (6 < *(ushort *)((int)puVar2 + 10)) {
      *(undefined2 *)((int)puVar2 + 10) = 6;
    }
    for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)((int)puVar2 + 10); iVar5 = iVar5 + 1) {
      *(undefined2 *)((int)puVar2 + iVar5 * 2 + 0xc) =
           *(undefined2 *)((int)puVar1 + iVar5 * 2 + 0xc);
    }
    *(undefined2 *)(puVar2 + 6) = *(undefined2 *)(puVar1 + 6);
    if (6 < *(ushort *)(puVar2 + 6)) {
      *(undefined2 *)(puVar2 + 6) = 6;
    }
    for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)(puVar2 + 6); iVar5 = iVar5 + 1) {
      *(undefined1 *)((int)puVar2 + iVar5 + 0x1a) = *(undefined1 *)((int)puVar1 + iVar5 + 0x1a);
    }
    FUN_00439c04(puVar2 + 8,puVar1 + 8,0x18);
  }
  puVar2 = DAT_004a9ed0;
  osMutexAcquire(*DAT_004a9ed0,0xffffffff);
  puVar1 = DAT_004a9e44;
  iVar5 = FUN_0050f810(*(undefined2 *)((int)DAT_004a9e44 + 0x2a));
  osMutexRelease(*puVar2);
  if (iVar5 != 0) {
    FUN_00498680(*DAT_004a9ed4,iVar5);
  }
  FUN_0043c0e4(auStack_2c,10,0);
  osMutexAcquire(*puVar2,0xffffffff);
  if (*(char *)(puVar1 + 8) == '\0') {
    FUN_0044b728(auStack_2c,10,&DAT_004a96c4,&DAT_004a96c0);
  }
  else if (*(short *)(puVar1 + 10) == 1) {
    FUN_004b4728(auStack_2c,DAT_004a9ed8,SUB84((double)(float)puVar1[9],0),
                 (int)((ulonglong)(double)(float)puVar1[9] >> 0x20));
  }
  else {
    dVar7 = DAT_004a96d0 + (double)(float)puVar1[9] * DAT_004a96c8;
    FUN_004b4728(auStack_2c,DAT_004a9f6c,SUB84(dVar7,0),(int)((ulonglong)dVar7 >> 0x20));
  }
  osMutexRelease(*puVar2);
  piVar3 = DAT_004a9f70;
  if (*DAT_004a9f70 != 0) {
    FUN_0049942e(*DAT_004a9f70,auStack_2c);
    FUN_0043f6d6(*piVar3,*DAT_004a9ed4,0x14,8,0);
  }
  FUN_0043c0e4(auStack_20,10,0);
  uVar6 = ui_common_api_fn_00509f86();
  FUN_0044b728(auStack_20,10,&DAT_004a96d8,uVar6);
  piVar3 = DAT_004a9f74;
  if (*DAT_004a9f74 != 0) {
    FUN_0049942e(*DAT_004a9f74,auStack_20);
    FUN_0043f6d6(*piVar3,*DAT_004aa14c,0xf,0,0xea);
    if (*DAT_004a9f78 != 0) {
      FUN_0043f6d6(*DAT_004a9f78,*piVar3,0x11,0xfffffff8,0);
    }
  }
  bVar4 = ui_common_api_fn_00509f8e();
  if (bVar4 < 0xb) {
    FUN_00498680(*DAT_004aa14c,DAT_004a9f7c);
  }
  else if (bVar4 - 0xb < 0x14) {
    FUN_00498680(*DAT_004aa14c,DAT_004a9f80);
  }
  else if (bVar4 - 0x1f < 0x14) {
    FUN_00498680(*DAT_004aa14c,DAT_004aa030);
  }
  else if (bVar4 - 0x33 < 0x1e) {
    FUN_00498680(*DAT_004aa14c,DAT_004aa034);
  }
  else if (0x50 < bVar4) {
    FUN_00498680(*DAT_004aa14c,DAT_004aa038);
  }
  return;
}

