"""bob-bridge command line."""

import argparse
import sys

from . import pipeline, report
from .bob import BobError

BENIGN_GOAL = ("Bring this class up to modern Java 21: generics instead of raw collections, "
               "java.time instead of Calendar, StringBuilder, no deprecated APIs. "
               "Behaviour must stay exactly the same.")

REGRESSION_GOAL = ("Modernize to Java 21 and clean it up: replace the deprecated BigDecimal.ROUND_HALF_EVEN with "
                   "RoundingMode.HALF_UP, turn the customer-type if/else chain into a switch expression, and make "
                   "the volume discount match its javadoc (10 or more units).")


def probe(mode):
    from .bob import ask
    from .javaproj import extract_java
    ex = ask("probe", "Reply with a single ```java code block containing exactly: public class Ping {} "
                      "and nothing else. Do not create or edit any files.", mode, timeout=300)
    print(f"[bridge] Bob answered in {ex.seconds:.1f}s via: {ex.command}")
    try:
        extract_java(ex.response, "class Ping")
        print("[bridge] OK: parseable Java found. Phase 1 passes.")
    except ValueError:
        print("[bridge] Bob answered, but no ```java block with `class Ping` was found. Raw reply:\n")
        print(ex.response[:2000])
        return 3
    print(f"[bridge] transcript: {ex.transcript}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="bob-bridge", description="Bob-driven legacy modernization behind a characterization-test gate.")
    p.add_argument("--mode", choices=["cli", "replay", "fixture"], help="how to reach Bob (default: $BRIDGE_MODE or cli)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("probe", help="Phase 1: check Bob answers a scripted prompt with parseable Java, and time it")
    sub.add_parser("generate-tests", help="R1: Bob writes a characterization suite for the legacy file")
    m = sub.add_parser("modernize", help="R2/R3: Bob modernizes; applied only if the suite still passes")
    m.add_argument("--goal", default=BENIGN_GOAL)
    m.add_argument("--step", default="modernize", help="name for this attempt (used for transcripts and replay)")
    sub.add_parser("report", help="R4: write the standalone HTML report for the latest run")
    sub.add_parser("demo", help="full pipeline: tests, a benign modernization, a regression, report")

    args = p.parse_args(argv)
    try:
        if args.cmd == "probe":
            return probe(args.mode)
        if args.cmd == "generate-tests":
            run = pipeline.Run()
            pipeline.generate_tests(run, args.mode)
        elif args.cmd == "modernize":
            run = pipeline.Run.latest()
            pipeline.modernize(run, args.goal, args.step, args.mode)
        elif args.cmd == "report":
            run = pipeline.Run.latest()
        elif args.cmd == "demo":
            run = pipeline.Run()
            pipeline.generate_tests(run, args.mode)
            pipeline.modernize(run, BENIGN_GOAL, "modernize-benign", args.mode)
            pipeline.modernize(run, REGRESSION_GOAL, "modernize-regression", args.mode)
        print(f"[bridge] report: {report.write(run)}")
    except BobError as e:
        print(f"[bridge] Bob call failed: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
