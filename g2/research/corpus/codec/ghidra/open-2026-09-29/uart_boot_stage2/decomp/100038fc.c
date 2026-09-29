
undefined4 FUN_100038fc(uint param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  byte bStack_21;
  
  do {
    FUN_100034a4(5,&bStack_21,1);
  } while ((bStack_21 & 1) != 0);
  FUN_10003524(6,bStack_21 & 1);
  iVar1 = DAT_1000398c;
  if ((param_1 & 0xff) + param_3 < 0x101) {
    (*(code *)(*(uint *)(DAT_1000398c + 0x18) & 0xfffffffe))(param_1,param_2,param_3);
    return 0;
  }
  uVar2 = 0x100 - (param_1 & 0xff);
  (*(code *)(*(uint *)(DAT_1000398c + 0x18) & 0xfffffffe))(param_1,param_2,uVar2);
  for (; uVar2 < param_3; uVar2 = uVar2 + iVar4) {
    uVar3 = param_3 - uVar2;
    iVar4 = (uVar3 < 0x100) * uVar3 + (uint)(uVar3 >= 0x100) * 0x100;
    FUN_10003524(6,0);
    (*(code *)(*(uint *)(iVar1 + 0x18) & 0xfffffffe))(param_1 + uVar2,param_2 + uVar2,iVar4);
  }
  return 0;
}

