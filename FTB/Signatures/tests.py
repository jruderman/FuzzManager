'''
Tests

@author:     Christian Holler (:decoder)

@license:

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

@contact:    choller@mozilla.com
'''
import unittest
from FTB.Signatures.CrashInfo import ASanCrashInfo, GDBCrashInfo, CrashInfo,\
    NoCrashInfo, MinidumpCrashInfo
from FTB.Signatures.CrashSignature import CrashSignature
from FTB.Signatures import RegisterHelper

from numpy import int64, uint64, int32, uint32
from FTB.ProgramConfiguration import ProgramConfiguration

asanTraceCrash = """
ASAN:SIGSEGV
=================================================================
==5854==ERROR: AddressSanitizer: SEGV on unknown address 0x00000014 (pc 0x0810845f sp 0xffc57860 bp 0xffc57f18 T0)
    #0 0x810845e in js::AbstractFramePtr::asRematerializedFrame() const /srv/repos/mozilla-central/js/src/shell/../jit/RematerializedFrame.h:114
    #1 0x810845e in js::AbstractFramePtr::script() const /srv/repos/mozilla-central/js/src/shell/../vm/Stack-inl.h:572
    #2 0x810845e in EvalInFrame(JSContext*, unsigned int, JS::Value*) /srv/repos/mozilla-central/js/src/shell/js.cpp:2655
    #3 0x93f5b92 in js::CallJSNative(JSContext*, bool (*)(JSContext*, unsigned int, JS::Value*), JS::CallArgs const&) /srv/repos/mozilla-central/js/src/jscntxtinlines.h:231
    #4 0x93f5b92 in js::Invoke(JSContext*, JS::CallArgs, js::MaybeConstruct) /srv/repos/mozilla-central/js/src/vm/Interpreter.cpp:484
    #5 0x9346ba7 in js::Invoke(JSContext*, JS::Value const&, JS::Value const&, unsigned int, JS::Value const*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/vm/Interpreter.cpp:540
    #6 0x8702baa in js::jit::DoCallFallback(JSContext*, js::jit::BaselineFrame*, js::jit::ICCall_Fallback*, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/jit/BaselineIC.cpp:8638

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /srv/repos/mozilla-central/js/src/shell/../jit/RematerializedFrame.h:114 js::AbstractFramePtr::asRematerializedFrame() const
==5854==ABORTING
"""

asanTraceHeapCrash = """
ASAN:SIGSEGV
=================================================================
==11923==ERROR: AddressSanitizer: SEGV on unknown address 0x00000019 (pc 0xf718072e sp 0xff87d130 bp 0x000006a1 T0)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV ??:0 ??
==11923==ABORTING
"""

