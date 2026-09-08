// SPDX-License-Identifier: MIT
// Diagnose constant-pool propagation on a previously decoded analog leaf.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
public class InspectGx8002Literal extends GhidraScript {
 protected void run() throws Exception {
  Address a=toAddr(0x10008060L);
  MemoryBlock b=currentProgram.getMemory().getBlock(a);
  println("LITERAL_BLOCK "+b.getName()+" write="+b.isWrite()+" volatile="+b.isVolatile());
  println("LITERAL_DATA "+getDataAt(a));
  Instruction instruction=getInstructionAt(toAddr(0x10008048L));
  println("LITERAL_INSTRUCTION "+instruction.getMnemonicString());
  for(Object o:instruction.getOpObjects(1)) println("LITERAL_OPERAND "+o.getClass().getName()+" "+o);
  if(currentProgram.getListing().getDefinedDataAt(a)==null) createDWord(a);
  println("LITERAL_AFTER "+getDataAt(a));
 }
}
