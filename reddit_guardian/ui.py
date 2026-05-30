from __future__ import annotations

import streamlit as st


RISK_META = {
    "SAFE": {"label": "Safe Waters", "color": "#22c55e", "bg": "rgba(34,197,94,0.12)"},
    "SPAM": {"label": "Scam Spray", "color": "#f59e0b", "bg": "rgba(245,158,11,0.12)"},
    "PII_LEAK": {"label": "Leak", "color": "#ef4444", "bg": "rgba(239,68,68,0.14)"},
    "HARASSMENT": {"label": "Harbor Trouble", "color": "#f472b6", "bg": "rgba(244,114,182,0.14)"},
    "NSFW": {"label": "Mutiny", "color": "#a855f7", "bg": "rgba(168,85,247,0.14)"},
    "OTHER": {"label": "Review", "color": "#ffdb3c", "bg": "rgba(255,219,60,0.12)"},
}


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Mono:wght@400;700&display=swap");
        html, body, [class*="css"] { font-family: "Inter", sans-serif; }
        .stApp {
            background:
                radial-gradient(circle at 15% 12%, rgba(185, 199, 228, 0.10), transparent 18%),
                radial-gradient(circle at 85% 10%, rgba(255, 219, 60, 0.10), transparent 16%),
                linear-gradient(180deg, #131315, #0e0e10);
            color: #e4e2e4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
