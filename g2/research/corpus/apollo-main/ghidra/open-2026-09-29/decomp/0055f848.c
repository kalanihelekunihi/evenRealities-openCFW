
void FUN_0055f848(undefined4 param_1,float param_2,undefined4 param_3,undefined4 param_4,int param_5
                 )

{
  char *pcVar1;
  int iVar2;
  float fVar3;
  undefined1 local_b8 [16];
  float local_a8;
  undefined1 auStack_a4 [4];
  undefined4 local_a0;
  undefined4 local_9c;
  undefined1 local_98 [72];
  undefined1 auStack_50 [16];
  undefined1 auStack_40 [16];
  undefined4 local_30;
  
  iVar2 = DAT_0055f980;
  pcVar1 = DAT_0055f974;
  if (((int)param_2 < 0) || (DAT_0055f974[1] != '\0')) {
    fVar3 = *(float *)(DAT_0055f974 + 0xc);
    local_a0 = *DAT_0055f978;
    local_9c = *DAT_0055f97c;
    if ((NAN(fVar3)) || (*DAT_0055f974 != '\x02')) {
      fVar3 = param_2 * *(float *)(DAT_0055f974 + 4);
    }
  }
  else {
    local_a0 = *DAT_0055f988;
    local_9c = *DAT_0055f98c;
    fVar3 = param_2 * *(float *)(DAT_0055f974 + 8);
  }
  FUN_0058eab0(DAT_0055f980,&local_a0);
  if (*pcVar1 == '\x05') {
    FUN_00439e90(local_98,DAT_0055f990,0x6c);
    VectorLoadRegister(iVar2 + 0x54,2,4,0);
    VectorLoadRegister(iVar2 + 100,2,4,0);
    local_30 = *(undefined4 *)(iVar2 + 0x74);
    VectorStoreRegister(auStack_50,2,4,0);
    VectorStoreRegister(auStack_40,2,4,0);
    FUN_0043bb00(iVar2,0,0xe0);
    FUN_0043a1b0(param_1,fVar3,param_3,local_98,*(undefined4 *)(iVar2 + 0xe0),iVar2);
    *pcVar1 = '\0';
  }
  FUN_0043a698(param_1,fVar3,param_3,param_4,DAT_0055f980,*(undefined4 *)(iVar2 + 0xe0),&local_a8,
               auStack_a4,local_98);
  if (param_5 != 0) {
    VectorLoadRegister(local_b8,2,4,0);
    *(float *)(param_5 + 0x10) = local_a8 * DAT_0055f984;
    VectorStoreRegister(param_5,2,4,0);
  }
  return;
}