asanTraceUAF = """
==19462==ERROR: AddressSanitizer: heap-use-after-free on address 0x7fd766c42800 at pc 0xe1f587 bp 0x7fffcb1b6ed0 sp 0x7fffcb1b6ec8
READ of size 6143520 at 0x7fd766c42800 thread T0
    #0 0xe1f586 in void mozilla::PodCopy<char16_t>(char16_t*, char16_t const*, unsigned long) /srv/repos/mozilla-central/js/src/opt64asan/js/src/../../dist/include/mozilla/PodOperations.h:110
    #1 0x5904e2 in js::frontend::CompileScript(js::ExclusiveContext*, js::LifoAlloc*, JS::Handle<JSObject*>, JS::Handle<JSScript*>, JS::ReadOnlyCompileOptions const&, char16_t const*, unsigned long, JSString*, unsigned int, js::SourceCompressionTask*) /srv/repos/mozilla-central/js/src/frontend/BytecodeCompiler.cpp:215
    #2 0xc7eb8d in JS::Compile(JSContext*, JS::Handle<JSObject*>, JS::ReadOnlyCompileOptions const&, char16_t const*, unsigned long) /srv/repos/mozilla-central/js/src/jsapi.cpp:4478
    #3 0x4f63a6 in Run(JSContext*, unsigned int, JS::Value*) /srv/repos/mozilla-central/js/src/shell/js.cpp:1193
    #4 0xf8eb1b in JSFunction::native() const /srv/repos/mozilla-central/js/src/jscntxtinlines.h:220
    #5 0xf377c8 in js::Invoke(JSContext*, JS::Value const&, JS::Value const&, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/vm/Interpreter.cpp:521
    #6 0x82e98a in js::jit::DoCallFallback(JSContext*, js::jit::BaselineFrame*, js::jit::ICCall_Fallback*, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/jit/BaselineIC.cpp:8103
    #7 0x7fd76b2b1323 in
0x7fd766c42800 is located 0 bytes inside of 6143522-byte region [0x7fd766c42800,0x7fd76721e622)
freed by thread T0 here:
    #0 0x4c6855 in __interceptor_free _asan_rtl_
    #1 0xf0f898 in js_free(void*) /srv/repos/mozilla-central/js/src/opt64asan/js/src/../../dist/include/js/Utility.h:167
    #2 0xd18c5d in _ZL19FinalizeTypedArenasI8JSStringEbPN2js6FreeOpEPPNS1_2gc11ArenaHeaderERNS4_9ArenaListENS4_9AllocKindERNS1_11SliceBudgetE /srv/repos/mozilla-central/js/src/jsgc.cpp:540
    #3 0xec61f6 in js::gc::ArenaLists::backgroundFinalize(js::FreeOp*, js::gc::ArenaHeader*, bool) /srv/repos/mozilla-central/js/src/jsgc.cpp:1539
    #4 0xebbaf7 in GCCycle(JSRuntime*, bool, long, js::JSGCInvocationKind, JS::gcreason::Reason) /srv/repos/mozilla-central/js/src/jsgc.cpp:4786
previously allocated by thread T0 here:
    #0 0x4c6995 in __interceptor_malloc _asan_rtl_
    #1 0xeeed65 in js_malloc(unsigned long) /srv/repos/mozilla-central/js/src/opt64asan/js/src/../../dist/include/js/Utility.h:144
    #2 0x4ff625 in FileAsString(JSContext*, char const*) /srv/repos/mozilla-central/js/src/shell/js.cpp:1104
    #3 0x4f61a0 in Run(JSContext*, unsigned int, JS::Value*) /srv/repos/mozilla-central/js/src/shell/js.cpp:1176
    #4 0xf8eb1b in JSFunction::native() const /srv/repos/mozilla-central/js/src/jscntxtinlines.h:220
    #5 0xf377c8 in js::Invoke(JSContext*, JS::Value const&, JS::Value const&, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/vm/Interpreter.cpp:521
    #6 0x82e98a in js::jit::DoCallFallback(JSContext*, js::jit::BaselineFrame*, js::jit::ICCall_Fallback*, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>) /srv/repos/mozilla-central/js/src/jit/BaselineIC.cpp:8103
    #7 0x7fd76b2b1323 in
    #8 0x61100032da17 in
    #9 0x7fd76b2aa503 in
Shadow bytes around the buggy address:
  0x0ffb6cd804b0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0ffb6cd804c0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0ffb6cd804d0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0ffb6cd804e0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0ffb6cd804f0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
=>0x0ffb6cd80500:[fd]fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0ffb6cd80510: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0ffb6cd80520: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0ffb6cd80530: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0ffb6cd80540: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0ffb6cd80550: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07
  Heap left redzone:     fa
  Heap right redzone:    fb
  Freed heap region:     fd
  Stack left redzone:    f1
  Stack mid redzone:     f2
  Stack right redzone:   f3
  Stack partial redzone: f4
  Stack after return:    f5
  Stack use after scope: f8
  Global redzone:        f9
  Global init order:     f6
  Poisoned by user:      f7
  ASan internal:         fe
==19462==ABORTING
"""

gdbCrashAddress1 = """
(gdb) bt 16 
#0  js::types::TypeObject::addProperty (this=0xf7469400, cx=0x9366458, id=$jsid(0x0), pprop=0xf7469418) at /srv/repos/mozilla-central/js/src/jsinfer.cpp:3691 
(More stack frames follow...) 
(gdb) info reg 
eax            0x1      1
ecx            0x1      1
(gdb) x /i $pc 
=> 0x812bf19 <js::types::TypeObject::addProperty(JSContext*, jsid, js::types::Property**)+121>: mov    (%ecx),%ecx
"""
   
gdbCrashAddress2 = """
Program terminated with signal 11, Segmentation fault. 
#0  repoint (this=0x160fc30, cx=0x15a4940, masm=..., attacher=..., ion=0x160fa80, attachKind=0x2b08c0 \"generic\") at /srv/repos/mozilla-central/js/src/ion/IonCaches.cpp:44 
#1  CodeLocationJump (this=0x160fc30, cx=0x15a4940, masm=..., attacher=..., ion=0x160fa80, attachKind=0x2b08c0 \"generic\") at ../ion/shared/Assembler-shared.h:452 
r0      0x34    52 
r4      0x15a4940       22694208 
r10     0x0     0 
sp      0xbe9fec08      3198151688 
pc      0x1a03ae <js::ion::IonCache::linkAndAttachStub(JSContext*, js::ion::MacroAssembler&, js::ion::IonCache::StubAttacher&, js::ion::IonScript*, char const*)+122> 
cpsr    0xd0030 852016 
=> 0x1a03ae <js::ion::IonCache::linkAndAttachStub(JSContext*, js::ion::MacroAssembler&, js::ion::IonCache::StubAttacher&, js::ion::IonScript*, char const*)+122>:       ldr.w   r4, [r10] 
   0x1a03b2 <js::ion::IonCache::linkAndAttachStub(JSContext*, js::ion::MacroAssembler&, js::ion::IonCache::StubAttacher&, js::ion::IonScript*, char const*)+126>:       mov     r3, r0
"""
   
gdbCrashAddress3 = """       
(gdb) bt 16 
#0  js::types::TypeObject::addProperty (this=0xf7469400, cx=0x9366458, id=$jsid(0x0), pprop=0xf7469418) at /srv/repos/mozilla-central/js/src/jsinfer.cpp:3691 
(More stack frames follow...) 
(gdb) info reg 
rax            0x1      1
rdx            0x1      1
rbx            0x1      1
(gdb) x /i $pc 
=> 0x812bf19 <js::types::TypeObject::addProperty(JSContext*, jsid, js::types::Property**)+121>: shrb   -0x69(%rdx,%rbx,8)
"""

