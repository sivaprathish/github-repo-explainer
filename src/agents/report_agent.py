from __future__ import annotations

from src.agents.common import run_agent


def generate_final_report(context: str) -> str:
    """
    Generate the final combined repository report.
    """

    return run_agent(
        role="repository technical reviewer",
        instructions="""
Create a final repository analysis report using the supplied
documentation report, architecture report, and static-analysis findings.

The report must contain:

# Repository Analysis

## Executive Summary
Give a concise explanation of the repository.

## Main Strengths
List evidence-based strengths.

## Code Quality
Explain:
- TODO and FIXME markers
- Large files
- Empty files
- Missing tests
- Maintainability concerns
- Other supplied static-analysis findings

## Risks and Limitations
Explain important technical risks.

## Recommended Improvements
Give prioritized, actionable improvements.

## Conclusion
Provide a concise final assessment.

Avoid repeating full sections from the previous reports.
Do not invent issues that are not present in the evidence.
""",
        context=context,
        run_name="final-report-agent",
    )