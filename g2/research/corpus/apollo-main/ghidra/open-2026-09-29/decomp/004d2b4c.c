
undefined1 dmInitPhyToIdx(char param_1,char param_2)

{
  undefined1 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 0;
  }
  else if (param_1 == '\x02') {
    uVar1 = param_2 != '\x01';
  }
  else if (param_2 == '\x01') {
    uVar1 = 0;
  }
  else if (param_2 == '\x02') {
    uVar1 = 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