gdbSampleTrace1 = """
[New Thread 14711]
[Thread debugging using libthread_db enabled]
Core was generated by `/srv/repos/ionmonkey/js/src/opt32/js --ion -n -m --ion-eager -f /home/ownhero/h'.
Program terminated with signal 11, Segmentation fault.
#0  0x083fa060 in internalAppend<js::ion::MDefinition*> (this=0x847e4e8, ins=0x9e2ced0) at ./dist/include/js/Vector.h:790
790         new(endNoCheck()) T(t);
#0  0x083fa060 in internalAppend<js::ion::MDefinition*> (this=0x847e4e8, ins=0x9e2ced0) at ./dist/include/js/Vector.h:790
#1  append<js::ion::MDefinition*> (this=0x847e4e8, ins=0x9e2ced0) at ./dist/include/js/Vector.h:779
#2  js::ion::MPhi::addInput (this=0x847e4e8, ins=0x9e2ced0) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/MIR.cpp:456
#3  0x0838ad1c in js::ion::MBasicBlock::setBackedge (this=0x9d4a630, pred=0x9e2d0a8) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/MIRGraph.cpp:661
#4  0x0833ea08 in js::ion::IonBuilder::finishLoop (this=0xffdef8e0, state=..., successor=0x9e2d280) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/IonBuilder.cpp:1303
#5  0x0833eb47 in js::ion::IonBuilder::processForUpdateEnd (this=0xffdef8e0, state=...) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/IonBuilder.cpp:1476
#6  0x08350ac0 in processCfgStack (this=0xffdef8e0) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/IonBuilder.cpp:1104
#7  js::ion::IonBuilder::traverseBytecode (this=0xffdef8e0) at /home/ownhero/homes/mozilla/repos/ionmonkey/js/src/ion/IonBuilder.cpp:627
eax    0x0    0
ebx    0x8962ff4    144060404
ecx    0xf76038ac    -144688980
edx    0x0    0
esi    0xf7602d9c    -144691812
edi    0x0    0
ebp    0xff916fb8    4287721400
esp    0xff916ed0    4287721168
eip    0x818bc33 <js::InvokeKernel(JSContext*, JS::CallArgs, js::MaybeConstruct)+419>
=> 0x818bc33 <js::InvokeKernel(JSContext*, JS::CallArgs, js::MaybeConstruct)+419>:    movl   $0x7b,0x0
   0x818bc3d <js::InvokeKernel(JSContext*, JS::CallArgs, js::MaybeConstruct)+429>:    call   0x804af50 <abort@plt>
"""
        
gdbSampleTrace2 = """
Program terminated with signal 11, Segmentation fault.
#0  operator+ (this=0xf6c7e760, cx=0xa3024b8, iv=..., useLocale=false, buffer=..., sb=...) at ../gc/Barrier.h:462
462         HeapSlotArray operator +(uint32_t offset) const { return HeapSlotArray(array + offset); }
#0  operator+ (this=0xf6c7e760, cx=0xa3024b8, iv=..., useLocale=false, buffer=..., sb=...) at ../gc/Barrier.h:462
#1  js::ParallelArrayObject::toStringBufferImpl (this=0xf6c7e760, cx=0xa3024b8, iv=..., useLocale=false, buffer=..., sb=...) at /srv/repos/mozilla-central/js/src/builtin/ParallelArray.cpp:1521
#2  0x081d0379 in js::ParallelArrayObject::toStringBuffer (this=0xf6c7e760, cx=0xa3024b8, useLocale=false, sb=...) at /srv/repos/mozilla-central/js/src/builtin/ParallelArray.cpp:1566
#3  0x081d05b3 in js::ParallelArrayObject::toString (cx=0xa3024b8, args=...) at /srv/repos/mozilla-central/js/src/builtin/ParallelArray.cpp:1573
#4  0x081d06be in CallNonGenericMethod (cx=0xa3024b8, argc=0, vp=0xf6ee2150) at ../jsapi.h:1570
#5  NonGenericMethod<js::ParallelArrayObject::toString> (cx=0xa3024b8, argc=0, vp=0xf6ee2150) at /srv/repos/mozilla-central/js/src/builtin/ParallelArray.cpp:163
#6  0x080d8dd8 in CallJSNative (cx=0xa3024b8, args=..., construct=js::NO_CONSTRUCT) at ../jscntxtinlines.h:389
#7  PropertyAccess<(PropertyAccessKind)1> (cx=0xa3024b8, args=..., construct=js::NO_CONSTRUCT) at /srv/repos/mozilla-central/js/src/jsinterp.cpp:351
rbx            0x1      1
r14            0x1      1
=> 0x7f01fffecf41:    mov    0x8(%r14),%rbx
   0x7f01fffecf45:    cmp    %rbx,0x18(%rdi)
"""

