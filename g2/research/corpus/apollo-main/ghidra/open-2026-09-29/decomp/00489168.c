
undefined8 FUN_00489168(int param_1,uint *param_2,uint param_3,undefined4 param_4)

{
  char cVar1;
  uint *puVar2;
  uint uVar3;
  int iVar4;
  
  if (param_2 == (uint *)0x0) {
    puVar2 = (uint *)0x0;
  }
  else {
    puVar2 = param_2;
    if ((((*(char *)(param_1 + 4) != '\0') && ((*param_2 & 0xffff) >> 8 != 0x14)) &&
        (uVar3 = FUN_0048aad8(param_2[1] & 0xffff,*param_2 >> 8 & 0xff),
        (param_2[2] & 0xffff) != uVar3)) && (cVar1 = FUN_0048b34e(param_2,uVar3), cVar1 != '\x01'))
    {
      puVar2 = (uint *)FUN_0048b010(DAT_00489444,param_2[1] & 0xffff,param_2[1] >> 0x10,
                                    *param_2 >> 8 & 0xff);
      if (puVar2 == (uint *)0x0) {
        param_3 = DAT_00489448;
        FUN_0044d25c(3,DAT_00489434,0x102,DAT_0048944c,DAT_00489448,param_4);
        puVar2 = (uint *)0x0;
        goto LAB_00489258;
      }
      FUN_0048ad42(puVar2,0,param_2,0);
      param_3 = uVar3;
    }
    if (((*(char *)(param_1 + 5) != '\0') && (3 < ((*puVar2 & 0xffff) >> 8) - 0xb)) &&
       ((iVar4 = FUN_00440fc4(*puVar2 >> 8 & 0xff), iVar4 != 0 &&
        (iVar4 = FUN_0048b73c(puVar2,1), iVar4 == 0)))) {
      iVar4 = FUN_0048b73c(puVar2,0x20);
      if (iVar4 == 0) {
        puVar2 = (uint *)FUN_0048b134(DAT_00489444,puVar2);
        if (puVar2 == (uint *)0x0) {
          param_3 = DAT_00489450;
          FUN_0044d25c(3,DAT_00489434,0x11a,DAT_0048944c);
          puVar2 = (uint *)0x0;
        }
        else {
          FUN_0048b540(puVar2);
        }
      }
      else {
        FUN_0048b540(puVar2);
      }
    }
  }
LAB_00489258:
  return CONCAT44(param_3,puVar2);
}

