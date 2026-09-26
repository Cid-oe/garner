FIXTURE (hand-written, not Bob).

```java
package org.apache.commons.codec.language;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

/**
 * Hand-written control tests: outputs of the unmodified Commons Codec 1.3 Metaphone,
 * one per special case that harness/mutants.json breaks. Bob's characterization suite
 * is scored against the same mutants.
 */
class MetaphoneCharacterizationTest {

    private final Metaphone m = new Metaphone();

    @Test
    void emptyAndNull() {
        assertEquals("", m.metaphone(null));
        assertEquals("", m.metaphone(""));
    }

    /** M2: one letter is returned upper-cased, without running the algorithm. */
    @Test
    void singleLetter() {
        assertEquals("A", m.metaphone("A"));
        assertEquals("B", m.metaphone("b"));
    }

    /** M1: duplicate letters are skipped, except C. */
    @Test
    void duplicateCIsKept() {
        assertEquals("AKSP", m.metaphone("ACCEPT"));
    }

    /** M3: initial X sounds like S. */
    @Test
    void initialX() {
        assertEquals("SFR", m.metaphone("XAVIER"));
    }

    /** M4: initial WH becomes W. */
    @Test
    void initialWH() {
        assertEquals("WT", m.metaphone("WHITE"));
    }

    /** M5: T in TCH is silent. */
    @Test
    void silentTInTCH() {
        assertEquals("MX", m.metaphone("MATCH"));
    }

    @Test
    void assortedWords() {
        assertEquals("NT", m.metaphone("KNIGHT"));
        assertEquals("SKL", m.metaphone("SCHOOL"));
        assertEquals("0MS", m.metaphone("THOMAS"));
        assertEquals("FN", m.metaphone("PHONE"));
        assertEquals("NM", m.metaphone("GNOME"));
        assertEquals("TJ", m.metaphone("DODGE"));
        assertEquals("RT", m.metaphone("WRIGHT"));
    }
}
```
