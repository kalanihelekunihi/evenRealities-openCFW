
undefined8 FUN_00473782(void)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_004738f8;
  uVar3 = FUN_0044f718(0x1c);
  *puVar1 = uVar3;
  uVar4 = FUN_0046ca6e();
  uVar3 = 0;
  cVar2 = FUN_0048aef8(*puVar1,0x240,0x120,0xd,0,uVar4,0x14400);
  if (cVar2 == '\0') {
    uVar3 = DAT_00473900;
    FUN_0044d25c(3,DAT_004738f0,0x105,DAT_00473904);
  }
  else {
    uVar5 = FUN_0044f7c0(0x240,0x120);
    FUN_0044fc2e(uVar5,DAT_00473908);
    puVar1 = DAT_004738fc;
    uVar6 = FUN_0048affa(0x240,0x120,6,0);
    *puVar1 = uVar6;
    FUN_0044fbfc(uVar5,*puVar1,0);
    FUN_0044fc18(uVar5,1);
    FUN_0044fa3e(uVar5,0x240,0x120);
    FUN_0044fa5e(uVar5,0,0);
  }
  return CONCAT44(uVar4,uVar3);
}

