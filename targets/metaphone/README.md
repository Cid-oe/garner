# Target: Metaphone (Apache Commons Codec 1.3)

Real open-source legacy code: `Metaphone.java` and the three small interfaces it needs are copied
**unmodified** from `commons-codec-1.3-sources.jar` on Maven Central (released 2005), under the
Apache License 2.0 (see `LICENSE.txt`). Copyright The Apache Software Foundation.

`MetaphoneControlTest` pins the outputs of the unmodified code; `mutants.json` lists five
plausible "simplifications" that each silently change behaviour.

## Differential check

Independent of any test suite, `differential/check.sh runs/<id>` rebuilds Bob's modernized versions
from a run's recorded diffs and runs them and the original on 136,800 deterministic inputs
(random words, combinations of the letter groups Metaphone special-cases, mixed case and
punctuation), comparing every output including exceptions.

Run `20260926-122205` (SRCH-431): **0 of 136,800 outputs differ** for both Bob refactors,
including the 44 inputs on which the original throws; Bob's versions throw the same exceptions.
