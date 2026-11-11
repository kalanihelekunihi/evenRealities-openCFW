# Dual-window feature support C probe

The ignored candidate at `build/goal-r1-dual-window-support-c/candidate.c` implements native peak-feature metrics `0x37a84` (220 bytes). It is not yet a source-manifest unit.

41,984 stock/C comparisons pass:32,768 direct,7,680 sentinel/data/output aliases and1,536 independent Fraction-oracle pairs. Ten compiled defects are detected. REA authenticates220 instruction bytes and8 literal bytes;all220 bytes/62 starts execute. Direct tests cover all32 FP configurations;aliases/oracles cover six.

The helper appends value1 and index length-1 BEFORE iterating through count+1 points. Signaling positive-value tests,full-word normalization length,nonfused squared-error accumulation,reverse absolute difference,raw signed-bit half clamp and VMLS quality arithmetic preserve stock order/status. The sentinel buffers can alias,including a case that reaches the zero-used-point branch. RMS and quality outputs can overlap inputs or each other. Actual C sqrtf is used;no stock executable code is mapped.

Independent Fraction normalized-position deviations yield expected RMS and clipped mean-absolute quality,with tolerances2e-5 RMS/5e-4 score for rounded finite cases. Exact stock/C comparisons,public RAM,FPSCR,saved registers,SP and masks are checked separately. Private8192 stack bytes and void caller-scratch/APSR are outside proof.

Before admission:add the shared native interface/source unit,verify normal objects and ownership,and connect real extractor callers. The dual-window extractor29144 still needs autocorrelation/normalization666a4 and92a04,peak selection36734/66900/668dc,rate extraction42bd0,and packed conversion28dd4/362f4/28de0/4fdf8 with array loop28dec. REA dossiers are saved beside this probe;generic packed-kernel pseudocode may be specialized to a different thunk/width,so raw ABI/register evidence must govern. No portable guessed ABI alias is introduced.

Valid mapped sentinel capacity is assumed. Invalid counts/pointers,physical hardware,timing and concurrency remain unverified.

[Probe evidence](goodix-dual-window-support-c-probe.json).
