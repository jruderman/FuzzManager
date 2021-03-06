'''
Created on Oct 9, 2014

@author: decoder
'''
import unittest
from FTB.Signatures.CrashInfo import CrashInfo
import json
from FTB.ProgramConfiguration import ProgramConfiguration
from FTB.Signatures.CrashSignature import CrashSignature
from FTB.Signatures.Matchers import StringMatch
from FTB.Signatures.Symptom import StackFramesSymptom

testTrace1 = """Program received signal SIGSEGV, Segmentation fault.
GetObjectAllocKindForCopy (obj=0x7ffff54001b0, nursery=...) at /srv/repos/mozilla-central/js/src/gc/Nursery.cpp:369
369         if (obj->is<ArrayObject>()) {
#0  GetObjectAllocKindForCopy (obj=0x7ffff54001b0, nursery=...) at /srv/repos/mozilla-central/js/src/gc/Nursery.cpp:369
#1  js::Nursery::moveToTenured (this=0x1673be0, trc=0x7fffffffa2d0, src=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Nursery.cpp:570
#2  0x00000000004d167a in MinorGCCallback (thingp=0x7fffffff9fd0, jstrc=<optimized out>, kind=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Nursery.cpp:721
#3  js::Nursery::MinorGCCallback (jstrc=<optimized out>, thingp=0x7fffffff9fd0, kind=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Nursery.cpp:717
#4  0x00000000004b8690 in MarkInternal<JSObject> (trc=0x7fffffffa2d0, thingp=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:317
#5  0x00000000004cc55e in MarkValueInternal (v=0x7fffffffa5d8, trc=0x7fffffffa2d0) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:804
#6  MarkValueInternal (v=0x7fffffffa5d8, trc=0x7fffffffa2d0) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:827
#7  js::gc::MarkValueRoot (trc=<optimized out>, v=0x7fffffffa5d8, name=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:831
rax     0x2b2b2b2b      3110627432037296939
rbx     0xf54001b0      140737308000688
rcx     0xbad0bad1      3134241489
rdx     0x1656120       23421216
rsi     0xffffa2d0      140737488331472
rdi     0x1673be0       23542752
rbp     0xf54001b0      140737308000688
rsp     0xffff9f10      140737488330512
r8      0x0     0
r9      0x0     0
r10     0x1     1
r11     0x1     1
r12     0x0     -1266637395197952
r13     0xffffa2d0      140737488331472
r14     0x1673be0       23542752
r15     0x201   513
rip     0x4d0b32 <js::Nursery::moveToTenured(js::gc::MinorCollectionTracer*, JSObject*)+34>
=> 0x4d0b32 <js::Nursery::moveToTenured(js::gc::MinorCollectionTracer*, JSObject*)+34>: mov    (%rax),%r8
"""

testTrace2 = """Program terminated with signal 11, Segmentation fault.
#0  JSObject::markChildren (this=0x7fc33ef5a060, trc=0x3538be0)
    at /srv/repos/mozilla-central/js/src/jsobj.cpp:4081
4081        if (clasp->trace)
Loading JavaScript value pretty-printers; see js/src/gdb/README.
If they cause trouble, type: disable pretty-printer .* SpiderMonkey
#0  JSObject::markChildren (this=(JSObject * const) 0x7fc33ef5a060 Cannot access memory at address 0x4949494949494949, trc=0x3538be0) at /srv/repos/mozilla-central/js/src/jsobj.cpp:4081
#1  0x00000000004e11e3 in MarkChildren (obj=(JSObject *) 0x7fc33ef5a060 Cannot access memory at address 0x4949494949494949, trc=0x3538be0) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:1323
#2  js::TraceChildren (trc=0x3538be0, thing=0x7fc33ef5a060, kind=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Marking.cpp:1934
#3  0x0000000000625d87 in js::gc::GCRuntime::startVerifyPreBarriers (this=this@entry=0x33ac568) at /srv/repos/mozilla-central/js/src/gc/Verifier.cpp:239
#4  0x0000000000633a5e in maybeVerifyPreBarriers (always=<optimized out>, this=0x33ac568) at /srv/repos/mozilla-central/js/src/gc/Verifier.cpp:563
#5  js::gc::MaybeVerifyBarriers (cx=<optimized out>, always=<optimized out>) at /srv/repos/mozilla-central/js/src/gc/Verifier.cpp:588
#6  0x00000000007c8660 in js::jit::CheckOverRecursedWithExtra (cx=0x33ce390, frame=<optimized out>, extra=<optimized out>, earlyCheck=<optimized out>) at /srv/repos/mozilla-central/js/src/jit/VMFunctions.cpp:153
#7  0x00007fc33ee95394 in ?? ()
#8  0x0000000000000000 in ?? ()
rax    0x4949494949494949    5280832617179597129
rbx    0x7fc33ef5a060    140476551635040
rcx    0x4949494949494949    5280832617179597129
rdx    0x4    4
rsi    0xa8ae16    11054614
rdi    0x3538be0    55806944
rbp    0x3538be0    55806944
rsp    0x7fff9aec80c0    140735792578752
r8    0x0    0
r9    0x2cd1    11473
r10    0x37d2580    58533248
r11    0x4000    16384
r12    0x7fc3240c5030    140476100137008
r13    0x2    2
r14    0x7fc3240c4ff0    140476100136944
r15    0x0    0
rip    0x84de35 <JSObject::markChildren(JSTracer*)+53>
=> 0x84de35 <JSObject::markChildren(JSTracer*)+53>:    mov    (%rax),%rax
   0x84de38 <JSObject::markChildren(JSTracer*)+56>:    mov    0x68(%rax),%rax
"""

