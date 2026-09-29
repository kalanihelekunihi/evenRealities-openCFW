
undefined8 FUN_00505692(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  byte bVar4;
  
  uVar2 = 0;
  cVar3 = '\x01';
  for (bVar4 = 0; bVar4 <= (*param_2 & 3); bVar4 = bVar4 + 1) {
    uVar1 = FUN_00504d2c(param_1,param_2,cVar3);
    uVar2 = uVar2 | uVar1;
    cVar3 = cVar3 + '\x01';
  }
  return CONCAT44(param_4,uVar2);
}