gdbSampleTrace3 = """
Program terminated with signal 11, Segmentation fault.
#0  0x083ba5a9 in AssertCanGC () at /srv/repos/ionmonkey/js/src/gc/Root.h:1029
1029        JS_ASSERT_IF(isGCEnabled(), !InNoGCScope());
#0  0x083ba5a9 in AssertCanGC () at /srv/repos/ionmonkey/js/src/gc/Root.h:1029
#1  js::gc::NewGCThing<JSString, (js::AllowGC)1> (cx=0x9224850, kind=js::gc::FINALIZE_STRING, thingSize=16, heap=js::gc::TenuredHeap) at ../jsgcinlines.h:491
#2  0x083b205d in js_NewGCString<(js::AllowGC)1> (cx=0x9224850) at ../jsgcinlines.h:578
#3  0x08508069 in new_<(js::AllowGC)1> (length=33, right=\"result: \", left=\"\\njstest: undefined bug:  \", cx=0x9224850) at /srv/repos/ionmonkey/js/src/vm/String-inl.h:194
#4  js::ConcatStrings<(js::AllowGC)1> (cx=0x9224850,: left=\"\\njstest: undefined bug:  \", right=\"result: \") at /srv/repos/ionmonkey/js/src/vm/String.cpp:339
#5  0x08780467 in js::ion::DoConcatStrings (cx=0x9224850, lhs=$jsval(-nan(0xfff85f6bb4ff0)), rhs=$jsval(-nan(0xfff85f6c194e0)), res=$jsval(-nan(0xfff8200000000))) at /srv/repos/ionmonkey/js/src/ion/BaselineIC.cpp:2037
#6  0xf772685f in ?? ()
#7  0xf772bb76 in ?? ()
"""

gdbRegressionTrace1 = """
Program received signal SIGSEGV, Segmentation fault.
js::ScriptedIndirectProxyHandler::defineProperty (this=0x930fad4, cx=0x9339130, proxy=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), desc={obj = (JSObject *) 0xf6247040 [object Proxy], attrs = 61524, getter = 0xf6700120, setter = 0, value = $jsval(-nan(0xfff88f62460d0))}) at /srv/repos/mozilla-central/js/src/proxy/ScriptedIndirectProxyHandler.cpp:201
201         RootedObject handler(cx, GetIndirectProxyHandlerObject(proxy));
#0  js::ScriptedIndirectProxyHandler::defineProperty (this=0x930fad4, cx=0x9339130, proxy=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), desc={obj = (JSObject *) 0xf6247040 [object Proxy], attrs = 61524, getter = 0xf6700120, setter = 0, value = $jsval(-nan(0xfff88f62460d0))}) at /srv/repos/mozilla-central/js/src/proxy/ScriptedIndirectProxyHandler.cpp:201
#1  0x084ac820 in js::SetPropertyIgnoringNamedGetter (cx=0x9339130, handler=0x930fad4, proxy=(JSObject * const) 0xf6247040 [object Proxy], receiver=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), desc={obj = (JSObject *) 0xf6247040 [object Proxy], attrs = 61524, getter = 0xf6700120, setter = 0, value = $jsval(-nan(0xfff88f62460d0))}, descIsOwn=true, strict=false, vp=$jsval(-nan(0xfff88f62460d0))) at /srv/repos/mozilla-central/js/src/proxy/BaseProxyHandler.cpp:186
#2  0x084b0677 in js::ScriptedIndirectProxyHandler::derivedSet (this=0x930fad4, cx=0x9339130, proxy=(JSObject * const) 0xf6247040 [object Proxy], receiver=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), strict=false, vp=$jsval(-nan(0xfff88f62460d0))) at /srv/repos/mozilla-central/js/src/proxy/ScriptedIndirectProxyHandler.cpp:311
#3  0x084b08a8 in js::ScriptedIndirectProxyHandler::set (this=0x930fad4, cx=0x9339130, proxy=(JSObject * const) 0xf6247040 [object Proxy], receiver=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), strict=false, vp=$jsval(-nan(0xfff88f62460d0))) at /srv/repos/mozilla-central/js/src/proxy/ScriptedIndirectProxyHandler.cpp:290
#4  0x084aeb59 in js::Proxy::set (cx=0x9339130, proxy=(JSObject * const) 0xf6247040 [object Proxy], receiver=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), strict=false, vp=$jsval(-nan(0xfff88f62460d0))) at /srv/repos/mozilla-central/js/src/proxy/Proxy.cpp:336
#5  0x08535ec0 in setGeneric (strict=<optimized out>, vp=..., id=..., receiver=..., obj=(JSObject * const) 0xf6247040 [object Proxy], cx=0x9339130) at /srv/repos/mozilla-central/js/src/vm/NativeObject.h:1428
#6  js::baseops::SetPropertyHelper<(js::ExecutionMode)0> (cxArg=0x9339130, obj=(js::NativeObject * const) 0xf6700050 [object Array], receiver=(JSObject * const) 0xf6700050 [object Array], id=$jsid(0), qualified=js::baseops::Qualified, vp=$jsval(-nan(0xfff88f62460d0)), strict=false) at /srv/repos/mozilla-central/js/src/vm/NativeObject.cpp:2353
#7  0x08519490 in setGeneric (strict=false, vp=..., id=..., receiver=..., obj=(JSObject * const) 0xf6700050 [object Array], cx=0x9339130) at /srv/repos/mozilla-central/js/src/vm/NativeObject.h:1430
"""

