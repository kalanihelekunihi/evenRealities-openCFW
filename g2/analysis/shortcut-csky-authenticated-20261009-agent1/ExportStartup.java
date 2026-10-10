import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.pcode.*;

public class ExportStartup extends GhidraScript {
  public void run() throws Exception {
    String[] args=getScriptArgs();
    long start=Long.decode(args[0]), end=Long.decode(args[1]);
    Address addr=toAddr(start);
    disassemble(addr);
    Function f=createFunction(addr,"bounded_startup");
    for (Instruction i:currentProgram.getListing().getInstructions(new AddressSet(addr,toAddr(end-1)),true)) {
      println("INSN " + i.getAddress()+" "+i);
      for(PcodeOp p:i.getPcode()) println("PCODE "+p);
    }
    if(f!=null){
      DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
      DecompileResults r=d.decompileFunction(f,60,monitor);
      println("BODY "+f.getBody());
      println("DECOMPILE_COMPLETE "+r.decompileCompleted()+" ERROR "+r.getErrorMessage());
      if(r.getDecompiledFunction()!=null) println(r.getDecompiledFunction().getC());
      d.dispose();
    }
  }
}
