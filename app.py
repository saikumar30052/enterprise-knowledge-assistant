import time
from typing import Any, Dict, List

try:
    import requests
except ImportError:  # pragma: no cover - handled at runtime
    requests = None  # type: ignore[assignment]

try:
    import streamlit as st
except ImportError:  # pragma: no cover - handled at runtime
    st = None  # type: ignore[assignment]


API_URL = "http://127.0.0.1:8000/query"
APP_VERSION = "1.0.0"


STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {
    --primary: #2563EB;
    --primary-dark: #1D4ED8;
    --page: #F8FAFC;
    --card: #FFFFFF;
    --text: #1E293B;
    --muted: #64748B;
    --border: #E2E8F0;
    --blue-soft: #EFF6FF;
    --shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
    --radius: 12px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--page);
}

[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.86);
}

.block-container {
    max-width: 1420px;
    padding: 2.5rem 3.5rem 4rem;
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text);
    letter-spacing: 0;
}

h1 { font-size: 34px !important; line-height: 1.2 !important; }
h2, h3 { font-size: 22px !important; }
p, label, [data-testid="stMarkdownContainer"] { font-size: 16px; }

.hero {
    background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
}

.hero-kicker {
    color: var(--primary);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: .65rem;
}

.hero-copy {
    color: var(--muted);
    font-size: 16px;
    margin: .6rem 0 0;
}

.metric-card, .response-card, .question-card, .citation-card, .sidebar-card, .history-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.metric-card {
    min-height: 104px;
    padding: 1rem 1.15rem;
}

.metric-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: .45rem;
}

.metric-value {
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 24px;
    font-weight: 700;
}

.sidebar-card {
    padding: .95rem 1rem;
    margin: .55rem 0;
}

.sidebar-card-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.sidebar-card-value {
    color: var(--text);
    font-size: 15px;
    font-weight: 600;
    margin-top: .3rem;
    overflow-wrap: anywhere;
}

.response-card, .question-card, .history-card {
    padding: 1.35rem 1.5rem;
    margin: .85rem 0;
}

.question-card {
    background: var(--blue-soft);
    border-color: #BFDBFE;
}

.response-card {
    border-left: 4px solid var(--primary);
}

.card-eyebrow {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
    margin-bottom: .55rem;
}

.card-text {
    color: var(--text);
    font-size: 16px;
    line-height: 1.7;
}

