"""Prompts sent to Bob. Kept in one place so the transcripts are easy to read against them."""

GENERATE_TESTS = """You are writing characterization tests for a legacy Java class before it is modernized.

Goal: pin down what the code DOES today, including odd behaviour, so any change in behaviour
during modernization makes a test fail. Do not test what the comments say it should do; test
what it actually does. Where the code and its javadoc disagree, the code wins.

Requirements:
- One JUnit 5 test class named `{test_class}` in package `com.acme.billing`.
- Use only JUnit 5 (org.junit.jupiter.api) and the JDK. No other libraries.
- Call only the public API of `InvoiceCalculator` shown below; keep test inputs deterministic.
- Cover boundaries (e.g. quantities around discount thresholds), rounding of half-cent values,
  input normalisation (whitespace, letter case, null), error cases, and date edge cases.
- Every test must pass against the code exactly as written below.
- Reply with the complete test class in a single ```java code block.

```java
{source}
```
"""

FIX_TESTS = """Some of your characterization tests fail against the ORIGINAL, unmodified code, which means
they assert behaviour the code does not have. Fix those assertions to match what the code
actually does (or remove a test only if its behaviour cannot be pinned deterministically).
Keep every passing test. Reply with the complete corrected `{test_class}` in one ```java block.

Failures:
{failures}

Your previous test class:
```java
{tests}
```

The original code:
```java
{source}
```
"""

MODERNIZE = """Modernize this legacy Java class.

Request from the developer: {goal}

Rules:
- Keep the class name, package, and every public method signature unchanged so callers compile.
- Reply with the complete modernized `InvoiceCalculator` in a single ```java code block.

```java
{source}
```
"""

REPAIR = """The characterization suite blocked your modernization: it changed behaviour that finance
depends on. Keep the modern style, but restore the exact original behaviour so every test passes.
Do not change the tests. Keep the class name, package and public method signatures.
Reply with the complete corrected `InvoiceCalculator` in a single ```java code block.

Failing tests:
{failures}

Your modernized version:
```java
{candidate}
```

The original legacy code (the behaviour to preserve):
```java
{source}
```
"""

HARDEN = """Your characterization suite let some behaviour changes slip through. Each change below
alters one behaviour of the original code, yet all your tests still passed. Add tests that pin
down the ORIGINAL behaviour so each of these changes would fail. Keep every existing test.
Reply with the complete `{test_class}` in one ```java block.

Changes your suite missed:
{survivors}

Your current test class:
```java
{tests}
```

The original code:
```java
{source}
```
"""
