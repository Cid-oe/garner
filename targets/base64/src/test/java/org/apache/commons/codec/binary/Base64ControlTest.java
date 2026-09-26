package org.apache.commons.codec.binary;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

/**
 * Hand-written control tests: outputs of the unmodified Commons Codec 1.3 Base64,
 * one per behaviour that harness mutants break. Bob's suite is scored on the same mutants.
 */
class Base64ControlTest {

    private static byte[] b(String s) {
        return s.getBytes(StandardCharsets.ISO_8859_1);
    }

    private static String str(byte[] bytes) {
        return new String(bytes, StandardCharsets.ISO_8859_1);
    }

    /** B1: decoding skips whitespace and junk instead of rejecting it. */
    @Test
    void decodeSkipsNonBase64Characters() {
        assertEquals("hello", str(Base64.decodeBase64(b("aGVs bG8="))));
        assertEquals("hello", str(Base64.decodeBase64(b("aGVs\r\nbG8="))));
        assertEquals("hello", str(Base64.decodeBase64(b("aGVs!!bG8="))));
    }

    /** Legacy quirk kept as-is: unpadded input decodes to trailing NUL bytes. */
    @Test
    void unpaddedInputGivesTrailingNuls() {
        assertArrayEquals(new byte[] {'h', 'e', 'l', 0, 0, 0}, Base64.decodeBase64(b("aGVsbG8")));
    }

    /** B2 + B3: chunked output uses CRLF and always ends with it. */
    @Test
    void chunkedOutputEndsWithCrlf() {
        assertEquals("YWJj\r\n", str(Base64.encodeBase64Chunked(b("abc"))));
    }

    /** B5: chunked lines are 76 characters long. */
    @Test
    void chunkedLinesAre76Characters() {
        byte[] data = new byte[60];
        for (int i = 0; i < data.length; i++) {
            data[i] = (byte) i;
        }
        String out = str(Base64.encodeBase64Chunked(data));
        assertEquals(76, out.indexOf("\r\n"));
        assertTrue(out.endsWith("\r\n"));
    }

    /** B4: whitespace counts as valid Base64, junk does not. */
    @Test
    void isArrayByteBase64AllowsWhitespace() {
        assertTrue(Base64.isArrayByteBase64(b("aGVs bG8=")));
        assertFalse(Base64.isArrayByteBase64(b("aGVs!bG8=")));
    }

    @Test
    void plainRoundTrip() {
        assertEquals("aGVsbG8=", str(Base64.encodeBase64(b("hello"))));
        assertEquals("hello", str(Base64.decodeBase64(b("aGVsbG8="))));
        assertEquals("", str(Base64.decodeBase64(b(""))));
    }
}