testSignature1 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
    {
    "functionName": "MinorGCCallback",
    "frameNumber": 2,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::MinorGCCallback",
    "frameNumber": 3,
    "type": "stackFrame"
  },
    {
    "address": "0x2b2b2b2b",
    "type": "crashAddress"
  }
]}
'''

testSignature2 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
    {
    "functionName": "MinorGCCallback",
    "frameNumber": 2,
    "type": "stackFrame"
  }
]}
'''

testSignature3 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
  {
    "address": "0x2b2b2b2b",
    "type": "crashAddress"
  },
    {
    "type": "instruction",
    "instructionName": "mov    (%rax),%r8"
  }
]}
'''

testSignature4 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
    {
    "type": "testcase", 
    "value": {
      "matchType": "pcre", 
      "value": "SIMD\\\.float\\\d+x"
    }
  }
]}
'''

testSignature5 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
    {
    "type": "testcase", 
    "value": "SIMD.float32x4"
  }
]}
'''

testSignature6 = '''{"symptoms": [
    {
    "functionName": "GetObjectAllocKindForCopy",
    "frameNumber": 0,
    "type": "stackFrame"
  },
    {
    "functionName": "js::Nursery::moveToTenured",
    "frameNumber": 1,
    "type": "stackFrame"
  },
    {
    "type": "testcase", 
    "value": "SIMD.float64x4"
  }
]}
'''

testCase1 = '''
function test() {
  var a = SIMD.float32x4();
  if (typeof reportCompare === "function")
    reportCompare(true, true);
}
test();
'''

testSignatureStackFrames1 = '''{"symptoms": [
    {
    "type": "stackFrames", 
    "functionNames": [ "GetObjectAllocKindForCopy", "moveToTenured", "?", "MinorGCCallback", "MarkInternal<JSObject>" ]
  }
]}
'''

testSignatureStackFrames2 = '''{"symptoms": [
    {
    "type": "stackFrames", 
    "functionNames": [ "GetObjectAllocKindForCopy", "moveToTenured", "?", "MinorGCCallback", "MinorGCCallback", "MarkInternal<JSObject>" ]
  }
]}
'''

testSignatureStackFrames3 = '''{"symptoms": [
    {
    "type": "stackFrames", 
    "functionNames": [ "GetObjectAllocKindForCopy", "moveToTenured", "?", "?", "MarkInternal<JSObject>" ]
  }
]}
'''

testSignatureStackFrames4 = '''{"symptoms": [
    {
    "type": "stackFrames", 
    "functionNames": [ "GetObjectAllocKindForCopy", "moveToTenured", "???", "MarkInternal<JSObject>" ]
  }
]}
'''

testSignatureStackFrames5 = '''{"symptoms": [
    {
    "type": "stackFrames", 
    "functionNames": [ "GetObjectAllocKindForCopy", "moveToTenured", "?", "MarkInternal<JSObject>" ]
  }
]}
'''


testSignaturePCREShort1 = '''{"symptoms": [
    {
    "functionName": "/.+KindForCopy/",
    "type": "stackFrame"
  }
]}
'''

testSignaturePCREShort2 = '''{"symptoms": [
    {
    "functionName": "/^.KindForCopy/",
    "type": "stackFrame"
  }
]}
'''

class SignatureCreateTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, auxCrashData=testTrace1.splitlines())
        crashSig1 = crashInfo.createCrashSignature(forceCrashAddress=True, maxFrames=4, minimumSupportedVersion=10)
        crashSig2 = crashInfo.createCrashSignature(forceCrashAddress=False, maxFrames=3, minimumSupportedVersion=10)
        crashSig3 = crashInfo.createCrashSignature(forceCrashInstruction=True, maxFrames=2, minimumSupportedVersion=10)

        # Check that all generated signatures match their originating crashInfo
        self.assert_(crashSig1.matches(crashInfo))
        self.assert_(crashSig2.matches(crashInfo))
        self.assert_(crashSig3.matches(crashInfo))
        
        # Check that the generated signatures look as expected
        self.assertEqual(json.loads(str(crashSig1)), json.loads(testSignature1))
        self.assertEqual(json.loads(str(crashSig2)), json.loads(testSignature2))
        
        #  The third crashInfo misses 2 frames from the top 4 frames, so it will
        #  also include the crash address, even though we did not request it.
        self.assertEqual(json.loads(str(crashSig3)), json.loads(testSignature3))

class SignatureTestCaseMatchTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, auxCrashData=testTrace1.splitlines())
        
        testSig3 = CrashSignature(testSignature3)
        testSig4 = CrashSignature(testSignature4)
        testSig5 = CrashSignature(testSignature5)
        testSig6 = CrashSignature(testSignature6)
        
        self.assertFalse(testSig3.matchRequiresTest())
        self.assertTrue(testSig4.matchRequiresTest())
        self.assertTrue(testSig5.matchRequiresTest())
        
        # Must not match without testcase provided
        self.assertFalse(testSig4.matches(crashInfo))
        self.assertFalse(testSig5.matches(crashInfo))
        self.assertFalse(testSig6.matches(crashInfo))
        
        # Attach testcase
        crashInfo.testcase = testCase1

        # Must match with testcase provided
        self.assertTrue(testSig4.matches(crashInfo))
        self.assertTrue(testSig5.matches(crashInfo))
        
        # This one does not match at all
        self.assertFalse(testSig6.matches(crashInfo))

class SignatureStackFramesTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, auxCrashData=testTrace1.splitlines())
        
        testSig1 = CrashSignature(testSignatureStackFrames1)
        testSig2 = CrashSignature(testSignatureStackFrames2)
        testSig3 = CrashSignature(testSignatureStackFrames3)
        testSig4 = CrashSignature(testSignatureStackFrames4)
        testSig5 = CrashSignature(testSignatureStackFrames5)
        
        self.assertTrue(testSig1.matches(crashInfo))
        self.assertTrue(testSig2.matches(crashInfo))
        self.assertTrue(testSig3.matches(crashInfo))
        self.assertTrue(testSig4.matches(crashInfo))
        self.assertFalse(testSig5.matches(crashInfo))

class SignatureStackFramesAlgorithmsTest(unittest.TestCase):
    def runTest(self):      
        # Do some direct matcher tests on edge cases
        self.assertTrue(StackFramesSymptom._match([], [StringMatch('???')]))
        self.assertFalse(StackFramesSymptom._match([], [StringMatch('???'), StringMatch('a')]))
        
        # Test the diff algorithm, test array contains:
        # stack, signature, expected distance, proposed signature
        testArray = [
                     (['a', 'b', 'x', 'a', 'b', 'c'], ['a', 'b', '???', 'a', 'b', 'x', 'c'], 1, ['a', 'b', '???', 'a', 'b', '?', 'c']),
                     (['b', 'x', 'a', 'b', 'c'], ['a', 'b', '???', 'a', 'b', 'x', 'c'], 2, ['?', 'b', '???', 'a', 'b', '?', 'c']),
                     (['b', 'x', 'a', 'd', 'x'], ['a', 'b', '???', 'a', 'b', 'x', 'c'], 3, ['?', 'b', '???', 'a', '?', 'x', '?']),
                     ]
        
        for (stack, rawSig, expectedDepth, expectedSig) in testArray:
            for maxDepth in (expectedDepth, 3):
                (actualDepth, actualSig) = StackFramesSymptom._diff(stack, [ StringMatch(x) for x in rawSig ], 0, 1, maxDepth)
                self.assertEqual(expectedDepth, actualDepth)
                self.assertEqual(expectedSig, [ str(x) for x in actualSig ])

class SignaturePCREShortTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, auxCrashData=testTrace1.splitlines())
        
        testSig1 = CrashSignature(testSignaturePCREShort1)
        testSig2 = CrashSignature(testSignaturePCREShort2)
        
        self.assertTrue(testSig1.matches(crashInfo))
        self.assertFalse(testSig2.matches(crashInfo))

class SignatureStackFramesWildcardTailTest(unittest.TestCase):
    def runTest(self):
        config = ProgramConfiguration("test", "x86", "linux")
        
        crashInfo = CrashInfo.fromRawCrashData([], [], config, auxCrashData=testTrace2.splitlines())
        
        testSig = crashInfo.createCrashSignature()
        
        # Ensure that the last frame with a symbol is at the right place and there is nothing else,
        # espcially no wildcard, following afterwards.
        self.assertTrue(isinstance(testSig.symptoms[0], StackFramesSymptom))
        self.assertEqual(str(testSig.symptoms[0].functionNames[6]), "js::jit::CheckOverRecursedWithExtra")
        self.assertEqual(len(testSig.symptoms[0].functionNames), 7)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()