.citation-card {
    padding: .95rem 1.1rem;
    margin: .6rem 0;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.citation-card:hover, .history-card:hover, .metric-card:hover, .sidebar-card:hover {
    border-color: #93C5FD;
    box-shadow: 0 12px 28px rgba(37, 99, 235, .12);
    transform: translateY(-1px);
}

.citation-title {
    color: var(--text);
    font-size: 15px;
    font-weight: 700;
}

.citation-meta {
    color: var(--muted);
    font-size: 13px;
    margin-top: .35rem;
}

.badge {
    border-radius: 999px;
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    padding: .32rem .65rem;
}

.badge-green { background: #DCFCE7; color: #166534; }
.badge-blue { background: #DBEAFE; color: #1D4ED8; }
.badge-gray { background: #F1F5F9; color: #475569; }

div[data-testid="stTextInput"] input {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 12px;
    color: var(--text);
    font-size: 16px;
    min-height: 3.25rem;
    padding: .75rem 1rem;
}

div[data-testid="stTextInput"] input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, .14);
}

div.stButton > button {
    background: var(--primary);
    border: 1px solid var(--primary);
    border-radius: 10px;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    min-height: 3.25rem;
    transition: background .18s ease, box-shadow .18s ease, transform .18s ease;
    width: 100%;
}

div.stButton > button:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
    box-shadow: 0 8px 18px rgba(37, 99, 235, .24);
    color: #FFFFFF;
    transform: translateY(-1px);
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.15rem 2rem;
}

[data-testid="stExpander"] {
    background: transparent;
    border: 0;
}

.dark-mode .stApp { background: #0F172A; }
.dark-mode .hero, .dark-mode .metric-card, .dark-mode .response-card,
.dark-mode .citation-card, .dark-mode .sidebar-card, .dark-mode .history-card { background: #172033; border-color: #334155; }
.dark-mode .question-card { background: #172554; border-color: #1D4ED8; }
.dark-mode h1, .dark-mode h2, .dark-mode h3, .dark-mode h4,
.dark-mode .metric-value, .dark-mode .sidebar-card-value, .dark-mode .card-text, .dark-mode .citation-title { color: #F8FAFC; }
.dark-mode .hero-copy, .dark-mode .metric-label, .dark-mode .sidebar-card-label, .dark-mode .citation-meta { color: #CBD5E1; }
.dark-mode [data-testid="stHeader"], .dark-mode [data-testid="stSidebar"] { background: #111827; }
.dark-mode div[data-testid="stTextInput"] input { background: #172033; color: #F8FAFC; border-color: #475569; }

@media (max-width: 768px) {
    .block-container { padding: 1.35rem 1rem 2.5rem; }
    h1 { font-size: 28px !important; }
    h2, h3 { font-size: 20px !important; }
    .hero { padding: 1.35rem; }
    .response-card, .question-card, .history-card { padding: 1rem; }
}
</style>
"""


def _initialize_session_state() -> None:
    """Initialize the session state used for chat history."""
    if st is None:
        raise ImportError("The 'streamlit' package is required to run the frontend app.")
    if "history" not in st.session_state:
        st.session_state.history = []


def call_api(question: str) -> Dict[str, Any]:
    """Send a question to the FastAPI backend and return the parsed result."""
    if requests is None:
        raise ImportError("The 'requests' package is required to call the backend API.")

    started_at = time.perf_counter()

    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=900,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError("Unable to connect to the backend. Make sure the FastAPI server is running.") from exc
    except requests.exceptions.Timeout as exc:
        raise TimeoutError("The backend request timed out. Please try again.") from exc
    except requests.exceptions.HTTPError as exc:
        try:
            detail = response.json().get("detail", "The backend returned an error.")
        except ValueError:
            detail = "The backend returned an error."
        raise requests.exceptions.HTTPError(detail) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("An unexpected request error occurred.") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ValueError("The backend returned an invalid JSON response.") from exc

    elapsed = round(time.perf_counter() - started_at, 2)
    payload["response_time"] = elapsed
    return payload


def _badge(label: str, value: str, color: str) -> str:
    return f'<span class="badge badge-{color}">{label}: {value}</span>'


def _file_icon(source: str) -> str:
    source_lower = source.lower()
    if source_lower.endswith(".pdf"):
        return "📄"
    if source_lower.endswith(".pptx"):
        return "📊"
    if source_lower.endswith(".docx"):
        return "📝"
    if source_lower.endswith((".xlsx", ".xls")):
        return "📗"
    return "📁"


def _confidence_label(result: Dict[str, Any]) -> tuple[str, str]:
    citations = result.get("citations", [])
    answer = str(result.get("answer", "")).lower()
    if citations and "i could not find" not in answer:
        return "Grounded", "green"
    return "Not found", "gray"


def _indexed_sources() -> List[str]:
    sources = set()
    for entry in st.session_state.history:
        for citation in entry.get("citations", []):
            source = citation.get("source")
            if source:
                sources.add(str(source))
    return sorted(sources)


def _render_sidebar_card(label: str, value: str, badge: str | None = None, color: str = "gray") -> None:
    badge_html = f'<div style="margin-top:.55rem">{_badge(label, badge, color)}</div>' if badge else ""
    st.markdown(
        f'<div class="sidebar-card"><div class="sidebar-card-label">{label}</div>'
        f'<div class="sidebar-card-value">{value}</div>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def display_answer(result: Dict[str, Any]) -> None:
    """Render the answer section inside a styled container."""
    confidence, confidence_color = _confidence_label(result)
    response_time = result.get("response_time", 0)
    st.markdown(
        '<div class="response-card">'
        '<div class="card-eyebrow">Assistant response</div>'
        f'<div style="margin-bottom:.8rem">{_badge("Confidence", confidence, confidence_color)} '
        f'{_badge("Response time", f"{response_time} sec", "blue")}</div>'
        f'<div class="card-text">{result.get("answer", "No answer was returned.")}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def display_sources(citations: List[Dict[str, Any]]) -> None:
    """Render the citation list in an expandable section."""
    if not citations:
        return

    with st.expander("Sources", expanded=True, icon=":material/menu_book:"):
        for citation in citations:
            source = str(citation.get("source", "Unknown"))
            page = citation.get("page", "N/A")
            chunk_id = citation.get("chunk_id", "Unknown")
            st.markdown(
                '<div class="citation-card">'
                f'<div class="citation-title">{_file_icon(source)} {source}</div>'
                f'<div class="citation-meta">Page {page} &nbsp; · &nbsp; Chunk ID {chunk_id}</div>'
                '</div>',
                unsafe_allow_html=True,
            )


def display_chat_history() -> None:
    """Render previous conversations in reverse chronological order."""
    if not st.session_state.history:
        st.caption("No conversations yet. Ask a question to begin.")
        return

    for index, entry in enumerate(reversed(st.session_state.history), start=1):
        with st.container():
            st.markdown(
                f'<div class="question-card"><div class="card-eyebrow">Question {index}</div>'
                f'<div class="card-text">{entry["question"]}</div></div>',
                unsafe_allow_html=True,
            )
            display_answer(entry)
            display_sources(entry.get("citations", []))


def main() -> None:
    """Render the Streamlit frontend for the Enterprise Knowledge Assistant."""
    if st is None:
        raise ImportError("The 'streamlit' package is required to run the frontend app.")

    st.set_page_config(
        page_title="Enterprise Knowledge Assistant",
        page_icon=":material/menu_book:",
        layout="wide",
    )
    _initialize_session_state()
    st.markdown(STYLE, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## Enterprise assistant")
        st.caption("Secure knowledge discovery for enterprise teams")
        dark_mode = st.toggle("Dark mode", value=False)
        if dark_mode:
            st.markdown(
                """
                <style>
                .stApp { background: #0F172A; }
                [data-testid="stHeader"] { background: #111827; }
                [data-testid="stSidebar"] { background: #111827; border-color: #334155; }
                h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"],
                [data-testid="stSidebar"] * { color: #F8FAFC !important; }
                .hero, .metric-card, .response-card, .citation-card, .sidebar-card, .history-card {
                    background: #172033; border-color: #334155;
                }
                .question-card { background: #172554; border-color: #1D4ED8; }
                .hero-copy, .metric-label, .sidebar-card-label, .citation-meta { color: #CBD5E1 !important; }
                div[data-testid="stTextInput"] input { background: #172033; color: #F8FAFC; border-color: #475569; }
                </style>
                """,
                unsafe_allow_html=True,
            )

        _render_sidebar_card("Backend status", "Ready", "Backend ready", "green")
        _render_sidebar_card("Backend URL", API_URL)
        _render_sidebar_card("Application version", APP_VERSION, f"Version {APP_VERSION}", "gray")
        _render_sidebar_card("Questions asked", str(len(st.session_state.history)))

        indexed_sources = _indexed_sources()
        with st.expander("Indexed documents", expanded=False, icon=":material/folder_open:"):
            if indexed_sources:
                for source in indexed_sources:
                    st.caption(f"{_file_icon(source)}  {source}")
            else:
                st.caption("Documents appear here after citations are returned.")

        if st.button("Clear chat history", icon=":material/delete_sweep:"):
            st.session_state.history = []
            st.success("Chat history cleared.")

    st.markdown(
        '<div class="hero">'
        '<div class="hero-kicker">Enterprise knowledge workspace</div>'
        '<h1>Enterprise Knowledge Assistant</h1>'
        '<p class="hero-copy">Ask precise questions and explore answers grounded in your indexed documents.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    metric_one, metric_two, metric_three = st.columns(3)
    with metric_one:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Session questions</div>'
            f'<div class="metric-value">{len(st.session_state.history)}</div></div>',
            unsafe_allow_html=True,
        )
    with metric_two:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Indexed sources</div>'
            f'<div class="metric-value">{len(_indexed_sources())}</div></div>',
            unsafe_allow_html=True,
        )
    with metric_three:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">System status</div>'
            f'<div class="metric-value" style="color:#16A34A">Ready</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("## Ask a question")
    question_col, ask_col = st.columns([5, 1], vertical_alignment="bottom")
    with question_col:
        question = st.text_input("Question", placeholder="Ask about your enterprise knowledge base...", label_visibility="collapsed")
    with ask_col:
        ask_clicked = st.button("Ask", icon=":material/arrow_upward:")

    if ask_clicked:
        if not question or not question.strip():
            st.warning("Please enter a question before submitting.", icon=":material/warning:")
            st.stop()

        with st.status("Working through your enterprise knowledge...", expanded=True) as status:
            st.write("Understanding your question")
            st.write("Searching indexed documents")
            try:
                result = call_api(question.strip())
                st.write("Preparing grounded response")
                status.update(label="Response ready", state="complete", expanded=False)
            except ConnectionError as exc:
                status.update(label="Backend unavailable", state="error", expanded=True)
                st.error(str(exc))
                st.stop()
            except TimeoutError as exc:
                status.update(label="Request timed out", state="error", expanded=True)
                st.error(str(exc))
                st.stop()
            except requests.exceptions.HTTPError as exc:
                status.update(label="Backend returned an error", state="error", expanded=True)
                st.error(str(exc))
                st.stop()
            except ValueError as exc:
                status.update(label="Invalid response", state="error", expanded=True)
                st.error(str(exc))
                st.stop()
            except Exception as exc:  # pragma: no cover - defensive fallback
                status.update(label="Unexpected error", state="error", expanded=True)
                st.error(f"Unexpected exception: {exc}")
                st.stop()

        st.markdown(
            f'<div class="question-card"><div class="card-eyebrow">Your question</div>'
            f'<div class="card-text">{question.strip()}</div></div>',
            unsafe_allow_html=True,
        )
        display_answer(result)
        display_sources(result.get("citations", []))

        st.session_state.history.append(
            {
                "question": result.get("question", question.strip()),
                "answer": result.get("answer", ""),
                "citations": result.get("citations", []),
                "response_time": result.get("response_time", 0),
            }
        )

    st.markdown("## Conversation history")
    display_chat_history()


if __name__ == "__main__":
    main()