gdbRegressionTrace2 = """
Program received signal SIGSEGV, Segmentation fault.
0xf7673132 in ?? ()
#0  0xf7673132 in ?? ()
eax            0xf6043040    -167497664
ecx            0xf651f4b0    -162401104
edx            0xf651f4d0    -162401072
ebx            0xf651f4f0    -162401040
esp            0xfffd573c    0xfffd573c
ebp            0xfffd57e4    0xfffd57e4
esi            0x0    0
edi            0x934d3d0    154457040
eip            0xf7673132    0xf7673132
=> 0xf7673132:    vmovaps %xmm1,0x60(%esp)
"""

gdbRegressionTrace3 = """
Program received signal SIGTRAP, Trace/breakpoint trap.
0x00007ffff5573368 in ?? ()
#0  0x00007ffff5573368 in ?? ()
#1  0x00007ffff558a9c9 in ?? ()
#2  0x0000000000000183 in ?? ()
#3  0x00007ffff5671ac0 in ?? ()
#4  0x0000000000000000 in ?? ()
rax    0x1ac4d40    28069184
rbx    0x7ffff5658730    140737310459696
rcx    0xfff9000000000000    -1970324836974592
rdx    0xfffc7ffff5700060    -985162595696544
rsi    0x7ffff55efa4d    140737310030413
rdi    0x1acfa60    28113504
rbp    0x7fffffffbf20    140737488338720
rsp    0x7fffffffbf28    140737488338728
r8    0x7ffff565b060    140737310470240
r9    0x0    0
r10    0x0    0
r11    0x7ffff6c3fc90    140737333427344
r12    0x0    0
r13    0x7fffffffca00    140737488341504
r14    0x183    387
r15    0x7ffff558a970    140737309616496
rip    0x7ffff5573368    140737309520744
=> 0x7ffff5573368:    movabs $0x7fffffffffff,%rbx
   0x7ffff5573372:    and    0xa08(%rax),%rbx
"""

gdbRegressionTrace4 = """
Program received signal SIGSEGV, Segmentation fault.
0x0000000000000000 in ?? ()
#0  0x0000000000000000 in ?? ()
#1 0xfffc7ffff7e8a6c0 in ?? ()
#2 0x000000000043026c in js::jit::IonCompile (cx=0xfffc7ffff7e766c0, script=<optimized out>, baselineFrame=<optimized out>, osrPc=<optimized out>, constructing=<optimized out>, recompile=<optimized out>, optimizationLevel=js::jit::Optimization_DontCompile) at /home/ownhero/homes/mozilla/repos/mozilla-central/js/src/jit/Ion.cpp:2253
#3 0x00007ffff7e61160 in ?? ()
#4 0x0000000000000000 in ?? ()
rax    0x0    0
rbx    0xfffc7ffff7e766c0    -985162554317120
rcx    0x7fffffffd6c0    140737488344768
rdx    0x7ffff6907050    140737330049104
rsi    0x0    0
rdi    0x7ffff6a00048    140737331069000
rbp    0x7fffffffd270    140737488343664
rsp    0x7fffffffd240    140737488343616
r8    0x0    0
r9    0xffffc000    4294950912
r10    0x46000    286720
r11    0x7ffff6a00121    140737331069217
r12    0x8    8
r13    0x7fffffffd6f0    140737488344816
r14    0x1    1
r15    0x7ffff6914800    140737330104320
rip    0x0    0
=> 0x0:    
"""

