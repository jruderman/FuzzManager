'''
AssertionHelper

Provides various functions around assertion handling and processing

@author:     Christian Holler (:decoder)

@license:

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

@contact:    choller@mozilla.com
'''

import re


def getAssertion(output, onlyProgramAssertions=False):
    '''
    This helper class provides a way to extract and process the
    different types of assertions from a given buffer.
    The problem here is that pretty much every software has its
    own type of assertions with different output formats.

    The "onlyProgramAssertions" boolean is to indicate that we
    are only interested in output from the program itself.
    Some aborts, like ASan or glibc, are not desirable in some
    cases, like signature generation and lead to incompatible
    signatures.

    @type output: list
    @param output: List of strings to be searched

    @type onlyProgramAssertions: bool
    @param onlyProgramAssertions: Boolean, see above
    '''
    lastLine = None
    addNext = False

    # Use this to ignore the ASan head line in case of an assertion
    haveFatalAssertion = False

    for line in output:
        # Remove any PID output at the beginning of the line
        line = re.sub("^\\[\\d+\\]\\s+", "", line, count=1)

        if addNext:
            lastLine += " "
            lastLine += line
        elif line.startswith("Assertion failure"):
            # Firefox JS assertion
            lastLine = line
            haveFatalAssertion = True
        elif line.startswith("###!!! ASSERTION:"):
            # Firefox assertion
            lastLine = line
            haveFatalAssertion = True
        elif line.startswith("# Fatal error in"):
            # Support v8 non-standard multi-line assertion output
            lastLine = line
            haveFatalAssertion = True
            addNext = True
        elif not onlyProgramAssertions and not haveFatalAssertion and "ERROR: AddressSanitizer" in line:
            lastLine = line
        elif "Assertion" in line and "failed" in line:
            # Firefox ANGLE assertion
            lastLine = line
        elif not onlyProgramAssertions and "glibc detected" in line:
            # Aborts caused by glibc runtime error detection
            lastLine = line
        elif "MOZ_CRASH" in line and re.search("MOZ_CRASH\(.+\)", line):
            # MOZ_CRASH line, but with a message (we should only look at these)
            lastLine = line

    return lastLine


def getSanitizedAssertionPattern(msg):
    '''
    This method provides a way to strip out unwanted dynamic information
    from assertions and replace it with pattern matching elements, e.g.
    for use in signature matching.

    @type msg: string
    @param msg: Assertion message to be sanitized

    @rtype: string
    @return: Sanitized assertion message (regular expression)
    '''
    assert msg != None

    sanitizedMsg = escapePattern(msg)

    replacementPatterns = []

    # Replace everything that looks like a memory address
    replacementPatterns.append("0x[0-9a-fA-F]+")

    # Strip line numbers as they can easily change across versions
    replacementPatterns.append(":[0-9]+")
    replacementPatterns.append(", line [0-9]+")

    # Strip full path
    replacementPatterns.append(" /.+/")

    for replacementPattern in replacementPatterns:
        sanitizedMsg = re.sub(replacementPattern, replacementPattern, sanitizedMsg)

    return sanitizedMsg


def escapePattern(msg):
    '''
    This method escapes regular expression characters in the string.
    And no, this is not re.escape, which would escape many more characters.

    @type msg: string
    @param msg: String that needs to be quoted

    @rtype: string
    @return: Escaped string for use in regular expressions
    '''

    escapedStr = msg

    activeChars = [ "\\", "[", "]", "{", "}", "(", ")", "*", "+", "-", "?", "^", "$", ".", "|" ]

    for activeChar in activeChars:
        escapedStr = escapedStr.replace(activeChar, "\\" + activeChar)

    return escapedStr
