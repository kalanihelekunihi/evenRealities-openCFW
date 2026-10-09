# EM9305 official QP/C provider lead — 2026-10-09

## Acquisition and scope

Official https://github.com/QuantumLeaps/qpc.git acquired in isolated `acquisitions/qpc-official`, detached at existing documented v6.5.1 pin `416dcec8820b9cdb5827497e645d0d9375db53c6`. No downloaded code executed. Sources carry GPL-3.0-or-later OR commercial notices; bundled third parties differ. Registered `third-party/upstream/qpc` is empty and was left untouched. Proposed owner action: populate that already registered submodule at the documented pin after review; no new .gitmodules addition is needed. Acquisition is useful because generic QPC source was locally unavailable, whereas stock symbol/provenance records already identify exact SDK QPC objects. The initial web fetch failed; official Git transport successfully retrieved the pinned object.

## Existing closure and ownership

Consolidated libraries/toolchains references establish QPC651 and release code0x8E7055B4, stock limits16active/2pools, zero tick rates, queue counters1byte and memory-pool sizes/counters2bytes. Historical symbol rows claim exact SDK archive bodies for QEQueue_init, QK_sched_, QK_activate_ and SWI0/SWI1 port. The older audit/source archive-match receipt paths referenced by those symbols are absent in the present tree; attribution is existing consolidated evidence, not freshly re-admitted proof. Current v4.6 probe independently reports two exact routines (SWI1 and QEQueue_init), eight changed QPC routines, and explicitly unknown v4.2 layout compatibility. Do not repeat or reinterpret that as10matches.

No matching IRQHandler/SWI1/ArcTimer root names or addresses were found in current task contracts by bounded search. This is not a global ownership/vacancy claim; no reconstruction work was assigned or started.

## Concrete source/configuration discriminators

Official `src/qf/qf_qeq.c:71` provides QEQueue_init: frontEvt=NULL, ring=qSto, end=qLen narrowed to configured counter; head/tail zeroed only for nonzero length; nFree=qLen+1 and nMin=nFree. Stock routine[0x310F5C,0x310F74) is24bytes, known exact also against v4.6. This source supplies a precise conditional-zeroing and counter-width comparator, beyond a generic queue analogy. It does not newly prove producing compiler/configuration or stock structure layout.

Official `src/qk/qk.c` contains QK_sched_ at317 and QK_activate_ at347. Stock bound extents[0x311634,0x31166C)56bytes and[0x311554,0x3115E4)144bytes are saved with fresh slice hashes. Public scheduler semantics can constrain ready-set priority selection, ceiling/preemption handling and nextPrio publication, but target-specific interrupt frames and compiler output remain separately owned. No new whole-function source match is claimed.

Official v6.5.1 ports inventory has **no ARC/arcv2em port**. Therefore generic QPC acquisition cannot explain SWI1[0x3025F8,0x302664)108bytes or timer wrappers by itself. Local authorized EM v4.6 `qf_port.h` is explicitly EM arcv2em and configures16active,2pools,eventsize2,queuecounter1,poolsize2,poolcounter2,timecounter2,tickrates0. It calls vendor critical/IRQ helpers and log2p1. These agree with several consolidated stock values but are not new stock compatibility proof. Header metadata/hash only retained here, no vendor source copied. The header's own permissive notice must be assessed together with recorded SDK agreement before broader redistribution.

Timer0[0x305B1C,0x305BDE) andTimer1[0x305BE0,0x305CA2) are both194bytes and Strong link-order attributed to irq_system_isr.c.obj, unlike nearby Proven GPIO224/PmlClock228 archive matches. Those paired wrappers are a concrete remaining in-image comparison lead: authenticate an available v4.2/v4.6 matching object, normalize only recorded relocations, compare frame save/restore and direct timer helper targets, preserve mismatches. Their equal lengths alone do not establish equivalence. Fresh stock hashes are recorded; no SDK extraction or compiler execution occurred.

## Stopping boundary

Generic embARC architecture/startup comparators do not outrank EM exact archive evidence, and architecture manuals are not producing source. No new official EM controller C implementation was found/acquired. Controller baselineLL_VER_NUM28992 differs from public Cordio1366 and is proprietary; do not substitute the Apollo host source. Authentic source/assembly for EM ARC IRQ port, generating compiler/configuration, v4.2 type layout and unavailable external resident startup remain distinct evidence gaps. SDK objects can support byte/provenance comparisons without supplying C source.

Next finite action for owner: review the pinned generic QPC source against one address-bound scheduler/queue routine, or compare the paired timer wrappers to authenticated available SDK object variants. Stop each comparison at an exact mismatch or unavailable original source/configuration; do not label all in-image ARC code blocked. No staging, canonical mutation, device activity or jobs occurred.
