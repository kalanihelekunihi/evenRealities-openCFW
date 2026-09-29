
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 hw_config_transaction_42c988(uint *param_1,byte param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  undefined4 uStack_10;
  
  iVar1 = _DAT_0042cdc8;
  uStack_10 = param_4;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0042cdb0)) {
    iVar1 = 2;
    goto LAB_0042cae4;
  }
  if (param_2 == 0) {
    if ((param_3 != '\0') && ((char)param_1[0x21a] == '\0')) {
      iVar1 = 7;
      goto LAB_0042cae4;
    }
    FUN_0041bf84(param_1[1] + 3 & 0xff);
    iVar1 = _DAT_0042cdc8;
    if (param_3 != '\0') {
      *(uint *)(_DAT_0042cdc8 + param_1[1] * 0x1000 + 0x104) = param_1[0x21b];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x118) = param_1[0x21d];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x22c) = param_1[0x220];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x234) = param_1[0x221];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x23c) = param_1[0x222];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x240) = param_1[0x223];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x244) = param_1[0x224];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x280) = param_1[0x225];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c0) = param_1[0x226];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x200) = param_1[0x227];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x210) = param_1[0x21c];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x228) = param_1[0x21f] & 0xfffffffe;
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c) = param_1[0x21e];
      if ((int)((uint)(byte)param_1[0x21f] << 0x1f) < 0) {
        cmdq_adapter_enable_42c420(param_1);
      }
      if ((int)(*param_1 << 6) < 0) {
        uStack_10 = 1;
        delay_us_status_check(1000,iVar1 + param_1[1] * 0x1000 + 0x248,6,4);
      }
      *(undefined1 *)(param_1 + 0x21a) = 0;
    }
    iVar1 = clock_request(4,param_1[1] + 3 & 0xff);
  }
  else {
    if ((param_2 != 2) && (1 < param_2)) {
      iVar1 = 6;
      goto LAB_0042cae4;
    }
    if (((int)(*param_1 << 6) < 0) &&
       (((*(uint *)(_DAT_0042cdc8 + param_1[1] * 0x1000 + 0x248) & 6) != 4 || (param_1[9] != 0)))) {
      iVar1 = 3;
      goto LAB_0042cae4;
    }
    if (param_3 != '\0') {
      param_1[0x21b] = *(uint *)(_DAT_0042cdc8 + param_1[1] * 0x1000 + 0x104);
      param_1[0x21d] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x118);
      param_1[0x21e] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c);
      param_1[0x21f] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x228);
      param_1[0x220] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x22c);
      param_1[0x221] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x234);
      param_1[0x222] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x23c);
      param_1[0x223] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x240);
      param_1[0x224] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x244);
      param_1[0x225] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x280);
      param_1[0x226] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c0);
      param_1[0x227] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x200);
      param_1[0x21c] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x210);
      if (*(int *)(iVar1 + param_1[1] * 0x1000 + 0x228) << 0x1f < 0) {
        cmdq_adapter_disable_42c44e(param_1);
      }
      *(undefined1 *)(param_1 + 0x21a) = 1;
    }
    iVar1 = _DAT_0042cdc8;
    puVar2 = (uint *)(_DAT_0042cdc8 + param_1[1] * 0x1000 + 0x11c);
    *puVar2 = *puVar2 & 0xfffffffe;
    puVar2 = (uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c);
    *puVar2 = *puVar2 & 0xffffffef;
    FUN_0041c17a(param_1[1] + 3 & 0xff);
    iVar1 = clock_release(4,param_1[1] + 3 & 0xff);
  }
  if (iVar1 == 0) {
    iVar1 = 0;
  }
LAB_0042cae4:
  return CONCAT44(uStack_10,iVar1);
}

