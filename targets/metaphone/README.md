# Target: Metaphone (Apache Commons Codec 1.3)

Real open-source legacy code: `Metaphone.java` and the three small interfaces it needs are copied
**unmodified** from `commons-codec-1.3-sources.jar` on Maven Central (released 2005), under the
Apache License 2.0 (see `LICENSE.txt`). Copyright The Apache Software Foundation.

`MetaphoneControlTest` pins the outputs of the unmodified code; `mutants.json` lists five
plausible "simplifications" that each silently change behaviour.
