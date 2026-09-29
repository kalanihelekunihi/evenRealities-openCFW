
void FUN_10008d48(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 int param_5,int param_6,undefined1 param_7,undefined4 param_8,undefined4 param_9,
                 undefined4 param_10,undefined4 param_11,uint param_12)

{
  char cVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  char *pcVar5;
  char cVar6;
  char local_4c [32];
  
  if ((param_5 == 0 && param_6 == 0) &&
     (uVar3 = param_12 & 0x400, param_12 = param_12 & 0xffffffef, uVar3 != 0)) {
    iVar4 = 0;
  }
  else {
    cVar6 = 'A';
    if ((param_12 & 0x20) == 0) {
      cVar6 = 'a';
    }
    pcVar5 = local_4c;
    iVar4 = 0;
    do {
      bVar2 = FUN_100117d0(param_5,param_6,param_8,param_9);
      iVar4 = iVar4 + 1;
      if (bVar2 < 10) {
        cVar1 = bVar2 + 0x30;
      }
      else {
        cVar1 = bVar2 + cVar6 + -10;
      }
      *pcVar5 = cVar1;
      param_5 = FUN_1001149c(param_5,param_6,param_8,param_9);
    } while ((param_6 != 0 || param_5 != 0) && (pcVar5 = pcVar5 + 1, iVar4 != 0x20));
  }
  FUN_10008aa0(param_1,param_2,param_3,param_4,local_4c,iVar4,param_7,param_8,param_10,param_11,
               param_12);
  return;
}