class ASanParserTestCrash(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = ASanCrashInfo([], asanTraceCrash.splitlines(), config)
        self.assertEqual(len(crashInfo.backtrace), 7)
        self.assertEqual(crashInfo.backtrace[0], "js::AbstractFramePtr::asRematerializedFrame() const")
        self.assertEqual(crashInfo.backtrace[2], "EvalInFrame(JSContext*, unsigned int, JS::Value*)")
        self.assertEqual(crashInfo.backtrace[6], "js::jit::DoCallFallback(JSContext*, js::jit::BaselineFrame*, js::jit::ICCall_Fallback*, unsigned int, JS::Value*, JS::MutableHandle<JS::Value>)")
        
        self.assertEqual(crashInfo.crashAddress, 0x00000014L)
        self.assertEqual(crashInfo.registers["pc"], 0x0810845fL)
        self.assertEqual(crashInfo.registers["sp"], 0xffc57860L)
        self.assertEqual(crashInfo.registers["bp"], 0xffc57f18L)

class ASanParserTestHeapCrash(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = ASanCrashInfo([], asanTraceHeapCrash.splitlines(), config)
        self.assertEqual(len(crashInfo.backtrace), 1)
        
        self.assertEqual(crashInfo.crashAddress, 0x00000019L)
        self.assertEqual(crashInfo.registers["pc"], 0xf718072eL)
        self.assertEqual(crashInfo.registers["sp"], 0xff87d130L)
        self.assertEqual(crashInfo.registers["bp"], 0x000006a1L)
        
        self.assertEqual(crashInfo.createShortSignature(), "[@ ??]")
        
class ASanParserTestUAF(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")

        crashInfo = ASanCrashInfo([], asanTraceUAF.splitlines(), config)
        self.assertEqual(len(crashInfo.backtrace), 23)
        self.assertEqual(crashInfo.backtrace[0], "void mozilla::PodCopy<char16_t>(char16_t*, char16_t const*, unsigned long)")
        self.assertEqual(crashInfo.backtrace[4], "JSFunction::native() const")
        
        self.assertEqual(crashInfo.crashAddress, 0x7fd766c42800L)
        
class ASanDetectionTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")

        crashInfo1 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=asanTraceCrash.splitlines())
        crashInfo2 = CrashInfo.fromRawCrashData([], asanTraceUAF.splitlines(), config)
        
        self.assertIsInstance(crashInfo1, ASanCrashInfo)
        self.assertIsInstance(crashInfo2, ASanCrashInfo)

class GDBParserTestCrash(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")

        crashInfo = GDBCrashInfo([], gdbSampleTrace1.splitlines(), config)
        self.assertEqual(len(crashInfo.backtrace), 8)
        self.assertEqual(crashInfo.backtrace[0], "internalAppend<js::ion::MDefinition*>")
        self.assertEqual(crashInfo.backtrace[2], "js::ion::MPhi::addInput")
        self.assertEqual(crashInfo.backtrace[6], "processCfgStack")

        self.assertEqual(crashInfo.registers["eax"], 0x0L)
        self.assertEqual(crashInfo.registers["ebx"], 0x8962ff4L)
        self.assertEqual(crashInfo.registers["eip"], 0x818bc33L)

class GDBParserTestCrashAddress(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")
        
        crashInfo1 = GDBCrashInfo([], gdbCrashAddress1.splitlines(), config)
        crashInfo2 = GDBCrashInfo([], gdbCrashAddress2.splitlines(), config)
        crashInfo3 = GDBCrashInfo([], gdbCrashAddress3.splitlines(), config)

        self.assertEqual(crashInfo1.crashAddress, 0x1L)
        self.assertEqual(crashInfo2.crashAddress, None)
        self.assertEqual(crashInfo3.crashAddress, 0xffffffffffffffa0L)

class GDBParserTestCrashAddressSimple(unittest.TestCase):
    def runTest(self):
        registerMap64 = {}
        registerMap64["rax"] = 0x0L
        registerMap64["rbx"] = -1L
        registerMap64["rsi"] = 0xde6e5L
        registerMap64["rdi"] = 0x7ffff6543238L
        
        registerMap32 = {}
        registerMap32["eax"] = 0x0L
        registerMap32["ebx"] = -1L
        registerMap32["ecx"] = 0xf75fffb8L
        
        # Simple tests
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %rbx,0x10(%rax)", registerMap64), 0x10L)
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %ebx,0x10(%eax)", registerMap32), 0x10L)
        
        
        # Overflow tests
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %rax,0x10(%rbx)", registerMap64), 0xFL)
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %eax,0x10(%ebx)", registerMap32), 0xFL)
        
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %rbx,-0x10(%rax)", registerMap64), int64(uint64(0xfffffffffffffff0L)))
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    %ebx,-0x10(%eax)", registerMap32), int32(uint32(0xfffffff0L)))
        
        # Scalar test
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("movl   $0x7b,0x0", registerMap32), 0x0L)
        
        # Real world examples
        # Note: The crash address here can also be 0xf7600000 because the double quadword 
        # move can fail on the second 8 bytes if the source address is not 16-byte aligned
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("movdqu 0x40(%ecx),%xmm4", registerMap32), int32(uint32(0xf75ffff8L)))
        
        # Again, this is an unaligned access and the crash can be at 0x7ffff6700000 or 0x7ffff6700000 - 4
        self.assertEqual(GDBCrashInfo.calculateCrashAddress("mov    -0x4(%rdi,%rsi,2),%eax", registerMap64), int64(uint64(0x7ffff66ffffeL)))

class GDBParserTestRegression1(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo1 = GDBCrashInfo([], gdbRegressionTrace1.splitlines(), config)

        self.assertEqual(crashInfo1.backtrace[0], "js::ScriptedIndirectProxyHandler::defineProperty")
        self.assertEqual(crashInfo1.backtrace[1], "js::SetPropertyIgnoringNamedGetter")

class GDBParserTestCrashAddressRegression2(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo2 = GDBCrashInfo([], gdbRegressionTrace2.splitlines(), config)
        
        self.assertEqual(crashInfo2.crashAddress, 0xfffd579cL)

class GDBParserTestCrashAddressRegression3(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")
        
        crashInfo3 = GDBCrashInfo([], gdbRegressionTrace3.splitlines(), config)
        
        self.assertEqual(crashInfo3.crashAddress, 0x7fffffffffffL)

class GDBParserTestCrashAddressRegression4(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")
        
        crashInfo4 = GDBCrashInfo([], gdbRegressionTrace4.splitlines(), config)
        
        self.assertEqual(crashInfo4.crashAddress, 0x0L)

class CrashSignatureOutputTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")
        
        crashSignature1 = '{ "symptoms" : [ { "type" : "output", "value" : "test" } ] }'
        crashSignature1Neg = '{ "symptoms" : [ { "type" : "output", "src" : "stderr", "value" : "test" } ] }'
        crashSignature2 = '{ "symptoms" : [ { "type" : "output", "src" : "stderr", "value" : { "value" : "^fest$", "matchType" : "pcre" } } ] }'
        
        outputSignature1 = CrashSignature(crashSignature1)
        outputSignature1Neg = CrashSignature(crashSignature1Neg)
        outputSignature2 = CrashSignature(crashSignature2)
        
        gdbOutput = []
        stdout = []
        stderr = []
        
        stdout.append("Foo")
        stdout.append("Bartester")
        stdout.append("Baz")
        stderr.append("hackfest")
        
        crashInfo = CrashInfo.fromRawCrashData(stdout, stderr, config, auxCrashData=gdbOutput)
        
        self.assertIsInstance(crashInfo, NoCrashInfo)
        
        # Ensure we match on stdout/err if nothing is specified
        self.assert_(outputSignature1.matches(crashInfo))
        
        # Don't match stdout if stderr is specified 
        self.assertFalse(outputSignature1Neg.matches(crashInfo))
        
        # Check that we're really using PCRE
        self.assertFalse(outputSignature2.matches(crashInfo))
        
        # Add something the PCRE should match, then retry
        stderr.append("fest")
        crashInfo = CrashInfo.fromRawCrashData(stdout, stderr, config, auxCrashData=gdbOutput)
        self.assert_(outputSignature2.matches(crashInfo))
        
class CrashSignatureAddressTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")

        crashSignature1 = '{ "symptoms" : [ { "type" : "crashAddress", "address" : "< 0x1000" } ] }'
        crashSignature1Neg = '{ "symptoms" : [ { "type" : "crashAddress", "address" : "0x1000" } ] }'
        addressSig1 = CrashSignature(crashSignature1)
        addressSig1Neg = CrashSignature(crashSignature1Neg)
        
        crashInfo1 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace1.splitlines())
        crashInfo3 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace3.splitlines())

        self.assertIsInstance(crashInfo1, GDBCrashInfo)
        
        self.assert_(addressSig1.matches(crashInfo1))
        self.assertFalse(addressSig1Neg.matches(crashInfo1))
        
        # For crashInfo3, we don't have a crash address. Ensure we don't match
        self.assertFalse(addressSig1.matches(crashInfo3))
        self.assertFalse(addressSig1Neg.matches(crashInfo3))
        
class CrashSignatureRegisterTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")
        
        crashSignature1 = '{ "symptoms" : [ { "type" : "instruction", "registerNames" : ["r14"] } ] }'
        crashSignature1Neg = '{ "symptoms" : [ { "type" : "instruction", "registerNames" : ["r14", "rax"] } ] }'
        crashSignature2 = '{ "symptoms" : [ { "type" : "instruction", "instructionName" : "mov" } ] }'
        crashSignature2Neg = '{ "symptoms" : [ { "type" : "instruction", "instructionName" : "cmp" } ] }'
        crashSignature3 = '{ "symptoms" : [ { "type" : "instruction", "instructionName" : "mov", "registerNames" : ["r14", "rbx"] } ] }'
        crashSignature3Neg = '{ "symptoms" : [ { "type" : "instruction", "instructionName" : "mov", "registerNames" : ["r14", "rax"] } ] }'
        
        instructionSig1 = CrashSignature(crashSignature1)
        instructionSig1Neg = CrashSignature(crashSignature1Neg)
        
        instructionSig2 = CrashSignature(crashSignature2)
        instructionSig2Neg = CrashSignature(crashSignature2Neg)
        
        instructionSig3 = CrashSignature(crashSignature3)
        instructionSig3Neg = CrashSignature(crashSignature3Neg)
        
        crashInfo2 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace2.splitlines())
        crashInfo3 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace3.splitlines())
        
        self.assertIsInstance(crashInfo2, GDBCrashInfo)
        self.assertIsInstance(crashInfo3, GDBCrashInfo)
        
        self.assert_(instructionSig1.matches(crashInfo2))
        self.assertFalse(instructionSig1Neg.matches(crashInfo2))
        
        self.assert_(instructionSig2.matches(crashInfo2))
        self.assertFalse(instructionSig2Neg.matches(crashInfo2))
        
        self.assert_(instructionSig3.matches(crashInfo2))
        self.assertFalse(instructionSig3Neg.matches(crashInfo2))
        
        # Crash info3 doesn't have register information, ensure we don't match any
        self.assertFalse(instructionSig1.matches(crashInfo3))
        self.assertFalse(instructionSig2.matches(crashInfo3))
        self.assertFalse(instructionSig3.matches(crashInfo3))

class CrashSignatureStackFrameTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")

        crashSignature1 = '{ "symptoms" : [ { "type" : "stackFrame", "functionName" : "internalAppend" } ] }'
        crashSignature1Neg = '{ "symptoms" : [ { "type" : "stackFrame", "functionName" : "foobar" } ] }'
        
        crashSignature2 = '{ "symptoms" : [ { "type" : "stackFrame", "functionName" : "js::ion::MBasicBlock::setBackedge", "frameNumber" : "<= 4" } ] }'
        crashSignature2Neg = '{ "symptoms" : [ { "type" : "stackFrame", "functionName" : "js::ion::MBasicBlock::setBackedge", "frameNumber" : "> 4" } ] }'
        
        stackFrameSig1 = CrashSignature(crashSignature1)
        stackFrameSig1Neg = CrashSignature(crashSignature1Neg)
        
        stackFrameSig2 = CrashSignature(crashSignature2)
        stackFrameSig2Neg = CrashSignature(crashSignature2Neg)
        
        crashInfo1 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace1.splitlines())
        
        self.assertIsInstance(crashInfo1, GDBCrashInfo)
        
        self.assert_(stackFrameSig1.matches(crashInfo1))
        self.assertFalse(stackFrameSig1Neg.matches(crashInfo1))
        
        self.assert_(stackFrameSig2.matches(crashInfo1))
        self.assertFalse(stackFrameSig2Neg.matches(crashInfo1))
        
class CrashSignatureStackSizeTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86-64", "linux")

        crashSignature1 = '{ "symptoms" : [ { "type" : "stackSize", "size" : 8 } ] }'
        crashSignature1Neg = '{ "symptoms" : [ { "type" : "stackSize", "size" : 9 } ] }'
        
        crashSignature2 = '{ "symptoms" : [ { "type" : "stackSize", "size" : "< 10" } ] }'
        crashSignature2Neg = '{ "symptoms" : [ { "type" : "stackSize", "size" : "> 10" } ] }'
        
        stackSizeSig1 = CrashSignature(crashSignature1)
        stackSizeSig1Neg = CrashSignature(crashSignature1Neg)
        
        stackSizeSig2 = CrashSignature(crashSignature2)
        stackSizeSig2Neg = CrashSignature(crashSignature2Neg)
        
        crashInfo1 = CrashInfo.fromRawCrashData([], [], config, auxCrashData=gdbSampleTrace1.splitlines())
        
        self.assertIsInstance(crashInfo1, GDBCrashInfo)
        
        self.assert_(stackSizeSig1.matches(crashInfo1))
        self.assertFalse(stackSizeSig1Neg.matches(crashInfo1))
        
        self.assert_(stackSizeSig2.matches(crashInfo1))
        self.assertFalse(stackSizeSig2Neg.matches(crashInfo1))

class RegisterHelperValueTest(unittest.TestCase):
    def runTest(self):
        registerMap = { "rax" : 0xfffffffffffffe00L, "rbx" : 0x7ffff79a7640L }
        
        self.assertEqual(RegisterHelper.getRegisterValue("rax", registerMap), 0xfffffffffffffe00L)
        self.assertEqual(RegisterHelper.getRegisterValue("eax", registerMap), 0xfffffe00L)
        self.assertEqual(RegisterHelper.getRegisterValue("ax", registerMap), 0xfe00L)
        self.assertEqual(RegisterHelper.getRegisterValue("ah", registerMap), 0xfeL)
        self.assertEqual(RegisterHelper.getRegisterValue("al", registerMap), 0x0L)
        
        self.assertEqual(RegisterHelper.getRegisterValue("rbx", registerMap), 0x7ffff79a7640L)
        self.assertEqual(RegisterHelper.getRegisterValue("ebx", registerMap), 0xf79a7640L)
        self.assertEqual(RegisterHelper.getRegisterValue("bx", registerMap), 0x7640L)
        self.assertEqual(RegisterHelper.getRegisterValue("bh", registerMap), 0x76L)
        self.assertEqual(RegisterHelper.getRegisterValue("bl", registerMap), 0x40L)

class MinidumpParserTestCrash(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        with open('minidump-example.txt', 'r') as f:
            crashInfo = MinidumpCrashInfo([], f.read().splitlines(), config)
            
        self.assertEqual(len(crashInfo.backtrace), 44)
        self.assertEqual(crashInfo.backtrace[0], "??")
        self.assertEqual(crashInfo.backtrace[5], "??")
        self.assertEqual(crashInfo.backtrace[6], "nsAppShell::ProcessNextNativeEvent(bool)")
        self.assertEqual(crashInfo.backtrace[7], "nsBaseAppShell::DoProcessNextNativeEvent(bool, unsigned int)")
        
        self.assertEqual(crashInfo.crashAddress, long(0x3e800006acb))

class MinidumpSelectorTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        with open('minidump-example.txt', 'r') as f:
            crashData = f.read().splitlines()
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, crashData)
        self.assertEqual(crashInfo.crashAddress, long(0x3e800006acb))


if __name__ == "__main__":
    unittest.main()
