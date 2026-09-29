
uint FUN_005088be(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined1 param_4)

{
  undefined4 *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  undefined1 auStack_38 [5];
  undefined1 local_33;
  undefined1 local_32;
  
  FUN_00439c04(auStack_38,DAT_00508a74,0x24);
  puVar1 = DAT_00508a70;
  local_33 = param_2;
  local_32 = param_4;
  uVar2 = FUN_0055d478(*DAT_00508a70,auStack_38,0);
  uVar3 = FUN_0055d510(*puVar1,1);
  uVar4 = FUN_00508868();
  uVar5 = FUN_0055d560(*puVar1,param_3,param_4);
  return uVar2 | uVar3 | uVar4 | uVar5;
}

