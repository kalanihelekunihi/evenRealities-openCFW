
undefined8 FUN_00487022(int param_1,undefined4 param_2,undefined4 param_3,uint param_4,int param_5)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  char cVar7;
  undefined4 local_30;
  undefined4 local_2c;
  uint local_28;
  
  local_30 = param_2;
  local_2c = param_3;
  local_28 = param_4;
  iVar1 = FUN_0048716c();
  if (iVar1 == 0) {
    uVar2 = FUN_0044f730(0x38c);
    *(undefined4 *)(DAT_00487184 + 0x178) = uVar2;
  }
  puVar6 = *(undefined4 **)(DAT_00487184 + 0x178);
  iVar1 = param_1;
  if (param_1 == 0) {
    iVar1 = FUN_0044fa1a();
  }
  iVar3 = FUN_0044fbe6(iVar1);
  iVar4 = FUN_0044fa7e(iVar1);
  if (iVar4 < 0x141) {
    cVar7 = '\x03';
  }
  else if (iVar4 < 0x2d0) {
    cVar7 = '\x02';
  }
  else {
    cVar7 = '\x01';
  }
  local_30 = param_3;
  local_2c = param_2;
  if (((*(char *)(puVar6 + 0xf) != '\0') && (puVar6[0xb] == iVar3)) &&
     (*(char *)(puVar6 + 10) == cVar7)) {
    FUN_00439be4(&local_28,puVar6 + 4,3);
    iVar4 = FUN_0044102e(local_28,local_2c);
    if (iVar4 != 0) {
      FUN_00439be4(&local_28,(int)puVar6 + 0x13,3);
      iVar4 = FUN_0044102e(local_28,local_30);
      if (((iVar4 != 0) && (puVar6[9] == (param_4 & 0xff))) && (puVar6[6] == param_5))
      goto LAB_00487152;
    }
  }
  *(char *)(puVar6 + 10) = cVar7;
  puVar6[0xb] = iVar3;
  puVar6[3] = iVar1;
  FUN_00439be4(puVar6 + 4,&local_2c,3);
  FUN_00439be4((int)puVar6 + 0x13,&local_30,3);
  puVar6[6] = param_5;
  puVar6[7] = param_5;
  puVar6[8] = param_5;
  *puVar6 = &LAB_00487188_1;
  puVar6[9] = (uint)((param_4 & 0xff) != 0);
  FUN_00484a98(puVar6);
  if ((param_1 == 0) || (puVar5 = (undefined4 *)FUN_0044fe7e(param_1), puVar5 == puVar6)) {
    FUN_0044bc48(0);
  }
  *(undefined1 *)(puVar6 + 0xf) = 1;
LAB_00487152:
  return CONCAT44(local_30,puVar6);
}

