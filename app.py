from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from agent import fetch_devto_data, scan_post_content

APP_TITLE = "The Coral Lookout"
PROJECT_ROOT = Path(__file__).resolve().parent
CORAL_YAML_PATH = PROJECT_ROOT / "coral" / "devto_guardian_connector.yaml"
CORAL_MAPPING = "Dev.to article array → id, title, description, url"


# -----------------------------
# Styling
# -----------------------------
def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Mono:wght@400;700&display=swap");

        :root {
            --bg: #08090c;
            --bg-soft: #10131a;
            --panel: #1b1f27;
            --panel-2: #232936;
            --ink: #f7f4eb;
            --muted: #b8bcc7;
            --muted-2: #8f97a5;
            --gold: #f3c546;
            --gold-2: #ffda7a;
            --parchment: #f4eddc;
            --parchment-2: #e7deca;
            --card: #e8e3d6;
            --card-2: #ddd5c6;
            --card-3: #d2c8b2;
            --card-text: #171717;
            --card-muted: #4b5563;
            --sea: #5cb8ff;
            --emerald: #33c36a;
            --danger: #ef4444;
            --amber: #f59e0b;
            --rose: #f472b6;
            --line: rgba(255,255,255,0.08);
        }

        html, body, [class*="css"] {
            font-family: "Inter", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 16% 16%, rgba(92,184,255,0.10), transparent 18%),
                radial-gradient(circle at 82% 10%, rgba(243,197,70,0.12), transparent 16%),
                radial-gradient(circle at 80% 78%, rgba(239,68,68,0.08), transparent 20%),
                linear-gradient(180deg, #0c1118 0%, #090b10 100%);
            color: var(--ink);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0e13 0%, #10141c 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        [data-testid="stSidebar"] * {
            color: var(--ink);
        }

        /* Default chrome */
        header[data-testid="stHeader"] {
            background: linear-gradient(180deg, rgba(248,241,228,0.96), rgba(223,213,194,0.95));
            border-bottom: 1px solid rgba(96,74,36,0.20);
        }

        header[data-testid="stHeader"]::after {
            content: "⚓  💎  🪙  ⛵  🧭  🔱";
            position: absolute;
            inset: 0 0 auto 0;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            letter-spacing: 0.55rem;
            color: rgba(48, 40, 24, 0.55);
            pointer-events: none;
        }

        .stApp [data-testid="stToolbar"] {
            background: transparent;
        }

        /* Main containers */
        .hero-card,
        .status-hub,
        .info-card,
        .console-card,
        .timeline-item,
        .metric-card,
        .sidebar-pill,
        .sidebar-box,
        .banner-card {
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 16px 40px rgba(0,0,0,0.28);
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 1.15rem 1.25rem 1.05rem 1.25rem;
            background:
                linear-gradient(180deg, rgba(244, 237, 220, 0.14), rgba(244, 237, 220, 0.06)),
                linear-gradient(180deg, rgba(20,24,33,0.96), rgba(13,15,21,0.96));
        }

        .hero-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 12% 20%, rgba(92,184,255,0.13), transparent 20%),
                radial-gradient(circle at 82% 18%, rgba(243,197,70,0.15), transparent 16%),
                radial-gradient(circle at 74% 84%, rgba(239,68,68,0.10), transparent 18%);
            pointer-events: none;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.3fr 0.9fr;
            gap: 1rem;
            align-items: stretch;
            position: relative;
            z-index: 1;
        }

        .title {
            margin: 0;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 0.96;
            font-weight: 900;
            letter-spacing: -0.04em;
            color: var(--gold-2);
        }

        .subtitle {
            margin-top: 0.35rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-weight: 900;
            font-size: 0.78rem;
            color: var(--muted);
        }

        .hero-copy,
        .mini-terminal,
        .muted,
        .section-subtle,
        .status-note {
            color: var(--muted);
        }

        .hero-copy {
            margin-top: 0.65rem;
            line-height: 1.6rem;
            max-width: 62ch;
        }

        .terminal-line {
            margin-top: 0.85rem;
            font-family: "Space Mono", monospace;
            color: #d8dbe3;
            font-size: 0.86rem;
            line-height: 1.6rem;
        }

        .status-hub {
            margin-top: 1rem;
            border-radius: 24px;
            padding: 1rem 1.05rem;
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(244,237,220,0.08), rgba(244,237,220,0.04)),
                linear-gradient(180deg, rgba(22,26,36,0.96), rgba(17,19,27,0.95));
        }

        .status-hub::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 18% 22%, rgba(92,184,255,0.14), transparent 22%),
                radial-gradient(circle at 82% 18%, rgba(243,197,70,0.16), transparent 20%),
                radial-gradient(circle at 44% 82%, rgba(239,68,68,0.10), transparent 18%);
            pointer-events: none;
        }

        .status-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.75rem;
            font-weight: 900;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: var(--gold-2);
            position: relative;
            z-index: 1;
        }

        .status-dot {
            width: 0.92rem;
            height: 0.92rem;
            border-radius: 999px;
            background: var(--emerald);
            box-shadow: 0 0 0 rgba(51,195,106,0.35);
            animation: pulse 1.8s infinite;
            flex: 0 0 auto;
        }

        .status-dot.red {
            background: var(--danger);
            animation: pulse-red 1.6s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(51,195,106,0.55); }
            70% { box-shadow: 0 0 0 18px rgba(51,195,106,0); }
            100% { box-shadow: 0 0 0 0 rgba(51,195,106,0); }
        }

        @keyframes pulse-red {
            0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.55); }
            70% { box-shadow: 0 0 0 18px rgba(239,68,68,0); }
            100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.8rem;
            position: relative;
            z-index: 1;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            gap: 0.42rem;
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            font-size: 0.78rem;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.05);
            color: var(--ink);
        }

        .banner-card,
        .info-card,
        .console-card {
            border-radius: 24px;
            padding: 0.95rem 1rem;
            background: rgba(19, 22, 30, 0.94);
        }

        .banner-card {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            background: linear-gradient(180deg, var(--parchment), var(--parchment-2));
            color: #1a1a1a;
        }

        .pirate-chrome {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
            background: linear-gradient(180deg, rgba(236,229,214,0.98), rgba(216,206,188,0.96));
            color: #1d1a12;
            border: 1px solid rgba(96,74,36,0.18);
            box-shadow: 0 14px 34px rgba(0,0,0,0.16);
        }

        .pirate-chrome::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 15% 25%, rgba(255,255,255,0.7), transparent 12%),
                radial-gradient(circle at 80% 16%, rgba(255,219,93,0.55), transparent 10%),
                linear-gradient(90deg, rgba(52,106,166,0.05), rgba(52,106,166,0.00));
            pointer-events: none;
        }

        .chrome-row {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            flex-wrap: wrap;
        }

        .chrome-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .chrome-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.33);
            border: 1px solid rgba(96,74,36,0.12);
            color: #2a2315;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.03em;
        }

        .chrome-track {
            position: relative;
            flex: 1 1 280px;
            min-height: 34px;
            border-radius: 999px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(247,244,235,0.96), rgba(221,212,197,0.98));
            border: 1px solid rgba(96,74,36,0.16);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.38);
        }

        .chrome-track::after {
            content: "🌊🌊🌊🌊🌊";
            position: absolute;
            left: 0.75rem;
            bottom: 0.18rem;
            font-size: 0.95rem;
            opacity: 0.55;
            letter-spacing: 0.2rem;
        }

        .chrome-ship {
            position: absolute;
            top: 2px;
            left: 112%;
            font-size: 1.65rem;
            animation: pirate-sail-left 16s linear infinite;
            z-index: 2;
            filter: drop-shadow(0 4px 3px rgba(0,0,0,0.18));
        }

        .chrome-wake {
            position: absolute;
            top: 15px;
            left: 100%;
            width: 140px;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.92), rgba(92,184,255,0.58));
            animation: pirate-wake-left 16s linear infinite;
            filter: blur(0.6px);
            z-index: 1;
        }

        .chrome-cut {
            position: absolute;
            top: 11px;
            left: 108%;
            width: 78px;
            height: 22px;
            border-left: 3px solid rgba(52,106,166,0.68);
            border-bottom: 3px solid rgba(52,106,166,0.68);
            transform: skewX(-18deg) rotate(-8deg);
            border-radius: 0 0 24px 0;
            animation: pirate-cut-left 16s linear infinite;
            z-index: 1;
        }

        .chrome-jewel {
            position: absolute;
            font-size: 1rem;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.12));
            animation: jewel-float 4s ease-in-out infinite;
            z-index: 2;
        }

        .chrome-jewel.one { top: 6px; left: 0.75rem; animation-delay: 0s; }
        .chrome-jewel.two { top: 5px; right: 0.8rem; animation-delay: 0.7s; }
        .chrome-jewel.three { top: 9px; left: 26%; animation-delay: 1.4s; }
        .chrome-jewel.four { top: 7px; right: 24%; animation-delay: 2.1s; }

        .pirate-ribbon {
            position: relative;
            z-index: 1;
            margin-top: 0.45rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }

        .pirate-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.36);
            border: 1px solid rgba(96,74,36,0.14);
            color: #262018;
            font-size: 0.76rem;
            font-weight: 800;
        }

        .floating-coin {
            position: absolute;
            font-size: 1.15rem;
            animation: jewel-float 3.8s ease-in-out infinite;
            opacity: 0.8;
            pointer-events: none;
        }

        .floating-coin.left { top: 1.2rem; left: 1.2rem; }
        .floating-coin.right { top: 1.4rem; right: 1rem; }
        .floating-coin.lower-left { bottom: 1rem; left: 1.4rem; }
        .floating-coin.lower-right { bottom: 1rem; right: 1.2rem; }

        @keyframes pirate-sail-left {
            0% { transform: translateX(0); }
            100% { transform: translateX(-240%); }
        }
        @keyframes pirate-wake-left {
            0% { transform: translateX(0); opacity: 0; }
            8% { opacity: 1; }
            100% { transform: translateX(-240%); opacity: 0; }
        }
        @keyframes pirate-cut-left {
            0% { transform: translateX(0) skewX(-18deg) rotate(-8deg); opacity: 0; }
            6% { opacity: 1; }
            100% { transform: translateX(-240%) skewX(-18deg) rotate(-8deg); opacity: 0; }
        }

        .banner-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 16% 30%, rgba(255,255,255,0.55), transparent 10%),
                radial-gradient(circle at 86% 18%, rgba(255,219,93,0.65), transparent 8%),
                linear-gradient(90deg, rgba(16,44,72,0.03), rgba(16,44,72,0.00));
            pointer-events: none;
        }

        .banner-inner {
            position: relative;
            z-index: 1;
        }

        .banner-title {
            font-size: 1.65rem;
            line-height: 1.02;
            margin: 0;
            color: #181818;
            font-weight: 900;
        }

        .banner-sub {
            margin-top: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.73rem;
            font-weight: 900;
            color: #6a5930;
        }

        .banner-copy {
            margin-top: 0.55rem;
            color: #3f3f46;
            line-height: 1.5rem;
        }

        .deck-strip {
            margin-top: 0.8rem;
            position: relative;
            min-height: 90px;
            border-radius: 22px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(248,246,238,1) 0%, rgba(226,217,201,1) 55%, rgba(192,172,139,1) 100%);
            border: 1px solid rgba(96, 74, 36, 0.14);
        }

        .deck-strip::before {
            content: "";
            position: absolute;
            inset: auto 0 0 0;
            height: 24px;
            background: linear-gradient(180deg, rgba(43,104,159,0.05), rgba(19,91,153,0.16));
            border-top: 1px solid rgba(16,73,116,0.18);
        }

        .deck-strip::after {
            content: "🌊🌊🌊";
            position: absolute;
            bottom: -1px;
            right: 0.8rem;
            font-size: 1.1rem;
            opacity: 0.5;
            letter-spacing: 0.18rem;
        }

        .ship {
            position: absolute;
            top: 18px;
            left: 112%;
            font-size: 2.15rem;
            animation: sail-left 18s linear infinite;
            filter: drop-shadow(0 10px 8px rgba(0,0,0,0.18));
            z-index: 2;
        }

        .wake {
            position: absolute;
            top: 54px;
            left: 100%;
            width: 140px;
            height: 11px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(255,255,255,0.0), rgba(248, 250, 252, 0.88), rgba(92,184,255,0.55));
            filter: blur(1px);
            animation: wake-left 18s linear infinite;
            z-index: 1;
        }

        .wave-cut {
            position: absolute;
            top: 43px;
            left: 108%;
            width: 70px;
            height: 25px;
            border-left: 3px solid rgba(52, 106, 166, 0.62);
            border-bottom: 3px solid rgba(52, 106, 166, 0.62);
            transform: skewX(-18deg) rotate(-8deg);
            border-radius: 0 0 24px 0;
            animation: cut-left 18s linear infinite;
            z-index: 1;
            opacity: 0.9;
        }

        .jewel {
            position: absolute;
            font-size: 1.15rem;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.18));
            animation: jewel-float 4s ease-in-out infinite;
        }

        .jewel.one { top: 12px; left: 1rem; animation-delay: 0s; }
        .jewel.two { top: 18px; right: 4rem; animation-delay: 0.6s; }
        .jewel.three { top: 46px; left: 22%; animation-delay: 1.2s; }
        .jewel.four { top: 44px; right: 18%; animation-delay: 1.8s; }
        .jewel.five { top: 10px; right: 1rem; animation-delay: 0.9s; }

        @keyframes sail-left {
            0% { transform: translateX(0); }
            100% { transform: translateX(-240%); }
        }
        @keyframes wake-left {
            0% { transform: translateX(0); opacity: 0; }
            8% { opacity: 1; }
            100% { transform: translateX(-240%); opacity: 0; }
        }
        @keyframes cut-left {
            0% { transform: translateX(0) skewX(-18deg) rotate(-8deg); opacity: 0; }
            10% { opacity: 1; }
            100% { transform: translateX(-240%) skewX(-18deg) rotate(-8deg); opacity: 0; }
        }
        @keyframes jewel-float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        .panel-title {
            margin: 0 0 0.7rem 0;
            font-size: 0.98rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--gold-2);
        }

        .panel-subtle {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5rem;
        }

        .metric-card {
            border-radius: 24px;
            padding: 1rem 1rem 0.95rem 1rem;
            background: linear-gradient(180deg, #e0d9cb, #d2cbbd);
            color: var(--card-text);
            min-height: 98px;
        }

        .metric-label {
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.68rem;
            font-weight: 900;
            color: #6b6b6b;
        }

        .metric-value {
            margin-top: 0.3rem;
            font-size: 2rem;
            line-height: 1;
            font-weight: 900;
            color: #151515;
        }

        .metric-foot {
            margin-top: 0.35rem;
            font-size: 0.82rem;
            color: #4f4f56;
        }

        .console-card {
            background: linear-gradient(180deg, rgba(28,31,39,0.98), rgba(19,22,28,0.98));
        }

        .console-input textarea {
            background: #ece7dd !important;
            color: #171717 !important;
            border: 1px solid rgba(96,74,36,0.28) !important;
            border-radius: 18px !important;
            min-height: 124px !important;
            font-family: "Space Mono", monospace !important;
        }

        /* Sidebar widgets -> light gray boxes */
        div[data-baseweb="select"] > div {
            background: #dcd6ca !important;
            color: #171717 !important;
            border-radius: 16px !important;
            border: 1px solid rgba(96,74,36,0.32) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.35);
        }

        div[data-baseweb="select"] * {
            color: #171717 !important;
        }

        input, textarea {
            background: #dcd6ca !important;
            color: #171717 !important;
            border: 1px solid rgba(96,74,36,0.28) !important;
        }

        .stTextInput input, .stTextArea textarea {
            background: #dcd6ca !important;
            color: #171717 !important;
            border: 1px solid rgba(96,74,36,0.28) !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #6c6558 !important;
            opacity: 1 !important;
        }

        .stRadio label, .stCheckbox label {
            color: var(--ink) !important;
        }

        div[data-testid="stCodeBlock"],
        div[data-testid="stCodeBlock"] pre,
        div[data-testid="stCodeBlock"] code,
        pre, code {
            background: #d5cfbf !important;
            color: #1b1a18 !important;
            border-color: rgba(96,74,36,0.18) !important;
        }

        .stAlert,
        div[data-testid="stAlert"] {
            background: #d7d1c4 !important;
            color: #1d1a16 !important;
            border-radius: 18px !important;
            border: 1px solid rgba(96,74,36,0.18) !important;
        }

        .sidebar-box {
            background: rgba(223,216,204,0.97);
            border-radius: 18px;
            padding: 0.8rem;
            color: #1a1a1a;
            border: 1px solid rgba(96,74,36,0.22);
        }

        .sidebar-pill {
            background: rgba(18, 22, 29, 0.78);
            border-radius: 999px;
            padding: 0.55rem 0.8rem;
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--ink);
        }

        .timeline {
            border-left: 2px solid rgba(243,197,70,0.22);
            margin-left: 0.35rem;
            padding-left: 1rem;
        }

        .timeline-item {
            position: relative;
            border-radius: 22px;
            padding: 0.95rem 1rem 0.85rem 1rem;
            margin: 0 0 1rem 0;
            background: linear-gradient(180deg, #e0d9cb, #d2cbbd);
            color: var(--card-text);
            border: 1px solid rgba(96,74,36,0.16);
            box-shadow: 0 14px 30px rgba(0,0,0,0.20);
        }

        .timeline-item::before {
            content: "";
            position: absolute;
            left: -1.17rem;
            top: 1.08rem;
            width: 0.72rem;
            height: 0.72rem;
            border-radius: 999px;
            background: #9aa3b2;
            border: 3px solid #0d1016;
        }

        .timeline-safe::before { background: var(--emerald); }
        .timeline-medium::before { background: var(--amber); }
        .timeline-high::before { background: var(--danger); }

        .timeline-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            flex-wrap: wrap;
        }

        .risk-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.67rem;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            border-radius: 999px;
            padding: 0.35rem 0.68rem;
            background: rgba(0,0,0,0.06);
            border: 1px solid rgba(0,0,0,0.08);
        }

        .risk-safe { color: #0f8a44; }
        .risk-medium { color: #a16207; }
        .risk-high { color: #b91c1c; }

        .timeline-title {
            margin: 0.45rem 0 0.35rem 0;
            font-size: 1.02rem;
            font-weight: 900;
            color: #151515;
        }

        .timeline-text {
            color: #424242;
            line-height: 1.55rem;
            font-size: 0.94rem;
        }

        .timeline-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
            color: #575757;
            font-size: 0.83rem;
        }

        .meta-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.32rem;
            padding: 0.35rem 0.62rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.28);
            border: 1px solid rgba(0,0,0,0.08);
        }

        .timeline-foot {
            margin-top: 0.68rem;
            color: #3b3b3b;
            font-size: 0.86rem;
        }

        .command-kicker {
            margin: 0 0 0.35rem 0;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            color: var(--muted);
            font-weight: 900;
        }

        .command-title {
            margin: 0;
            font-size: 1.02rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 900;
            color: var(--gold-2);
        }

        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.8rem;
        }

        .quick-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.46rem 0.78rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.09);
            background: rgba(255,255,255,0.06);
            color: var(--ink);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .footer-note {
            color: var(--muted-2);
            font-size: 0.82rem;
            margin-top: 0.5rem;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(96,74,36,0.26);
            background: linear-gradient(180deg, #f4cd53, #e0ae37) !important;
            color: #241b05 !important;
            font-weight: 900 !important;
            box-shadow: 0 10px 24px rgba(225,174,55,0.22);
        }

        .stDownloadButton > button {
            border-radius: 14px;
            border: 1px solid rgba(96,74,36,0.26);
            background: linear-gradient(180deg, #f3f0e7, #ded7c5) !important;
            color: #1b1b1b !important;
            font-weight: 800 !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.02);
            transform: translateY(-1px);
        }

        /* Hide some chrome clutter */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# UI helpers
# -----------------------------
def metric_card(label: str, value: str, foot: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-foot">{foot}</div>
    </div>
    """


def risk_classes(risk_level: str) -> tuple[str, str]:
    risk = (risk_level or "LOW").upper()
    if risk == "HIGH":
        return "timeline-high", "risk-high"
    if risk == "MEDIUM":
        return "timeline-medium", "risk-medium"
    return "timeline-safe", "risk-safe"


def render_banner() -> None:
    st.markdown(
        """
        <div class="banner-card">
          <div class="banner-inner">
            <div class="banner-title">🏴‍☠️ Coral Lookout</div>
            <div class="banner-sub">pirate-style personal AI agent</div>
            <div class="banner-copy">
              Watching developer feeds for scams, malicious packages, and leaked secrets — with Coral as the chart and Gemini or heuristics as the oracle.
            </div>
            <div class="deck-strip" aria-hidden="true">
              <div class="jewel one">💎</div>
              <div class="jewel two">🪙</div>
              <div class="jewel three">💠</div>
              <div class="jewel four">⚓</div>
              <div class="jewel five">💎</div>
              <div class="ship">⛵</div>
              <div class="wake"></div>
              <div class="wave-cut"></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pirate_chrome() -> None:
    st.markdown(
        """
        <div class="pirate-chrome">
          <div class="chrome-row">
            <div class="chrome-group">
              <span class="chrome-chip">⚓ Mission: Protect the feed</span>
              <span class="chrome-chip">💎 Pirate jewels</span>
              <span class="chrome-chip">🪙 Coral bounty</span>
            </div>
            <div class="chrome-track" aria-hidden="true">
              <div class="chrome-jewel one">💎</div>
              <div class="chrome-jewel two">🪙</div>
              <div class="chrome-jewel three">🦜</div>
              <div class="chrome-jewel four">🔱</div>
              <div class="chrome-ship">⛵</div>
              <div class="chrome-wake"></div>
              <div class="chrome-cut"></div>
            </div>
            <div class="chrome-group">
              <span class="chrome-chip">🗺️ Chart room</span>
              <span class="chrome-chip">🌊 Live waters</span>
              <span class="chrome-chip">🧭 Open sea</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_hub(articles: list[dict[str, Any]], flagged: list[dict[str, Any]], source_mode: str) -> None:
    total = len(articles)
    high = sum(1 for x in flagged if x.get("risk_level") == "HIGH")
    medium = sum(1 for x in flagged if x.get("risk_level") == "MEDIUM")
    mode_label = "LIVE CORAL" if source_mode == "Coral SQL" else "DEMO FLEET"
    status = "🟢 GUARDIAN: ONLINE & VIGILANT" if not flagged else f"🚨 GUARDIAN: {len(flagged)} THREATS INTERCEPTED"
    task = (
        "Subscribing to live Dev.to feed..."
        if source_mode == "Coral SQL"
        else "Consulting the chart room archives..."
    )

    st.markdown(
        f"""
        <div class="status-hub">
          <div class="floating-coin lower-left">🦜</div>
          <div class="floating-coin lower-right">🔱</div>
          <div class="status-row"><span class="status-dot {'red' if flagged else ''}"></span>{status}</div>
          <div class="terminal-line">Current Task: {task}</div>
          <div class="chip-row">
            <span class="chip">Source: {mode_label}</span>
            <span class="chip">Articles: {total}</span>
            <span class="chip">High Risk: {high}</span>
            <span class="chip">Medium Risk: {medium}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(articles: list[dict[str, Any]], flagged: list[dict[str, Any]]) -> None:
    high = sum(1 for x in flagged if x.get("risk_level") == "HIGH")
    medium = sum(1 for x in flagged if x.get("risk_level") == "MEDIUM")
    safe = max(len(articles) - len(flagged), 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Articles Scanned", str(len(articles)), "Total records inspected"), unsafe_allow_html=True)
    c2.markdown(metric_card("Threats Intercepted", str(len(flagged)), "All flagged incidents"), unsafe_allow_html=True)
    c3.markdown(metric_card("High Risk", str(high), "Immediate action required"), unsafe_allow_html=True)
    c4.markdown(metric_card("Safe Waters", str(safe), "Passed without alert"), unsafe_allow_html=True)


def build_excerpt(post: dict[str, Any], limit: int = 180) -> str:
    text = post.get("description") or post.get("selftext") or ""
    text = " ".join(str(text).split())
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text or "No description available."


def render_timeline(alerts: list[dict[str, Any]], show_safe: bool) -> None:
    if not alerts:
        st.success("Scan complete! No malicious packages or scams detected in this batch.")
        return

    st.markdown("### 🗺️ Scout Logs")
    st.markdown("<div class='panel-subtle'>A living timeline of what the lookout intercepted on your behalf.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    for idx, alert in enumerate(alerts, start=1):
        risk_level = alert["risk_level"]
        if risk_level == "LOW" and not show_safe:
            continue

        outer_cls, risk_cls = risk_classes(risk_level)
        badge_label = {
            "HIGH": "BLOCKED",
            "MEDIUM": "SUSPICIOUS",
            "LOW": "SAFE WATERS",
        }.get(risk_level, "REVIEW")

        avatar = "🏴‍☠️" if risk_level == "HIGH" else "🧭" if risk_level == "MEDIUM" else "⚓"
        title = alert.get("title", "Untitled post")
        excerpt = build_excerpt(alert, 220)
        author = alert.get("author", "unknown")
        url = alert.get("url", "#")
        confidence = int(round(float(alert.get("confidence", 0.0)) * 100))
        source = alert.get("source", "Coral SQL")
        summary = alert.get("summary", "Analysis complete.")
        score = alert.get("ups", alert.get("score", "—"))
        tags = alert.get("signals", []) or []
        sig_text = ", ".join(tags[:3]) if tags else "No keyword hits"

        st.markdown(
            f"""
            <div class="timeline-item {outer_cls}">
              <div class="timeline-head">
                <div class="risk-badge {risk_cls}">{avatar} [{badge_label}] {risk_level}</div>
                <div class="status-note">Incident #{idx:02d} · Source: {source}</div>
              </div>
              <div class="timeline-title">{title}</div>
              <div class="timeline-text">{excerpt}</div>
              <div class="timeline-meta">
                <span class="meta-chip">👤 u/{author}</span>
                <span class="meta-chip">⬆ {score} ups</span>
                <span class="meta-chip">🎯 Confidence {confidence}%</span>
                <span class="meta-chip">🔍 {alert.get('violation_type', 'None')}</span>
              </div>
              <div class="timeline-foot"><strong>Rationale:</strong> {summary} · <strong>Signals:</strong> {sig_text}</div>
              <div style="margin-top:0.65rem; font-size:0.88rem; color:#394150;">
                🔗 <a href="{url}" target="_blank" style="color:#304b73; text-decoration: underline;">Open original post</a>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_console() -> None:
    st.markdown(
        """
        <div class="console-card">
          <div class="command-kicker">Interactive Center</div>
          <div class="command-title">Command Console</div>
          <div class="panel-subtle" style="margin-top:0.45rem;">Ask the guardian to scan a feed, recheck a thread, or explain an alert in plain language.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Data pipeline
# -----------------------------
def run_scan(source_mode: str, scan_mode: str) -> list[dict[str, Any]]:
    articles = fetch_devto_data(source_mode=source_mode)
    alerts: list[dict[str, Any]] = []
    for item in articles:
        title = item.get("title", "Untitled")
        description = item.get("description", "")
        analysis = scan_post_content(title, description, scan_mode=scan_mode)
        alerts.append(
            {
                **item,
                **analysis,
                "source": source_mode,
                "url": item.get("url", "#"),
            }
        )
    return alerts


# -----------------------------
# App
# -----------------------------
def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🏴‍☠️", layout="wide", initial_sidebar_state="expanded")
    inject_styles()

    with st.sidebar:
        st.markdown("## Mission Control")
        st.markdown("<div class='panel-subtle'>Personal cyber companion for Dev.to moderation</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)

        scan_mode = st.selectbox(
            "Scan mode",
            ["All Threats", "Malicious Packages", "Phishing & Scams", "PII Leak"],
            index=0,
        )
        source_mode = st.radio("Feed source", ["Coral SQL", "Demo fallback"], index=0)
        show_safe_logs = st.toggle("Show safe logs", value=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-box'>")
        st.markdown("<div style='font-size:0.82rem; font-weight:900; text-transform:uppercase; letter-spacing:0.08em; color:#6b5a34;'>Coral mapping</div>", unsafe_allow_html=True)
        st.code(CORAL_MAPPING, language="text")
        st.markdown("<div class='pirate-ribbon'><span class='pirate-badge'>⚓ Coral mapping</span><span class='pirate-badge'>🗺️ Dev.to path</span><span class='pirate-badge'>💎 Legend</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        yaml_bytes = CORAL_YAML_PATH.read_bytes() if CORAL_YAML_PATH.exists() else b""
        st.download_button(
            "Download Coral connector YAML",
            data=yaml_bytes,
            file_name=CORAL_YAML_PATH.name,
            mime="text/yaml",
            use_container_width=True,
        )

        execute = st.button("⚓ Execute Live Scan", use_container_width=True, key="execute_live_scan")
        purge_safe = st.button("🧹 Purge Safe Logs", use_container_width=True, key="purge_safe_logs")
        deep_scan = st.button("⚡ Deep Scan Live Feed", use_container_width=True, key="deep_scan_sidebar")

        if deep_scan:
            st.toast("Deep scan set for next execution.")

        st.markdown("<div class='footer-note'>Tip: switch to Demo fallback when Coral is offline. The UI stays live.</div>", unsafe_allow_html=True)

    # Decorative top banner
    render_pirate_chrome()
    render_banner()

    # Data load
    if "alerts" not in st.session_state or execute:
        with st.spinner("Charting the feed and consulting the oracle..."):
            st.session_state["alerts"] = run_scan(source_mode, scan_mode)
            st.session_state["scan_mode"] = scan_mode
            st.session_state["source_mode"] = source_mode

    alerts = list(st.session_state.get("alerts", []))

    # Optionally purge safe logs in-memory for cleaner demo focus.
    if purge_safe:
        alerts = [a for a in alerts if a.get("risk_level") != "LOW"]
        st.session_state["alerts"] = alerts
        st.toast("Safe logs purged from view.")

    if alerts:
        flagged = [a for a in alerts if a.get("risk_level") in {"HIGH", "MEDIUM"}]
    else:
        flagged = []

    # Hero + status section
    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-grid">
            <div class="floating-coin left">💎</div>
            <div class="floating-coin right">🪙</div>
            <div>
              <h1 class="title">The Coral Lookout</h1>
              <div class="subtitle">pirate-style personal AI agent</div>
              <div class="hero-copy">
                Watching developer feeds for scams, malicious packages, and leaked secrets — with Coral as the chart and Gemini or heuristics as the oracle.
              </div>
              <div class="terminal-line">Watching your back across the Dev.to channels...</div>
              <div class="terminal-line">Current Task: Consulting the Cartographer's Ledger...</div>
            </div>
            <div>
              <div class="banner-card" style="padding:0.9rem 0.95rem; background: rgba(238,231,217,0.16); border-color: rgba(255,255,255,0.08);">
                <div class="banner-title" style="font-size:1.05rem; color:#f3c546;">🗝️ Deck Notes</div>
                <div class="banner-copy" style="color:#d9dbe2; margin-top:0.35rem;">
                  A single scroll shows the current mode, intercepted incidents, and where the ship is sailing next.
                </div>
                <div class="chip-row">
                  <span class="chip">⚓ Coral SQL</span>
                  <span class="chip">💎 Threat jewels</span>
                  <span class="chip">🪙 Pirate UI</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_status_hub(alerts, flagged, st.session_state.get("source_mode", source_mode))

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    render_metrics(alerts, flagged)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.35, 0.95], gap="large")

    with left:
        st.markdown("### Scout Logs")
        render_timeline(alerts, show_safe_logs)

    with right:
        render_console()
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="console-card console-input">
              <div class="panel-subtle" style="margin-bottom:0.6rem;">Command prompt</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        command = st.text_area(
            "",
            placeholder="> Ask Guardian to scan a specific URL, explain a risk, or replay the latest alert...",
            height=120,
            label_visibility="collapsed",
        )
        quick1, quick2 = st.columns(2)
        with quick1:
            st.button("⚡ Deep Scan Live Feed", use_container_width=True, key="deep_scan_main")
        with quick2:
            st.button("🧽 Clear Safe Logs", use_container_width=True, key="clear_safe_logs")

        if command.strip():
            st.info("Command received. Hook this input to a planner or chat loop next.")

        st.markdown(
            """
            <div class="console-card" style="margin-top:0.75rem;">
              <div class="panel-title">Port Chart</div>
              <div class="panel-subtle">Coral is the chart room. Streamlit is the captain's deck. The ship animation marks the voyage from live feed to verdict.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Data summary table for quick debugging
    if alerts:
        df = pd.DataFrame(
            [
                {
                    "title": a.get("title", ""),
                    "risk": a.get("risk_level", "LOW"),
                    "violation": a.get("violation_type", "None"),
                    "author": a.get("author", ""),
                }
                for a in alerts
            ]
        )
        with st.expander("Raw scan summary", expanded=False):
            st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
