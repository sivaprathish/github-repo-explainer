from __future__ import annotations

import traceback
from typing import Any

import pandas as pd
import streamlit as st

from src.services.analysis_service import AnalysisService
from src.services.chat_service import ChatService


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="GitHub Repository Explainer",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .app-title {
            font-size: 2.35rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .app-subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .repo-card {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1rem;
        }

        .section-card {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }

        .small-muted {
            color: #6b7280;
            font-size: 0.9rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 12px;
            padding: 0.75rem 0.9rem;
            background: rgba(128, 128, 128, 0.03);
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .status-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.2rem 0.65rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            background: rgba(46, 160, 67, 0.12);
            border: 1px solid rgba(46, 160, 67, 0.30);
            font-size: 0.82rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Session state
# ============================================================

def initialize_state() -> None:
    defaults = {
        "analysis": None,
        "chat_service": None,
        "chat_repository": None,
        "messages": [],
        "error": None,
        "last_repository_url": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# Cached services
# ============================================================

@st.cache_resource(show_spinner=False)
def analyze_repository_cached(repo_url: str) -> dict[str, Any]:
    return AnalysisService().analyze(repo_url)


def initialize_chat_service(result: dict[str, Any]) -> ChatService:
    repository_name = (
        result["repository_data"].metadata.full_name
    )

    if (
        st.session_state.chat_service is None
        or st.session_state.chat_repository != repository_name
    ):
        st.session_state.chat_service = ChatService(
            repository_name=repository_name,
            files=result["files"],
        )

        st.session_state.chat_repository = repository_name

    return st.session_state.chat_service


def clear_analysis() -> None:
    st.session_state.analysis = None
    st.session_state.chat_service = None
    st.session_state.chat_repository = None
    st.session_state.messages = []
    st.session_state.error = None
    st.session_state.last_repository_url = ""


def to_rows(items: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for item in items:
        if hasattr(item, "model_dump"):
            rows.append(item.model_dump())
        elif isinstance(item, dict):
            rows.append(item)

    return rows


def format_datetime(value: Any) -> str:
    if value is None:
        return "Not available"

    try:
        return value.strftime("%d %b %Y, %I:%M %p")
    except AttributeError:
        return str(value)


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="app-title">GitHub Repository Explainer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-subtitle">
        Multi-agent repository analysis using LangGraph, LangChain,
        NVIDIA, LangSmith and retrieval-augmented generation.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.header("Repository Input")

    with st.form("repository_form"):
        repo_url = st.text_input(
            "GitHub repository URL",
            value=st.session_state.last_repository_url,
            placeholder="https://github.com/owner/repository",
            help=(
                "Enter the complete URL of a public repository "
                "or a private repository accessible through your token."
            ),
        )

        analyze_button = st.form_submit_button(
            "Analyze repository",
            type="primary",
            use_container_width=True,
        )

    if st.session_state.analysis is not None:
        if st.button(
            "Clear current analysis",
            use_container_width=True,
        ):
            clear_analysis()
            st.rerun()

    st.divider()

    st.markdown("### Analysis Pipeline")

    st.caption(
        "1. GitHub metadata\n\n"
        "2. Clone and scan\n\n"
        "3. Static analysis\n\n"
        "4. Documentation agent\n\n"
        "5. Architecture agent\n\n"
        "6. Final report"
    )

    st.divider()

    st.caption(
        "RAG indexing is created only when the first repository "
        "question is asked."
    )


# ============================================================
# Run analysis
# ============================================================

if analyze_button:
    cleaned_url = repo_url.strip()

    if not cleaned_url:
        st.warning("Enter a GitHub repository URL.")

    elif not cleaned_url.startswith(
        ("https://github.com/", "http://github.com/")
    ):
        st.warning("Enter a valid github.com repository URL.")

    else:
        st.session_state.error = None
        st.session_state.chat_service = None
        st.session_state.chat_repository = None
        st.session_state.messages = []
        st.session_state.last_repository_url = cleaned_url

        try:
            with st.status(
                "Analyzing repository...",
                expanded=True,
            ) as status:
                st.write("Fetching GitHub metadata")
                st.write("Cloning repository")
                st.write("Scanning important files")
                st.write("Running parallel static analysis")
                st.write("Generating documentation report")
                st.write("Generating architecture report")
                st.write("Generating final technical report")

                result = analyze_repository_cached(cleaned_url)

                st.session_state.analysis = result

                status.update(
                    label="Repository analysis completed",
                    state="complete",
                    expanded=False,
                )

        except Exception as error:
            st.session_state.error = str(error)

            with st.expander(
                "Technical error details",
                expanded=False,
            ):
                st.code(
                    traceback.format_exc(),
                    language="text",
                )


# ============================================================
# Error display
# ============================================================

if st.session_state.error:
    st.error(st.session_state.error)


# ============================================================
# Empty state
# ============================================================

result = st.session_state.analysis

if not result:
    left_column, right_column = st.columns(
        [1.2, 1],
        gap="large",
    )

    with left_column:
        st.info(
            "Enter a GitHub repository URL in the sidebar and "
            "select **Analyze repository**."
        )

        st.markdown("### Available Analysis")

        feature_rows = [
            {
                "Feature": "Repository Analysis",
                "Description": "Reads repository metadata and source files.",
            },
            {
                "Feature": "Technology Stack",
                "Description": "Detects languages, frameworks and libraries.",
            },
            {
                "Feature": "Architecture",
                "Description": "Explains components, dependencies and code flow.",
            },
            {
                "Feature": "Static Quality Checks",
                "Description": "Detects large files, TODOs and maintenance issues.",
            },
            {
                "Feature": "Repository Chat",
                "Description": "Answers questions using retrieved source-code chunks.",
            },
        ]

        st.dataframe(
            pd.DataFrame(feature_rows),
            use_container_width=True,
            hide_index=True,
        )

    with right_column:
        st.markdown("### Processing Flow")

        st.code(
            """
GitHub URL
    ↓
Repository Metadata
    ↓
Clone Repository
    ↓
Important File Scanner
    ↓
Parallel Static Analysis
    ↓
Documentation Agent
    ↓
Architecture Agent
    ↓
Final Report
    ↓
RAG-powered Repository Chat
""",
            language="text",
        )

    st.stop()


# ============================================================
# Repository header
# ============================================================

repository = result["repository_data"]
metadata = repository.metadata

st.markdown(
    '<div class="repo-card">',
    unsafe_allow_html=True,
)

header_left, header_right = st.columns(
    [4, 1],
    vertical_alignment="center",
)

with header_left:
    st.subheader(metadata.full_name)

    if metadata.description:
        st.write(metadata.description)
    else:
        st.caption("No GitHub repository description is available.")

    st.caption(
        f"Owner: {metadata.owner} · "
        f"Default branch: {metadata.default_branch} · "
        f"Visibility: {'Private' if metadata.is_private else 'Public'}"
    )

with header_right:
    st.link_button(
        "Open on GitHub",
        metadata.html_url,
        use_container_width=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# Metrics
# ============================================================

metric_columns = st.columns(6)

metric_columns[0].metric(
    "Primary Language",
    metadata.primary_language or "Unknown",
)

metric_columns[1].metric(
    "Stars",
    f"{metadata.stars:,}",
)

metric_columns[2].metric(
    "Forks",
    f"{metadata.forks:,}",
)

metric_columns[3].metric(
    "Open Issues",
    f"{metadata.open_issues:,}",
)

metric_columns[4].metric(
    "Files Analyzed",
    f"{len(result.get('files', [])):,}",
)

metric_columns[5].metric(
    "Dependencies",
    f"{len(result.get('dependencies', [])):,}",
)


# ============================================================
# Agent status
# ============================================================

completed_agents = result.get(
    "completed_agents",
    [],
)

if completed_agents:
    st.markdown("#### Completed Pipeline")

    status_html = "".join(
        f'<span class="status-chip">✓ {agent}</span>'
        for agent in completed_agents
    )

    st.markdown(
        status_html,
        unsafe_allow_html=True,
    )


# ============================================================
# Tabs
# ============================================================

(
    overview_tab,
    documentation_tab,
    architecture_tab,
    source_tab,
    dependencies_tab,
    api_tab,
    quality_tab,
    activity_tab,
    chat_tab,
) = st.tabs(
    [
        "Overview",
        "Documentation",
        "Architecture",
        "Source Files",
        "Dependencies",
        "API Discovery",
        "Code Quality",
        "Repository Activity",
        "Repository Chat",
    ]
)


# ============================================================
# Overview tab
# ============================================================

with overview_tab:
    summary_column, info_column = st.columns(
        [2, 1],
        gap="large",
    )

    with summary_column:
        st.markdown("### Final Analysis Report")

        final_report = result.get(
            "final_report",
            "",
        )

        if final_report:
            st.markdown(final_report)
        else:
            st.warning("The final report was not generated.")

        st.download_button(
            label="Download final report",
            data=final_report,
            file_name=f"{metadata.name}_analysis.md",
            mime="text/markdown",
            disabled=not bool(final_report),
        )

    with info_column:
        st.markdown("### Repository Details")

        st.write(
            f"**License:** "
            f"{metadata.license_name or 'Not specified'}"
        )
        st.write(
            f"**Repository size:** {metadata.size_kb:,} KB"
        )
        st.write(
            f"**Created:** {format_datetime(metadata.created_at)}"
        )
        st.write(
            f"**Updated:** {format_datetime(metadata.updated_at)}"
        )
        st.write(
            f"**Last pushed:** {format_datetime(metadata.pushed_at)}"
        )
        st.write(
            f"**Forked repository:** "
            f"{'Yes' if metadata.is_fork else 'No'}"
        )

        if metadata.topics:
            st.markdown("**Topics**")
            st.write(", ".join(metadata.topics))

        st.divider()

        st.markdown("### Detected Counts")

        st.write(
            f"API routes: **{len(result.get('api_routes', []))}**"
        )
        st.write(
            f"Entry points: **{len(result.get('entry_points', []))}**"
        )
        st.write(
            f"Quality findings: "
            f"**{len(result.get('quality_findings', []))}**"
        )


# ============================================================
# Documentation tab
# ============================================================

with documentation_tab:
    st.markdown("### Documentation and Technology Analysis")

    documentation_report = result.get(
        "documentation_report",
        "",
    )

    if documentation_report:
        st.markdown(documentation_report)
    else:
        st.warning("The documentation report was not generated.")

    if repository.readme:
        with st.expander(
            "Original README",
            expanded=False,
        ):
            st.markdown(repository.readme.content)


# ============================================================
# Architecture tab
# ============================================================

with architecture_tab:
    st.markdown("### Architecture, Dependencies, APIs and Code Flow")

    architecture_report = result.get(
        "architecture_report",
        "",
    )

    if architecture_report:
        st.markdown(architecture_report)
    else:
        st.warning("The architecture report was not generated.")


# ============================================================
# Source files tab
# ============================================================

with source_tab:
    st.markdown("### Repository Source Files")

    source_summary_columns = st.columns(3)

    source_summary_columns[0].metric(
        "Analyzed Files",
        len(result.get("files", [])),
    )

    source_summary_columns[1].metric(
        "Entry Points",
        len(result.get("entry_points", [])),
    )

    source_summary_columns[2].metric(
        "File Tree Characters",
        len(result.get("file_tree", "")),
    )

    with st.expander(
        "Repository file tree",
        expanded=True,
    ):
        st.code(
            result.get("file_tree", ""),
            language="text",
        )

    file_rows = [
        {
            "Path": file.path,
            "Extension": file.extension or "none",
            "Size (bytes)": file.size_bytes,
            "Lines": file.line_count,
        }
        for file in result.get("files", [])
    ]

    files_df = pd.DataFrame(file_rows)

    if files_df.empty:
        st.info("No supported source files were found.")
    else:
        file_search = st.text_input(
            "Filter files",
            placeholder="Search by path or extension",
            key="file_filter",
        )

        filtered_files_df = files_df

        if file_search.strip():
            search_value = file_search.strip().lower()

            filtered_files_df = files_df[
                files_df["Path"]
                .str.lower()
                .str.contains(
                    search_value,
                    na=False,
                )
                |
                files_df["Extension"]
                .str.lower()
                .str.contains(
                    search_value,
                    na=False,
                )
            ]

        st.dataframe(
            filtered_files_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Size (bytes)": st.column_config.NumberColumn(
                    format="%d",
                ),
                "Lines": st.column_config.NumberColumn(
                    format="%d",
                ),
            },
        )


# ============================================================
# Dependencies tab
# ============================================================

with dependencies_tab:
    st.markdown("### Detected Dependencies")

    dependency_rows = to_rows(
        result.get("dependencies", [])
    )

    dependency_df = pd.DataFrame(dependency_rows)

    if dependency_df.empty:
        st.info("No dependency files or packages were detected.")
    else:
        dependency_types = [
            value
            for value in dependency_df.get(
                "dependency_type",
                pd.Series(dtype=str),
            ).dropna().unique()
        ]

        selected_type = st.selectbox(
            "Dependency type",
            options=["All", *dependency_types],
        )

        filtered_dependency_df = dependency_df

        if selected_type != "All":
            filtered_dependency_df = dependency_df[
                dependency_df["dependency_type"]
                == selected_type
            ]

        st.dataframe(
            filtered_dependency_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# API tab
# ============================================================

with api_tab:
    st.markdown("### Discovered API Routes")

    route_rows = to_rows(
        result.get("api_routes", [])
    )

    route_df = pd.DataFrame(route_rows)

    if route_df.empty:
        st.info(
            "No REST or GraphQL routes were detected by the current parsers."
        )
    else:
        api_summary_columns = st.columns(3)

        api_summary_columns[0].metric(
            "Routes",
            len(route_df),
        )

        api_summary_columns[1].metric(
            "Methods",
            route_df["method"].nunique()
            if "method" in route_df.columns
            else 0,
        )

        api_summary_columns[2].metric(
            "Frameworks",
            route_df["framework"].nunique()
            if "framework" in route_df.columns
            else 0,
        )

        st.dataframe(
            route_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# Code quality tab
# ============================================================

with quality_tab:
    st.markdown("### Static Code Quality Findings")

    finding_rows = to_rows(
        result.get("quality_findings", [])
    )

    finding_df = pd.DataFrame(finding_rows)

    if finding_df.empty:
        st.success(
            "No configured static-analysis findings were detected."
        )
    else:
        severity_options = [
            value
            for value in finding_df.get(
                "severity",
                pd.Series(dtype=str),
            ).dropna().unique()
        ]

        selected_severity = st.selectbox(
            "Severity",
            options=["All", *severity_options],
        )

        filtered_finding_df = finding_df

        if selected_severity != "All":
            filtered_finding_df = finding_df[
                finding_df["severity"]
                == selected_severity
            ]

        st.dataframe(
            filtered_finding_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# Activity tab
# ============================================================

with activity_tab:
    left_activity, right_activity = st.columns(
        2,
        gap="large",
    )

    with left_activity:
        st.markdown("### Branches")

        branch_rows = [
            branch.model_dump()
            for branch in repository.branches
        ]

        branch_df = pd.DataFrame(branch_rows)

        if branch_df.empty:
            st.info("No branches were returned.")
        else:
            st.dataframe(
                branch_df,
                use_container_width=True,
                hide_index=True,
            )

    with right_activity:
        st.markdown("### Latest Commit")

        latest_commit = repository.latest_commit

        if latest_commit:
            st.write(
                f"**Message:** {latest_commit.message}"
            )
            st.write(
                f"**Author:** "
                f"{latest_commit.author_name or 'Unknown'}"
            )
            st.write(
                f"**Committed:** "
                f"{format_datetime(latest_commit.committed_at)}"
            )
            st.write(
                f"**SHA:** `{latest_commit.short_sha}`"
            )

            st.link_button(
                "Open commit",
                latest_commit.html_url,
            )
        else:
            st.info("No latest commit information is available.")

        st.divider()

        st.markdown("### Local Clone")

        st.code(
            repository.local_path,
            language="text",
        )


# ============================================================
# Chat tab
# ============================================================

with chat_tab:
    st.markdown("### Ask Questions About the Repository")

    st.caption(
        "The vector index is created only when the first question "
        "is submitted. Answers use retrieved repository source chunks."
    )

    if not st.session_state.messages:
        st.info(
            "Example questions: Where is authentication implemented? "
            "What is the application entry point? "
            "How does data flow through the project?"
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a repository question..."
    )

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner(
                    "Searching repository files..."
                ):
                    chat_service = initialize_chat_service(
                        result
                    )

                    answer = chat_service.ask(question)

                st.markdown(answer)

            except Exception as error:
                answer = (
                    "Repository question answering failed: "
                    f"{error}"
                )

                st.error(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )