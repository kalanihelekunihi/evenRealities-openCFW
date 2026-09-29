
undefined4 touch_platform_1334_probe(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = Cy_SysPm_RegisterCallback(DAT_00004648);
  uVar2 = DAT_0000464c;
  if (iVar1 != 0) {
    uVar2 = 0;
  }
  return uVar2;
}

