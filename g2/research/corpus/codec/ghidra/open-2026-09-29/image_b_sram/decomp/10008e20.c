
uint FUN_10008e20(undefined *param_1,int param_2,uint param_3,char *param_4)

{
  undefined *puVar1;
  char cVar2;
  char *pcVar3;
  uint uVar4;
  undefined *puVar5;
  uint uVar6;
  
  puVar1 = PTR_PTR_10008e88;
  puVar5 = PTR_LAB_10008e80;
  if (param_2 != 0) {
    puVar5 = param_1;
  }
  uVar6 = 0;
  cVar2 = *param_4;
  do {
    if (cVar2 == '\0') {
      uVar4 = uVar6;
      if (param_3 <= uVar6) {
        uVar4 = param_3 - 1;
      }
      (*(code *)((uint)puVar5 & 0xfffffffe))(0,param_2,uVar4,param_3);
      return uVar6;
    }
    if (cVar2 == '%') {
      pcVar3 = param_4 + 1;
      cVar2 = *pcVar3;
      if ((byte)(cVar2 - 0x20) < 0x11) {
                    /* WARNING: Could not recover jumptable at 0x10008e76. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        uVar6 = (*(code *)(*(uint *)(puVar1 + (uint)(byte)(cVar2 - 0x20) * 4) & 0xfffffffe))();
        return uVar6;
      }
      if ((byte)(cVar2 - 0x30U) < 10) {
        do {
          pcVar3 = pcVar3 + 1;
          cVar2 = *pcVar3;
        } while ((byte)(cVar2 - 0x30U) < 10);
      }
      else if (cVar2 == '*') {
        cVar2 = param_4[2];
        pcVar3 = param_4 + 2;
      }
      param_4 = pcVar3;
      if (cVar2 == '.') {
        cVar2 = pcVar3[1];
        param_4 = pcVar3 + 1;
        if ((byte)(cVar2 - 0x30U) < 10) {
          do {
            param_4 = param_4 + 1;
            cVar2 = *param_4;
          } while ((byte)(cVar2 - 0x30U) < 10);
        }
        else if (cVar2 == '*') {
          cVar2 = pcVar3[2];
          param_4 = pcVar3 + 2;
        }
      }
      if ((byte)(cVar2 + 0x98) < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10008eec. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        uVar6 = (*(code *)(*(uint *)(PTR_PTR_10008ef0 + (uint)(byte)(cVar2 + 0x98) * 4) & 0xfffffffe
                          ))();
        return uVar6;
      }
      if ((byte)(cVar2 - 0x25) < 0x54) {
                    /* WARNING: Could not recover jumptable at 0x10008f0e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        uVar6 = (*(code *)(*(uint *)(PTR_PTR_10008f10 + (uint)(byte)(cVar2 - 0x25) * 4) & 0xfffffffe
                          ))();
        return uVar6;
      }
    }
    param_4 = param_4 + 1;
    (*(code *)((uint)puVar5 & 0xfffffffe))(cVar2,param_2,uVar6,param_3);
    cVar2 = *param_4;
    uVar6 = uVar6 + 1;
  } while( true );
}

