# Target: Base64 (Apache Commons Codec 1.3)

Real open-source legacy code: `Base64.java` and the six small interfaces/exceptions it needs are
copied **unmodified** from `commons-codec-1.3-sources.jar` on Maven Central (released 2005), under
the Apache License 2.0 (see `LICENSE.txt`). Copyright The Apache Software Foundation.

Why it is a good test: the most common real-world ticket for a class like this is "replace our
hand-rolled Base64 with `java.util.Base64`", and that swap silently changes behaviour:

| Input | Commons Codec 1.3 | `java.util.Base64` (basic) |
|---|---|---|
| `"aGVs bG8="` (space) | `hello` (skipped) | throws |
| `"aGVs!!bG8="` (junk) | `hello` (skipped) | throws |
| `"aGVsbG8"` (no padding) | `hel` + three NUL bytes (a genuine 2005 bug) | `hello` |
| `"="` | empty | throws |
| chunked `"abc"` | `YWJj\r\n` (always ends with CRLF) | MIME encoder: `YWJj` |

`Base64ControlTest` pins the original behaviour; `mutants.json` breaks five of these behaviours one at a time.
