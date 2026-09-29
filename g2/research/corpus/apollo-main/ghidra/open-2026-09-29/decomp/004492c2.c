
undefined8 osThreadFlagsWait(uint param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint local_30;
  uint local_2c;
  undefined4 uStack_28;
  
  local_2c = param_3;
  uStack_28 = param_4;
  iVar1 = IRQ_Context();
  local_30 = param_2;
  if (iVar1 == 0) {
    if ((int)param_1 < 0) {
      uVar4 = 0xfffffffc;
    }
    else {
      uVar5 = param_1;
      if ((int)(param_2 << 0x1e) < 0) {
        uVar5 = 0;
      }
      uVar4 = 0;
      iVar1 = xTaskGetTickCount();
      uVar6 = param_3;
      do {
        local_30 = uVar6;
        iVar2 = FUN_00455b84(0,0,uVar5,&local_2c);
        if (iVar2 == 1) {
          uVar4 = local_2c | uVar4 & param_1;
          if ((int)(param_2 << 0x1f) < 0) {
            if ((uVar4 & param_1) == param_1) break;
            if (param_3 == 0) {
              uVar4 = 0xfffffffd;
              break;
            }
          }
          else {
            if ((param_1 & uVar4) != 0) break;
            if (param_3 == 0) {
              uVar4 = 0xfffffffd;
              break;
            }
          }
          iVar3 = xTaskGetTickCount();
          if (param_3 < (uint)(iVar3 - iVar1)) {
            uVar6 = 0;
          }
          else {
            uVar6 = param_3 - (iVar3 - iVar1);
          }
        }
        else {
          uVar6 = local_30;
          if (param_3 == 0) {
            uVar4 = 0xfffffffd;
          }
          else {
            uVar4 = 0xfffffffe;
          }
        }
      } while (iVar2 != 0);
    }
  }
  else {
    uVar4 = 0xfffffffa;
  }
  return CONCAT44(local_30,uVar4);
}

