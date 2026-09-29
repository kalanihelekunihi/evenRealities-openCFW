
undefined8 FUN_004708a8(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = 0;
  if (((*DAT_004710ac == 0) || (param_2 == 0)) || (param_3 == 0)) {
    FUN_004733ee(DAT_004710b0,*DAT_004710ac,param_2,param_3,param_3,param_4);
    iVar1 = 6;
    uVar4 = param_3;
  }
  else if (param_1 < 0x2000000) {
    uVar4 = param_3;
    FUN_0046f65e();
    FUN_00470f68();
    uVar2 = param_1 & 0xff;
    for (; param_3 != 0; param_3 = param_3 - uVar3) {
      uVar3 = 0x100 - uVar2;
      if (param_3 <= 0x100 - uVar2) {
        uVar3 = param_3;
      }
      iVar1 = FUN_004703ba();
      if (iVar1 != 0) {
        FUN_004733ee(DAT_004710b8,param_1,uVar3);
        iVar1 = 4;
        break;
      }
      iVar1 = FUN_00470670();
      if (iVar1 != 0) {
        FUN_004733ee(DAT_004710bc,param_1,uVar3,iVar1);
        break;
      }
      uVar4 = uVar3;
      iVar1 = FUN_0047021c(2,param_1,1,param_2);
      if (iVar1 != 0) {
        FUN_004733ee(DAT_004710c0,param_1,uVar3,iVar1);
        break;
      }
      iVar1 = FUN_00470368(10);
      if (iVar1 != 0) {
        FUN_004733ee(DAT_004710c4,param_1,uVar3);
        iVar1 = 4;
        break;
      }
      iVar1 = FUN_004706e0();
      if (iVar1 != 0) {
        FUN_004733ee(DAT_004710c8,param_1,uVar3,iVar1);
        break;
      }
      param_1 = uVar3 + param_1;
      param_2 = param_2 + uVar3;
      uVar2 = 0;
    }
    FUN_00470e90();
    FUN_0046f674();
  }
  else {
    FUN_004733ee(DAT_004710b4,param_1,0x2000000,param_4,param_3,param_4);
    iVar1 = 5;
    uVar4 = param_3;
  }
  return CONCAT44(uVar4,iVar1);
}

