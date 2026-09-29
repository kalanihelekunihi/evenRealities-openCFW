
char FUN_005445f2(undefined4 *param_1,uint param_2,undefined4 param_3)

{
  char cVar1;
  undefined4 uVar2;
  undefined1 uStack_3c;
  undefined1 auStack_3b [3];
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined1 auStack_2c [4];
  uint local_28;
  
  FUN_0043c0e4(&uStack_3c,0x10,0);
  if (param_2 != param_1[3] * (param_2 / (uint)param_1[3])) {
    FUN_004733ee(DAT_00544b6c);
    uVar2 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00544b70,*param_1,uVar2);
    FUN_004733ee(DAT_00544ce0,DAT_00544cdc,DAT_0054516c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  cVar1 = FUN_00585a32(param_1,param_2,param_1[3]);
  if (cVar1 == '\0') {
    FUN_0043c0e4(&uStack_3c,0x10,0xff);
    FUN_00585870(&uStack_3c,4,1);
    FUN_00585870(auStack_3b,4,1);
    local_38 = DAT_00544ce8;
    local_30 = 0xffffffff;
    local_34 = param_3;
    cVar1 = FUN_00585a52(param_1,param_2,&uStack_3c,0x10,1);
    FUN_00439c04(auStack_2c,DAT_00545170,0x18);
    local_28 = param_2;
    FUN_00543c48(param_1,auStack_2c);
  }
  return cVar1;
}

