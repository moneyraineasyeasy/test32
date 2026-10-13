# aegisultra_app.py
#
# AEGIS ULTRA V3 Streamlit Command Center
#
# Compatible with:
# - aegisultra_enginev2.py
# - aegisultra_enginev3.py
#
# Important:
# CORRECT_SCORE is not an engine input market. Correct-score
# references are generated automatically from the FT model.

from __future__ import annotations

import hashlib
import html
import importlib
import json
import math
import os
import traceback
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

os.environ["ARROW_DEFAULT_MEMORY_POOL"] = "system"

import pandas as pd
import streamlit as st

import aegisultra_enginev2 as aegis_v2
import aegisultra_enginev3 as aegis


# ============================================================
# 1. Reload engine modules
# ============================================================

importlib.invalidate_caches()

aegis_v2 = importlib.reload(
    aegis_v2
)

aegis = importlib.reload(
    aegis
)


APP_NAME = "AEGIS ULTRA"
APP_VERSION = "3.1.0"

ENGINE_NAME = getattr(
    aegis,
    "ENGINE_NAME",
    "Aegis Ultra Engine",
)

ENGINE_VERSION = getattr(
    aegis,
    "ENGINE_VERSION",
    "Unknown",
)

DEFAULT_API_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwhceZ9-Z-n4R7U-ctJsLrmZuSiy98MtCPgUIw26ZOM9tv2Y5WPt7af56mJJ8M4pbqfww/"
    "exec"
)

PERIOD_ORDER = {
    "FT": 0,
    "HT": 1,
}

SUPPORTED_INPUT_MARKETS = {
    "1X2",
    "AH",
    "OU",
    "HHAD",
    "TEAM_OU",
}


# ============================================================
# 2. Page configuration
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 3. Styling
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #080a11;
        --surface: rgba(255,255,255,0.045);
        --border: rgba(255,255,255,0.09);
        --green: #32d9a1;
        --blue: #7388ff;
        --purple: #ae72ff;
        --amber: #ffbd59;
        --red: #ff6577;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(81,102,255,0.15),
                transparent 29%
            ),
            radial-gradient(
                circle at 90% 2%,
                rgba(172,81,255,0.12),
                transparent 26%
            ),
            linear-gradient(
                180deg,
                #090b13 0%,
                #0d1019 48%,
                #080a11 100%
            );
    }

    .block-container {
        max-width: 1540px;
        padding-top: 1.25rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(16,19,31,0.99),
                rgba(8,10,17,0.99)
            );
        border-right: 1px solid var(--border);
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.15rem;
        margin-bottom: 1.25rem;
        border-radius: 24px;
        background:
            linear-gradient(
                120deg,
                rgba(76,95,255,0.23),
                rgba(150,68,255,0.16),
                rgba(0,214,170,0.09)
            );
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 18px 60px rgba(0,0,0,0.36);
    }

    .hero-badge {
        display: inline-block;
        padding: 0.38rem 0.75rem;
        margin-bottom: 0.9rem;
        border-radius: 999px;
        color: #c6ffee;
        background: rgba(0,214,163,0.12);
        border: 1px solid rgba(0,214,163,0.27);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
    }

    .hero-title {
        margin: 0;
        color: white;
        font-size: 3rem;
        font-weight: 850;
        letter-spacing: -0.055em;
    }

    .hero-text {
        max-width: 1050px;
        margin-top: 0.72rem;
        color: rgba(255,255,255,0.70);
        line-height: 1.65;
    }

    .summary-card {
        min-height: 125px;
        padding: 1.05rem 1.15rem;
        border-radius: 17px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.085);
        box-shadow: 0 10px 32px rgba(0,0,0,0.20);
    }

    .summary-label {
        color: rgba(255,255,255,0.50);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .summary-value {
        margin-top: 0.42rem;
        color: white;
        font-size: 1.55rem;
        font-weight: 850;
    }

    .summary-note {
        margin-top: 0.35rem;
        color: rgba(255,255,255,0.48);
        font-size: 0.8rem;
    }

    .status-pass {
        color: var(--green);
    }

    .status-caution {
        color: var(--amber);
    }

    .status-fail {
        color: var(--red);
    }

    .recommendation-card {
        padding: 1.25rem 1.35rem;
        margin-bottom: 0.9rem;
        border-radius: 18px;
        background:
            linear-gradient(
                120deg,
                rgba(0,214,163,0.10),
                rgba(255,255,255,0.035)
            );
        border: 1px solid rgba(0,214,163,0.22);
        box-shadow: 0 12px 34px rgba(0,0,0,0.23);
    }

    .recommendation-rank {
        color: #7fffd3;
        font-size: 0.77rem;
        font-weight: 850;
        letter-spacing: 0.1em;
    }

    .recommendation-name {
        margin-top: 0.32rem;
        color: white;
        font-size: 1.35rem;
        font-weight: 850;
    }

    .recommendation-stats {
        margin-top: 0.55rem;
        color: rgba(255,255,255,0.66);
        font-size: 0.91rem;
        line-height: 1.65;
    }

    .period-badge {
        display: inline-block;
        padding: 0.26rem 0.62rem;
        margin-bottom: 0.4rem;
        border-radius: 999px;
        color: #bae6fd;
        background: rgba(56,189,248,0.11);
        border: 1px solid rgba(56,189,248,0.24);
        font-size: 0.72rem;
        font-weight: 850;
    }

    .score-card {
        text-align: center;
        min-height: 140px;
        padding: 1.25rem 0.85rem;
        border-radius: 18px;
        background:
            linear-gradient(
                145deg,
                rgba(130,91,255,0.16),
                rgba(255,255,255,0.035)
            );
        border: 1px solid rgba(151,120,255,0.22);
    }

    .score-value {
        color: white;
        font-size: 2rem;
        font-weight: 850;
    }

    .score-note {
        margin-top: 0.35rem;
        color: #d7ceff;
        font-size: 0.9rem;
    }

    textarea {
        font-family:
            "SFMono-Regular",
            Consolas,
            monospace !important;
        font-size: 0.86rem !important;
        line-height: 1.5 !important;
    }

    [data-testid="stMetric"] {
        padding: 0.9rem 1rem;
        border-radius: 15px;
        background: rgba(255,255,255,0.042);
        border: 1px solid rgba(255,255,255,0.075);
    }

    [data-testid="stDataFrame"] {
        overflow: hidden;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.075);
    }

    div[data-testid="stExpander"] {
        border-radius: 15px;
        background: rgba(255,255,255,0.018);
    }

    @media (max-width: 700px) {
        .hero-title {
            font-size: 2.15rem;
        }

        .hero {
            padding: 1.4rem 1.3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. Generic helpers
# ============================================================

def optional_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(number):
        return default

    return number


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    number = safe_float(value)

    if number is None:
        return default

    return int(number)


def html_escape(value: Any) -> str:
    return html.escape(
        str(value if value is not None else "—")
    )


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()

    if hasattr(value, "tolist"):
        return value.tolist()

    if isinstance(value, set):
        return list(value)

    return str(value)


def json_text(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=json_default,
    )


def format_probability(
    value: Any,
    digits: int = 1,
) -> str:
    number = safe_float(value)

    if number is None:
        return "—"

    if 1.0 < number <= 100.0:
        number /= 100.0

    return f"{number * 100:.{digits}f}%"


def format_odds(
    value: Any,
    digits: int = 3,
) -> str:
    number = safe_float(value)

    if number is None:
        return "—"

    return f"{number:.{digits}f}"


def format_ev(
    value: Any,
    digits: int = 2,
) -> str:
    number = safe_float(value)

    if number is None:
        return "—"

    return f"{number * 100:+.{digits}f}%"


def _fmt_market_change(value: Any) -> str:
    """把市場變動值格式化為帶正負號的 pp 字串，None 時回傳 —。"""
    number = safe_float(value)

    if number is None:
        return "—"

    return f"{number:+.2f}pp"


def probability_value(
    record: Dict[str, Any],
    metric: str,
    statistic: str = "minimum",
) -> Any:
    probability = record.get(
        "probability",
        {},
    )

    if not isinstance(probability, dict):
        return None

    metric_record = probability.get(
        metric,
        {},
    )

    if not isinstance(metric_record, dict):
        return None

    return metric_record.get(
        statistic
    )


def summary_value(
    record: Dict[str, Any],
    field: str,
    statistic: str = "minimum",
) -> Any:
    section = record.get(
        field,
        {},
    )

    if isinstance(section, dict):
        return section.get(
            statistic
        )

    return section


def status_chinese(status: Any) -> str:
    translations = {
        "PASS": "通過",
        "CAUTION": "注意",
        "FAIL": "失敗",
        "COMPLETED": "已完成",
        "NOT_AVAILABLE": "不適用",
        "NOT_PROVIDED": "未提供",
        "NOT_TESTABLE": "無法測試",
        "DISABLED": "已停用",
        "ROBUST": "穩健",
        "FRAGILE": "脆弱",
        "OFFICIAL": "正式推薦",
        "REFERENCE_ONLY": "僅供參考",
        "FAIR_OR_BETTER": "價格合理或更佳",
        "MIXED_PRICE": "價格訊號混合",
        "SLIGHTLY_UNDERPAID": "輕微回報不足",
        "POOR_PRICE": "價格偏差",
        "SEVERELY_UNDERPAID": "嚴重回報不足",
        "SUPPORTED": "支持",
        "CONFLICTED": "衝突",
        "NEUTRAL": "中性",
        "STRONG": "強",
        "MODERATE": "中等",
        "WEAK": "弱",
        "NONE": "沒有",
        "UNKNOWN": "未知",
    }

    text = optional_text(
        status
    ).upper() or "UNKNOWN"

    return translations.get(
        text,
        text.replace("_", " "),
    )


def status_css_class(status: Any) -> str:
    value = optional_text(
        status
    ).upper()

    if value in {
        "PASS",
        "COMPLETED",
        "SUPPORTED",
        "ROBUST",
        "OFFICIAL",
        "FAIR_OR_BETTER",
    }:
        return "status-pass"

    if value in {
        "CAUTION",
        "NEUTRAL",
        "NOT_AVAILABLE",
        "NOT_PROVIDED",
        "NOT_TESTABLE",
        "DISABLED",
        "FRAGILE",
        "MIXED_PRICE",
    }:
        return "status-caution"

    return "status-fail"


def result_summary_card(
    label: str,
    value: str,
    note: str,
    css_class: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">
                {html_escape(label)}
            </div>
            <div class="summary-value {css_class}">
                {html_escape(value)}
            </div>
            <div class="summary-note">
                {html_escape(note)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def download_name(prefix: str) -> str:
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"{prefix}_{timestamp}.json"


# ============================================================
# 5. Example V3 input
# ============================================================

def example_json_input() -> Dict[str, Any]:
    return {
        "match": {
            "name": "主隊 vs 客隊",
            "home": "主隊",
            "away": "客隊",
            "competition": "示例賽事",
            "kickoff": "",
            "snapshot_time": (
                datetime.now()
                .astimezone()
                .isoformat(
                    timespec="minutes"
                )
            ),
        },
        "sharp_books": [
            {
                "key": "pinnacle",
                "title": "Pinnacle",
                "markets": {
                    "FT": {
                        "1X2": {
                            "home": 2.12,
                            "draw": 3.35,
                            "away": 3.55,
                        },
                        "AH": [
                            {
                                "line": -0.25,
                                "home": 1.95,
                                "away": 1.95,
                            }
                        ],
                        "OU": [
                            {
                                "line": 2.25,
                                "over": 1.92,
                                "under": 1.98,
                            }
                        ],
                        "HHAD": [],
                        "TEAM_OU": [],
                    },
                    "HT": {
                        "1X2": {
                            "home": 2.75,
                            "draw": 2.10,
                            "away": 4.10,
                        },
                        "AH": [
                            {
                                "line": 0.0,
                                "home": 1.62,
                                "away": 2.28,
                            }
                        ],
                        "OU": [
                            {
                                "line": 1.0,
                                "over": 1.92,
                                "under": 1.98,
                            }
                        ],
                        "HHAD": [],
                        "TEAM_OU": [],
                    },
                },
            }
        ],
        "hkjc_markets": [
            {
                "id": "M001",
                "period": "FT",
                "market": "AH",
                "selection": "HOME",
                "line": -0.25,
                "odds": 1.95,
                "label": "主隊 全場 AH -0.25",
            },
            {
                "id": "M002",
                "period": "FT",
                "market": "OU",
                "selection": "UNDER",
                "line": 2.25,
                "odds": 1.88,
                "label": "全場入球細 2.25",
            },
            {
                "id": "M003",
                "period": "HT",
                "market": "OU",
                "selection": "UNDER",
                "line": 1.0,
                "odds": 1.90,
                "label": "半場入球細 1.0",
            },
        ],
        "odds_movements": [],
        "settings": {
            "minimum_odds": 1.50,
            "maximum_odds": None,
            "max_recommendations": 3,
            "minimum_official_hit_probability": 0.50,
            "correct_score_count": 2,
            "devig_methods": [
                "MULTIPLICATIVE",
                "POWER",
                "SHIN",
            ],
            "primary_source": "pinnacle",
            "ev_rejection_floor": None,
            "features": {
                "quality_gate": True,
                "stress_audit": True,
                "family_out_audit": True,
                "adaptive_grids": True,
                "ht_ft_coherence": True,
                "prior_comparison": True,
                "odds_shift_analysis": True,
            },
            "movement": {
                "neutral_threshold_pp": 0.50,
                "strong_threshold_pp": 2.00,
                "minimum_external_books": 2,
                "minimum_agreement": 0.60,
                "strong_agreement": 0.75,
                "adjacent_line_tolerance": 0.50,
            },
        },
    }


# ============================================================
# 6. Input compatibility validation
# ============================================================

def reject_unsupported_correct_score_inputs(
    input_data: Dict[str, Any],
) -> None:
    """
    Engine V3 generates correct-score references from the FT
    score distribution. It does not accept CORRECT_SCORE as a
    sharp constraint or HKJC candidate market.
    """

    for book in input_data.get(
        "sharp_books",
        [],
    ):
        if not isinstance(book, dict):
            continue

        markets = book.get(
            "markets",
            {},
        )

        if not isinstance(markets, dict):
            continue

        for period in [
            "FT",
            "HT",
        ]:
            block = markets.get(
                period,
                {},
            )

            if (
                isinstance(block, dict)
                and block.get(
                    "CORRECT_SCORE"
                )
            ):
                raise ValueError(
                    "Engine V3 不接受 CORRECT_SCORE 作為"
                    "尖銳市場約束。請移除 sharp_books 內的 "
                    "CORRECT_SCORE。波膽參考會由 FT 模型"
                    "自動產生。"
                )

    for candidate in input_data.get(
        "hkjc_markets",
        [],
    ):
        if not isinstance(candidate, dict):
            continue

        market = optional_text(
            candidate.get("market")
        ).upper()

        if market in {
            "CORRECT_SCORE",
            "EXACT_SCORE",
            "CS",
        }:
            raise ValueError(
                "Engine V3 不接受 CORRECT_SCORE 作為 "
                "HKJC 候選盤。請移除此候選盤。"
                "波膽參考會由 FT 模型自動產生。"
            )


def normalize_v3_input(
    input_data: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(input_data, dict):
        raise ValueError(
            "輸入 JSON 最外層必須是 object。"
        )

    data = deepcopy(
        input_data
    )

    reject_unsupported_correct_score_inputs(
        data
    )

    settings = data.setdefault(
        "settings",
        {},
    )

    if not isinstance(settings, dict):
        raise ValueError(
            "settings 必須是 object。"
        )

    settings.setdefault(
        "devig_methods",
        [
            "MULTIPLICATIVE",
            "POWER",
            "SHIN",
        ],
    )

    features = settings.setdefault(
        "features",
        {},
    )

    if not isinstance(features, dict):
        features = {}
        settings["features"] = features

    features.setdefault(
        "quality_gate",
        True,
    )

    features.setdefault(
        "stress_audit",
        True,
    )

    features.setdefault(
        "family_out_audit",
        True,
    )

    features.setdefault(
        "adaptive_grids",
        True,
    )

    features.setdefault(
        "ht_ft_coherence",
        True,
    )

    features.setdefault(
        "prior_comparison",
        True,
    )

    features.setdefault(
        "odds_shift_analysis",
        True,
    )

    movement = settings.setdefault(
        "movement",
        {},
    )

    if not isinstance(movement, dict):
        movement = {}
        settings["movement"] = movement

    movement.setdefault(
        "neutral_threshold_pp",
        0.50,
    )

    movement.setdefault(
        "strong_threshold_pp",
        2.00,
    )

    movement.setdefault(
        "minimum_external_books",
        2,
    )

    movement.setdefault(
        "minimum_agreement",
        0.60,
    )

    movement.setdefault(
        "strong_agreement",
        0.75,
    )

    movement.setdefault(
        "adjacent_line_tolerance",
        0.50,
    )

    data.setdefault(
        "odds_movements",
        [],
    )

    return data


# ============================================================
# 7. Cached engine execution
# ============================================================

@st.cache_data(
    show_spinner=False,
    max_entries=24,
)
def cached_engine_run(
    canonical_json: str,
    engine_fingerprint: str,
) -> Dict[str, Any]:
    del engine_fingerprint

    return aegis.run_engine(
        json.loads(
            canonical_json
        )
    )


def engine_fingerprint() -> str:
    content = b""

    modules = [
        aegis_v2,
        aegis,
    ]

    seen_paths = set()

    for module in modules:
        path = getattr(
            module,
            "__file__",
            None,
        )

        if (
            not path
            or path in seen_paths
        ):
            continue

        seen_paths.add(
            path
        )

        try:
            with open(
                path,
                "rb",
            ) as file:
                content += file.read()

        except OSError:
            content += optional_text(
                path
            ).encode("utf-8")

    return hashlib.sha256(
        content
    ).hexdigest()


def execute_engine(
    input_data: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = normalize_v3_input(
        input_data
    )

    canonical = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=json_default,
    )

    fingerprint = engine_fingerprint()

    analysis_hash = hashlib.sha256(
        (
            canonical
            + fingerprint
        ).encode("utf-8")
    ).hexdigest()

    if (
        st.session_state.get(
            "analysis_hash"
        )
        == analysis_hash
        and st.session_state.get(
            "result"
        )
        is not None
    ):
        return st.session_state[
            "result"
        ]

    result = cached_engine_run(
        canonical,
        fingerprint,
    )

    st.session_state[
        "analysis_hash"
    ] = analysis_hash

    st.session_state[
        "result"
    ] = result

    st.session_state[
        "input_snapshot"
    ] = result.get(
        "input_snapshot",
        normalized,
    )

    return result


# ============================================================
# 8. Result renderers
# ============================================================

def recommendation_card(
    recommendation: Dict[str, Any],
) -> None:
    rank = recommendation.get(
        "rank",
        recommendation.get(
            "official_rank",
            "—",
        ),
    )

    hit_min = probability_value(
        recommendation,
        "hit",
        "minimum",
    )

    hit_median = probability_value(
        recommendation,
        "hit",
        "median",
    )

    nonloss = probability_value(
        recommendation,
        "nonloss",
        "minimum",
    )

    full_loss = probability_value(
        recommendation,
        "full_loss",
        "maximum",
    )

    ev_min = summary_value(
        recommendation,
        "expected_return",
        "minimum",
    )

    shift = recommendation.get(
        "odds_shift",
        {},
    )

    shift_text = ""

    if isinstance(shift, dict):
        verdict = shift.get(
            "verdict"
        )

        strength = shift.get(
            "strength"
        )

        if verdict:
            shift_text = (
                "<br>市場走勢："
                f"<b>{html_escape(status_chinese(verdict))}</b>"
                "｜強度："
                f"<b>{html_escape(status_chinese(strength))}</b>"
            )

    st.markdown(
        f"""
        <div class="recommendation-card">
            <div class="period-badge">
                {html_escape(recommendation.get("period", "FT"))}
            </div>
            <div class="recommendation-rank">
                OFFICIAL PICK #{html_escape(rank)}
            </div>
            <div class="recommendation-name">
                {html_escape(recommendation.get("label", "—"))}
            </div>
            <div class="recommendation-stats">
                HKJC 賠率：
                <b>{format_odds(recommendation.get("hkjc_odds"))}</b>
                ｜保守命中率：
                <b>{format_probability(hit_min)}</b>
                ｜中位命中率：
                <b>{format_probability(hit_median)}</b>
                ｜保守不輸率：
                <b>{format_probability(nonloss)}</b>
                <br>
                最大全輸率：
                <b>{format_probability(full_loss)}</b>
                ｜保守 EV：
                <b>{format_ev(ev_min)}</b>
                ｜價格：
                <b>{html_escape(
                    status_chinese(
                        recommendation.get("price_status")
                    )
                )}</b>
                {shift_text}
            </div>
            <div class="recommendation-stats" style="margin-top:4px;padding-top:4px;border-top:1px dashed rgba(255,255,255,0.15);">
                <b>市場共識：</b>
                {
                    f'{safe_float(recommendation.get("consensus_pct"), 0.0) * 100:.0f}%'
                    if recommendation.get("consensus_pct") is not None
                    else '—'
                }
                ｜<b>Pinnacle 對齊：</b>
                {
                    '✅ 是'
                    if recommendation.get("pinnacle_alignment") is True
                    else (
                        '❌ 否'
                        if recommendation.get("pinnacle_alignment") is False
                        else '—'
                    )
                }
                ｜<b>平均偏差：</b>
                {
                    f'{safe_float(recommendation.get("mean_deviation_pp"), 0.0):.1f}pp'
                    if recommendation.get("mean_deviation_pp") is not None
                    else '—'
                }
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def candidate_dataframe(
    candidates: List[Dict[str, Any]],
) -> pd.DataFrame:
    rows = []

    for candidate in candidates:
        shift = candidate.get(
            "odds_shift",
            {},
        )

        if not isinstance(shift, dict):
            shift = {}

        prior_comparison = candidate.get(
            "pre_projection_prior_comparison",
            {},
        )

        disparity = (
            prior_comparison.get(
                "disparity",
                {},
            )
            if isinstance(
                prior_comparison,
                dict,
            )
            else {}
        )

        reasons = []

        for key in [
            "exclusion_reasons",
            "official_exclusion_reasons",
        ]:
            values = candidate.get(
                key,
                [],
            )

            if isinstance(values, list):
                reasons.extend(
                    optional_text(value)
                    .replace("_", " ")
                    for value in values
                )

        rows.append({
            "正式": (
                "✅"
                if candidate.get("official")
                else ""
            ),
            "排名": candidate.get(
                "official_rank"
            ),
            "ID": candidate.get("id"),
            "候選盤": candidate.get(
                "label"
            ),
            "時段": candidate.get(
                "period"
            ),
            "市場": candidate.get(
                "market"
            ),
            "HKJC 賠率": candidate.get(
                "hkjc_odds"
            ),
            "保守命中率": format_probability(
                probability_value(
                    candidate,
                    "hit",
                    "minimum",
                )
            ),
            "中位命中率": format_probability(
                probability_value(
                    candidate,
                    "hit",
                    "median",
                )
            ),
            "保守不輸率": format_probability(
                probability_value(
                    candidate,
                    "nonloss",
                    "minimum",
                )
            ),
            "保守 EV": format_ev(
                summary_value(
                    candidate,
                    "expected_return",
                    "minimum",
                )
            ),
            "價格": status_chinese(
                candidate.get(
                    "price_status"
                )
            ),
            "Prior 差距": format_probability(
                disparity.get(
                    "median_hit_range"
                ),
                2,
            ),
            "走勢": status_chinese(
                shift.get(
                    "verdict",
                    "NOT_AVAILABLE",
                )
            ),
            "走勢強度": status_chinese(
                shift.get(
                    "strength",
                    "NONE",
                )
            ),
            "市場變動": (
                _fmt_market_change(
                    shift.get(
                        "market_implied_probability_change_pp"
                    )
                )
            ),
            "排除原因": "；".join(
                reasons
            ),
            "共識度": (
                f"{safe_float(candidate.get('consensus_pct'), 0.0) * 100:.0f}%"
                if candidate.get("consensus_pct") is not None
                else "—"
            ),
            "Pinnacle 對齊": (
                "✅ 是"
                if candidate.get("pinnacle_alignment")
                else (
                    "❌ 否"
                    if candidate.get("pinnacle_alignment") is False
                    else "—"
                )
            ),
            "平均偏差(pp)": (
                f"{safe_float(candidate.get('mean_deviation_pp'), 0.0):.1f}"
                if candidate.get("mean_deviation_pp") is not None
                else "—"
            ),
        })

    return pd.DataFrame(
        rows
    )


def consensus_dataframe(
    records: List[Dict[str, Any]],
) -> pd.DataFrame:
    """把 market consensus 檢查結果整理成顯示用的 dataframe。"""
    if not records:
        return pd.DataFrame()

    rows = []

    for record in records:
        rows.append({
            "市場": record.get("market"),
            "時段": record.get("period"),
            "選項": record.get("selection"),
            "線位": (
                f'{safe_float(record.get("line"), 0.0):.2f}'
                if record.get("line") is not None
                else "—"
            ),
            "Pinnacle 機率": format_probability(
                record.get("pinnacle_probability"),
            ),
            "共識度": (
                f'{safe_float(record.get("consensus_pct"), 0.0) * 100:.0f}%'
                if record.get("consensus_pct") is not None
                else "—"
            ),
            "Pinnacle 對齊": (
                "✅ 是"
                if record.get("pinnacle_alignment")
                else (
                    "❌ 否"
                    if record.get("pinnacle_alignment") is False
                    else "—"
                )
            ),
            "平均偏差(pp)": (
                f'{safe_float(record.get("mean_deviation_pp"), 0.0):.2f}'
                if record.get("mean_deviation_pp") is not None
                else "—"
            ),
            "最大偏差(pp)": (
                f'{safe_float(record.get("max_deviation_pp"), 0.0):.2f}'
                if record.get("max_deviation_pp") is not None
                else "—"
            ),
            "莊家數": record.get("n_books"),
        })

    return pd.DataFrame(
        rows
    )


def prior_dataframe(
    candidate: Dict[str, Any],
) -> pd.DataFrame:
    comparison = candidate.get(
        "pre_projection_prior_comparison",
        {},
    )

    priors = (
        comparison.get(
            "priors",
            {},
        )
        if isinstance(
            comparison,
            dict,
        )
        else {}
    )

    rows = []

    for prior_name in [
        "DIXON_COLES",
        "INDEPENDENT_POISSON",
        "COM_POISSON",
    ]:
        record = priors.get(
            prior_name,
            {},
        )

        if not record.get(
            "available"
        ):
            rows.append({
                "Prior": prior_name,
                "可用": "否",
                "情境數": 0,
                "最低命中率": "—",
                "中位命中率": "—",
                "最高命中率": "—",
                "中位 EV": "—",
                "中位公平賠率": "—",
            })
            continue

        hit = (
            record.get(
                "probability",
                {},
            ).get(
                "hit",
                {},
            )
        )

        expected_return = record.get(
            "expected_return",
            {},
        )

        fair_odds = record.get(
            "fair_odds",
            {},
        )

        rows.append({
            "Prior": prior_name,
            "可用": "是",
            "情境數": record.get(
                "scenario_count"
            ),
            "最低命中率": format_probability(
                hit.get("minimum"),
                2,
            ),
            "中位命中率": format_probability(
                hit.get("median"),
                2,
            ),
            "最高命中率": format_probability(
                hit.get("maximum"),
                2,
            ),
            "中位 EV": format_ev(
                expected_return.get(
                    "median"
                )
            ),
            "中位公平賠率": format_odds(
                fair_odds.get(
                    "median"
                )
            ),
        })

    return pd.DataFrame(
        rows
    )



def movement_dataframe(
    audits: List[Dict[str, Any]],
) -> pd.DataFrame:
    rows = []

    for audit in audits:
        primary = audit.get(
            "pinnacle_confirmation",
            {},
        )

        hkjc = audit.get(
            "hkjc_response",
            {},
        )

        rows.append({
            "ID": audit.get("id"),
            "候選盤": audit.get(
                "label"
            ),
            "時段": audit.get(
                "period"
            ),
            "市場": audit.get(
                "market"
            ),
            "結果": status_chinese(
                audit.get(
                    "verdict"
                )
            ),
            "強度": status_chinese(
                audit.get(
                    "strength"
                )
            ),
            "外部莊家數": audit.get(
                "external_book_count"
            ),
            "一致比例": format_probability(
                audit.get(
                    "agreement_ratio"
                )
            ),
            "開盤概率": format_probability(
                audit.get(
                    "consensus_opening_probability"
                ),
                2,
            ),
            "最新概率": format_probability(
                audit.get(
                    "consensus_latest_probability"
                ),
                2,
            ),
            "概率變動": (
                _fmt_market_change(
                    audit.get(
                        "market_implied_probability_change_pp"
                    )
                )
            ),
            "Pinnacle": status_chinese(
                primary.get(
                    "status"
                )
            ),
            "HKJC": status_chinese(
                hkjc.get(
                    "status"
                )
            ),
            "行動提示": optional_text(
                audit.get(
                    "actionability"
                )
            ).replace("_", " "),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# 9. Portal helpers
# ============================================================

def configured_api_url() -> str:
    try:
        value = optional_text(
            st.secrets[
                "portal_api"
            ]["url"]
        )

        if value:
            return value

    except Exception:
        pass

    return (
        optional_text(
            os.getenv(
                "AEGIS_API_URL"
            )
        )
        or DEFAULT_API_URL
    )


def configured_api_token() -> str:
    try:
        value = optional_text(
            st.secrets[
                "portal_api"
            ]["token"]
        )

        if value:
            return value

    except Exception:
        pass

    return optional_text(
        os.getenv(
            "AEGIS_API_TOKEN"
        )
    )


def portal_request(
    payload: Dict[str, Any],
    timeout: int = 40,
) -> Dict[str, Any]:
    token = configured_api_token()

    if not token:
        raise ValueError(
            "Portal API token 未設定。"
        )

    request_payload = deepcopy(
        payload
    )

    request_payload[
        "token"
    ] = token

    request = urllib.request.Request(
        configured_api_url(),
        data=json.dumps(
            request_payload,
            ensure_ascii=False,
            default=json_default,
        ).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": (
                "application/json; charset=utf-8"
            ),
            "Accept": "application/json",
            "User-Agent": (
                f"AEGIS-ULTRA/{APP_VERSION}"
            ),
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            text = (
                response.read()
                .decode(
                    "utf-8-sig",
                    errors="replace",
                )
            )

    except urllib.error.HTTPError as error:
        text = (
            error.read()
            .decode(
                "utf-8-sig",
                errors="replace",
            )
        )

        raise RuntimeError(
            f"API HTTP {error.code}: {text}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"無法連接 Portal API："
            f"{error.reason}"
        ) from error

    result = json.loads(
        text
    )

    if (
        not isinstance(result, dict)
        or result.get("ok") is not True
    ):
        raise RuntimeError(
            "Portal API 拒絕要求："
            + optional_text(
                result.get("error")
                if isinstance(result, dict)
                else result
            )
        )

    return result


def stable_match_id(
    result: Dict[str, Any],
) -> str:
    match = result.get(
        "match",
        {},
    )

    identity = "|".join([
        optional_text(
            match.get("home")
        ).casefold(),
        optional_text(
            match.get("away")
        ).casefold(),
        optional_text(
            match.get("competition")
        ).casefold(),
        optional_text(
            match.get("kickoff")
        ),
    ])

    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:20]

    return f"match_{digest}"


def build_portal_bundle(
    result: Dict[str, Any],
    selected_ids: set,
    publish_status: str,
) -> Dict[str, Any]:
    match = result.get(
        "match",
        {},
    )

    match_id = stable_match_id(
        result
    )

    records = []

    candidates = result.get(
        "candidate_markets",
        [],
    )

    for candidate in candidates:
        candidate_id = optional_text(
            candidate.get("id")
        )

        if candidate_id not in selected_ids:
            continue

        identity = "|".join([
            match_id,
            candidate_id,
            optional_text(
                candidate.get("period")
            ),
            optional_text(
                candidate.get("market")
            ),
            optional_text(
                candidate.get("selection")
            ),
            optional_text(
                candidate.get("line")
            ),
        ])

        rec_id = (
            "rec_"
            + hashlib.sha256(
                identity.encode("utf-8")
            ).hexdigest()[:22]
        )

        # 讀取手動 tier（session_state）
        manual_tier_key = (
            "manual_tier_"
            + candidate_id
        )

        manual_tier = (
            st.session_state.get(
                manual_tier_key
            )
            if manual_tier_key in st.session_state
            else None
        )

        if not manual_tier:
            manual_tier = (
                "OFFICIAL"
                if candidate.get("official")
                else "ALTERNATIVE"
            )

        # 讀取手動 commentary（session_state）
        manual_commentary_key = (
            "manual_commentary_"
            + candidate_id
        )

        manual_commentary = (
            st.session_state.get(
                manual_commentary_key
            )
            if manual_commentary_key in st.session_state
            else ""
        )

        records.append({
            "rec_id": rec_id,
            "match_id": match_id,
            "tier": manual_tier,
            "commentary": manual_commentary,
            "rank": (
                candidate.get(
                    "official_rank"
                )
                or 999
            ),
            "rec_title": candidate.get(
                "label"
            ),
            "market": candidate.get(
                "market"
            ),
            "selection": candidate.get(
                "selection"
            ),
            "line": (
                candidate.get("line")
                if candidate.get("line")
                is not None
                else ""
            ),
            "odds": candidate.get(
                "hkjc_odds"
            ),
            "conservative_hit": probability_value(
                candidate,
                "hit",
                "minimum",
            ),
            "median_hit": probability_value(
                candidate,
                "hit",
                "median",
            ),
            "nonloss_probability": probability_value(
                candidate,
                "nonloss",
                "minimum",
            ),
            "full_loss_probability": probability_value(
                candidate,
                "full_loss",
                "maximum",
            ),
            "fair_odds": summary_value(
                candidate,
                "fair_odds",
                "maximum",
            ),
            "price_status": candidate.get(
                "price_status"
            ),
            "stars": (
                4
                if candidate.get("official")
                else 3
            ),
            "is_heavy": False,
            "compatibility_group": "",
            "conflict_ids": "",
            "result": "pending",
            "status": publish_status,
            "period": candidate.get(
                "period"
            ),
            "market_scope": (
                candidate.get("team")
                or ""
            ),
            "edge": "",
            "expected_value": summary_value(
                candidate,
                "expected_return",
                "minimum",
            ),
        })

    return {
        "action": "publish_bundle",
        "replace_recommendations": True,
        "match": {
            "match_id": match_id,
            "match_name": (
                match.get("name")
                or (
                    f"{match.get('home', '')} "
                    f"vs {match.get('away', '')}"
                )
            ),
            "home_team": match.get(
                "home"
            ),
            "away_team": match.get(
                "away"
            ),
            "competition": match.get(
                "competition"
            ),
            "kickoff": match.get(
                "kickoff"
            ),
            "status": publish_status,
            "model_direction": (
                st.session_state.get(
                    "manual_model_direction"
                )
                if "manual_model_direction" in st.session_state
                and st.session_state.get(
                    "manual_model_direction"
                )
                else (
                    "；".join(
                        optional_text(
                            item.get("label")
                        )
                        for item in result.get(
                            "recommendations",
                            [],
                        )
                    )
                    or "沒有正式推薦"
                )
            ),
            "model_summary": (
                f"AEGIS Engine V{ENGINE_VERSION}"
            ),
            "top_scores": "",
            "final_score": "",
        },
        "recommendations": records,
    }


# ============================================================
# 10. Session state
# ============================================================

DEFAULTS = {
    "result": None,
    "input_snapshot": None,
    "analysis_hash": None,
    "error": None,
    "traceback": None,
    "json_input": json_text(
        example_json_input()
    ),
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[
            key
        ] = value


# ============================================================
# 11. Header
# ============================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-badge">
            ENGINE V{html_escape(ENGINE_VERSION)}
            · APP V{APP_VERSION}
        </div>
        <h1 class="hero-title">
            🛡️ AEGIS ULTRA V3
        </h1>
        <div class="hero-text">
            Sharp-market reconstruction with Multiplicative,
            Power and Shin de-vigging; Dixon–Coles,
            Independent Poisson and COM-Poisson prior
            comparison; target-line-out reconstruction;
            stress audits; HT–FT coherence; and structured
            external/Pinnacle/HKJC odds-movement analysis.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 12b. Odds movement input — multi-period / multi-market / multi-line
# ============================================================
#
# Replaces the old single-line, 2-way-or-3-way exclusive form.
# Structure: PERIOD  ->  MARKET  ->  one or more LINES (each with
# opening & closing odds for every outcome). Pinnacle and external
# books live in two separate blocks but share the same layout so the
# form mirrors what oddshub shows side by side.
#
# Backwards-compat: old "sharp_movements_v2" entries (single `line`,
# fields open_over/open_under/close_over) are upgraded on load.
# ============================================================

def _outcome_fields_for(
    market: str,
) -> tuple[list[str], list[str], list[str]]:
    """Return (open_fields, close_fields, labels) for a market."""

    if market in {"1X2", "HHAD"}:
        return (
            ["open_home", "open_draw", "open_away"],
            ["close_home", "close_draw", "close_away"],
            ["Home", "Draw", "Away"],
        )

    if market == "AH":
        return (
            ["open_home", "open_away"],
            ["close_home", "close_away"],
            ["Home", "Away"],
        )

    # OU and TEAM_OU
    return (
        ["open_over", "open_under"],
        ["close_over", "close_under"],
        ["Over", "Under"],
    )


def _default_line_record(
    market: str,
    line: float,
) -> Dict[str, Any]:
    """A blank line record with zeroed odds, ready for the user to fill."""

    open_fields, close_fields, _ = _outcome_fields_for(
        market
    )

    record: Dict[str, Any] = {
        "line": line,
        "market": market,
        "odds_format": "DECIMAL",
    }

    for field in open_fields + close_fields:
        record.setdefault(field, 1.90)

    return record


def _upgrade_legacy_entries(
    entries: list,
) -> list:
    """Promote the old single-`line` shape into the multi-line shape."""

    upgraded = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        if "lines" in entry and isinstance(
            entry["lines"], list
        ):
            upgraded.append(entry)

            continue

        market = entry.get("market", "OU")
        line_val = entry.get("line", 2.75)

        new_entry = {
            "bookmaker": entry.get("bookmaker", ""),
            "period": entry.get("period", "FT"),
            "market": market,
            "odds_format": entry.get(
                "odds_format", "DECIMAL"
            ),
            "lines": [],
        }

        record = _default_line_record(
            market,
            line_val,
        )

        # 2-way: copy the legacy box values across.
        for prefix, dest in (
            ("open", "open"),
            ("close", "close"),
        ):
            for side, field in (
                ("over", "over"),
                ("under", "under"),
            ):
                legacy = (
                    f"{prefix}_{side}"
                )

                if legacy in entry:
                    record[
                        f"{dest}_{field}"
                    ] = entry[legacy]

        new_entry["lines"].append(record)
        upgraded.append(new_entry)

    return upgraded


def _ensure_movement_session() -> None:
    """Seed the session structures if they are missing."""

    if "mv_periods" not in st.session_state:
        st.session_state["mv_periods"] = ["FT"]

    if "mv_pinnacle" not in st.session_state:
        st.session_state["mv_pinnacle"] = {
            "enabled": True,
            "odds_format": "DECIMAL",
            "markets": {
                "FT": {},
                "HT": {},
            },
        }

    if "mv_external" not in st.session_state:
        st.session_state["mv_external"] = {
            "FT": _upgrade_legacy_entries(
                [
                    {
                        "bookmaker": "bet365",
                        "period": "FT",
                        "market": "OU",
                        "line": 2.75,
                        "open_over": 1.90,
                        "open_under": 1.90,
                        "close_over": 2.00,
                        "close_under": 1.80,
                        "odds_format": "DECIMAL",
                    },
                    {
                        "bookmaker": "1xbet",
                        "period": "FT",
                        "market": "OU",
                        "line": 2.75,
                        "open_over": 1.88,
                        "open_under": 1.92,
                        "close_over": 1.98,
                        "close_over": 1.82,
                        "odds_format": "DECIMAL",
                    },
                ]
            ),
            "HT": [],
        }

    # Keep sharp_movements_v2 in sync so older code paths still work.
    flat = []

    for period in ("FT", "HT"):
        for entry in st.session_state[
            "mv_external"
        ].get(period, []):
            if not isinstance(entry, dict):
                continue

            lines = entry.get("lines") or []

            if not lines:
                continue

            first = dict(lines[0])
            first["bookmaker"] = entry.get(
                "bookmaker", ""
            )
            first["period"] = period
            first["market"] = entry.get("market", "OU")
            first["odds_format"] = entry.get(
                "odds_format", "DECIMAL"
            )

            flat.append(first)

    st.session_state["sharp_movements_v2"] = flat


def _market_block_editor(
    *,
    period: str,
    market: str,
    line_records: list,
    odds_format: str,
    key_prefix: str,
    show_bookmaker: bool = False,
    bookmaker: str = "",
) -> tuple[list, str, str]:
    """
    Edit the line list for one market. Returns the (possibly
    mutated) records, the odds format and the bookmaker title.
    """

    open_fields, close_fields, labels = _outcome_fields_for(
        market
    )

    edited: list = []
    current_format = odds_format
    current_bookmaker = bookmaker

    if show_bookmaker:
        current_bookmaker = st.text_input(
            "莊家名稱",
            value=bookmaker or "",
            key=f"{key_prefix}_bk",
            placeholder="例：bet365",
        )

    current_format = st.selectbox(
        "賠率格式",
        ["DECIMAL", "HK"],
        index=0 if odds_format == "DECIMAL" else 1,
        key=f"{key_prefix}_fmt",
    )

    for idx, record in enumerate(line_records):
        st.markdown(
            f"**Line {idx + 1}**"
        )

        line_val = record.get("line")

        if market in {"1X2", "HHAD"}:
            rendered_line = "—（讓球盤不適用）"
        else:
            rendered_line = safe_float(
                line_val, 0.0
            )

        col_line, col_open, col_close = st.columns(
            [1, 1.6, 1.6]
        )

        with col_line:
            if market in {"1X2", "HHAD"}:
                st.text_input(
                    "Line",
                    value="—",
                    key=f"{key_prefix}_ln_{idx}",
                    disabled=True,
                    label_visibility="visible",
                )

                record["line"] = None
            else:
                record["line"] = st.number_input(
                    "Line",
                    value=float(
                        safe_float(line_val, 0.0) or 0.0
                    ),
                    step=0.25,
                    key=f"{key_prefix}_ln_{idx}",
                    label_visibility="visible",
                )

        with col_open:
            st.caption("初盤")

            for field, label in zip(
                open_fields, labels
            ):
                record[field] = st.number_input(
                    f"{label} 初盤",
                    value=float(
                        safe_float(
                            record.get(field), 1.90
                        ) or 1.90
                    ),
                    step=0.01,
                    key=f"{key_prefix}_op_{idx}_{field}",
                    label_visibility="visible",
                )

        with col_close:
            st.caption("尾盤")

            for field, label in zip(
                close_fields, labels
            ):
                record[field] = st.number_input(
                    f"{label} 尾盤",
                    value=float(
                        safe_float(
                            record.get(field), 1.90
                        ) or 1.90
                    ),
                    step=0.01,
                    key=f"{key_prefix}_cl_{idx}_{field}",
                    label_visibility="visible",
                )

        edited.append(record)

        if st.button(
            "🗑️ 刪除這條線",
            key=f"{key_prefix}_del_{idx}",
        ):
            return (
                [
                    r for r in line_records
                    if r is not record
                ],
                current_format,
                current_bookmaker,
                True,  # signal rerun
            )

    if st.button(
        "➕ 新增一條線",
        key=f"{key_prefix}_add",
        use_container_width=False,
    ):
        last_line = safe_float(
            (edited[-1].get("line") if edited else None),
            2.50,
        )

        edited.append(
            _default_line_record(
                market,
                last_line,
            )
        )

        return (
            edited,
            current_format,
            current_bookmaker,
            True,
        )

    return (
        edited,
        current_format,
        current_bookmaker,
        False,
    )


def _period_section(
    period: str,
) -> None:
    """Render the Pinnacle + external blocks for one period."""

    st.markdown(f"### 🕒 {period} 時段")

    pin = st.session_state["mv_pinnacle"]
    pin_block = pin["markets"].setdefault(
        period, {}
    )

    pin["enabled"] = st.checkbox(
        f"啟用 Pinnacle（{period} 基準走勢）",
        value=pin.get("enabled", True),
        key=f"mv_pin_en_{period}",
    )

    # ---- Pinnacle ----
    if pin["enabled"]:
        st.markdown("**Pinnacle**")

        chosen = st.multiselect(
            f"Pinnacle 市場（{period}）",
            ["OU", "AH", "1X2", "HHAD"],
            default=[
                m for m in pin_block.keys()
                if m in {"OU", "AH", "1X2", "HHAD"}
            ] or ["OU"],
            key=f"mv_pin_markets_{period}",
        )

        for market in chosen:
            st.markdown(
                f"**Pinnacle · {market}**"
            )

            lines = pin_block.get(
                market
            ) or [
                _default_line_record(
                    market,
                    2.50 if market not in {
                        "1X2", "HHAD"
                    } else 0.0,
                )
            ]

            (
                updated,
                fmt,
                _,
                needs_rerun,
            ) = _market_block_editor(
                period=period,
                market=market,
                line_records=lines,
                odds_format=pin.get(
                    "odds_format", "DECIMAL"
                ),
                key_prefix=(
                    f"pin_{period}_{market}"
                ),
            )

            pin["odds_format"] = fmt
            pin_block[market] = updated

            if needs_rerun:
                st.rerun()

            # Pinnacle limits (optional)
            with st.expander(
                "Pinnacle 限額（可選）",
                expanded=False,
            ):
                col_o, col_c = st.columns(2)

                with col_o:
                    pin_block[
                        f"{market}__limit_open"
                    ] = st.number_input(
                        "初盤限額",
                        value=float(
                            safe_float(
                                pin_block.get(
                                    f"{market}__limit_open"
                                ),
                                1000.0,
                            ) or 1000.0
                        ),
                        step=50.0,
                        key=(
                            f"pin_lim_op_"
                            f"{period}_{market}"
                        ),
                        help="留空表示沒有資料",
                    )

                with col_c:
                    pin_block[
                        f"{market}__limit_close"
                    ] = st.number_input(
                        "尾盤限額",
                        value=float(
                            safe_float(
                                pin_block.get(
                                    f"{market}__limit_close"
                                ),
                                1000.0,
                            ) or 1000.0
                        ),
                        step=50.0,
                        key=(
                            f"pin_lim_cl_"
                            f"{period}_{market}"
                        ),
                    )

        # Drop markets that were unchecked.
        for market in list(pin_block.keys()):
            if (
                not market.startswith("OU")
                and market not in chosen
            ):
                del pin_block[market]

    # ---- External books ----
    st.divider()

    st.markdown(
        f"**External Books（{period} 共識驗證）**"
    )

    st.caption(
        "每個莊家、每個市場可填多條 line。"
        "市場之間可自由混搭，不必只選一種。"
    )

    entries = st.session_state[
        "mv_external"
    ].setdefault(period, [])

    for idx, entry in enumerate(entries):
        st.markdown(
            f"**莊家 #{idx + 1}**"
        )

        cols = st.columns([2, 1.2, 1, 0.6])

        with cols[0]:
            entry["bookmaker"] = st.text_input(
                "名稱",
                value=entry.get("bookmaker", ""),
                key=(
                    f"ext_{period}_{idx}_bk"
                ),
                label_visibility="collapsed",
            )

        with cols[1]:
            _ext_market = entry.get("market", "OU")
            if _ext_market not in {
                "OU", "AH", "1X2", "HHAD"
            }:
                _ext_market = "OU"

            entry["market"] = st.selectbox(
                "市場",
                ["OU", "AH", "1X2", "HHAD"],
                index=["OU", "AH", "1X2", "HHAD"].index(
                    _ext_market
                ),
                key=f"ext_{period}_{idx}_mk",
                label_visibility="collapsed",
            )

        with cols[2]:
            entry["odds_format"] = st.selectbox(
                "格式",
                ["DECIMAL", "HK"],
                index=0 if entry.get(
                    "odds_format", "DECIMAL"
                ) == "DECIMAL" else 1,
                key=f"ext_{period}_{idx}_fmt",
                label_visibility="collapsed",
            )

        with cols[3]:
            if st.button(
                "🗑️",
                key=f"ext_{period}_{idx}_del",
                help="刪除這個莊家",
            ):
                entries.pop(idx)

                # Sync legacy slot before rerun.
                flat = [
                    dict(e) for e in entries
                    if isinstance(e, dict)
                ]

                st.session_state[
                    "sharp_movements_v2"
                ] = flat

                st.rerun()

        lines = entry.setdefault("lines", [])

        (
            updated,
            fmt,
            bk,
            needs_rerun,
        ) = _market_block_editor(
            period=period,
            market=entry["market"],
            line_records=lines,
            odds_format=entry.get(
                "odds_format", "DECIMAL"
            ),
            key_prefix=(
                f"ext_{period}_{idx}"
            ),
            show_bookmaker=False,
        )

        entry["lines"] = updated
        entry["odds_format"] = fmt

        if bk:
            entry["bookmaker"] = bk

        if needs_rerun:
            st.rerun()

    if st.button(
        "➕ 新增莊家",
        key=f"add_book_{period}",
        use_container_width=False,
    ):
        entries.append({
            "bookmaker": "",
            "period": period,
            "market": "OU",
            "odds_format": "DECIMAL",
            "lines": [
                _default_line_record("OU", 2.75)
            ],
        })

        st.rerun()


def _build_series_from_record(
    *,
    bookmaker: str,
    bookmaker_title: str,
    role: str,
    period: str,
    market: str,
    odds_format: str,
    record: Dict[str, Any],
    series_id: str,
) -> Optional[Dict[str, Any]]:
    """
    One line record -> one movement series. All outcomes must be
    present and positive; otherwise the line is skipped rather than
    producing a half-formed series.
    """

    if market in {"1X2", "HHAD"}:
        required = ["home", "draw", "away"]
    elif market == "AH":
        required = ["home", "away"]
    else:
        required = ["over", "under"]

    odds_open: Dict[str, float] = {}
    odds_close: Dict[str, float] = {}

    for side in required:
        o = safe_float(
            record.get(f"open_{side}")
        )

        c = safe_float(
            record.get(f"close_{side}")
        )

        if o is None or c is None or o <= 0 or c <= 0:
            return None

        odds_open[side] = o
        odds_close[side] = c

    import datetime as _dt

    now = _dt.datetime.now().astimezone().isoformat(
        timespec="minutes"
    )

    return {
        "id": series_id,
        "bookmaker": bookmaker,
        "key": bookmaker,
        "title": bookmaker_title,
        "role": role,
        "period": period,
        "market": market,
        "line": (
            record.get("line")
            if market not in {"1X2", "HHAD"}
            else None
        ),
        "odds_format": odds_format,
        "observations": [
            {
                "timestamp": now,
                "odds": dict(odds_open),
            },
            {
                "timestamp": now,
                "odds": dict(odds_close),
            },
        ],
    }


def _build_all_series() -> list:
    """Flatten the period/market/line tree into movement series."""

    movements: list = []
    pin = st.session_state.get("mv_pinnacle", {})

    # Pinnacle: one series per (period, market, line).
    for period, markets in pin.get(
        "markets", {}
    ).items():
        if not pin.get("enabled", True):
            continue

        if not isinstance(markets, dict):
            continue

        for market, lines in markets.items():
            if not isinstance(lines, list):
                continue

            for i, record in enumerate(lines):
                series = _build_series_from_record(
                    bookmaker="pinnacle",
                    bookmaker_title="Pinnacle",
                    role="PRIMARY",
                    period=period,
                    market=market,
                    odds_format=pin.get(
                        "odds_format", "DECIMAL"
                    ),
                    record=record,
                    series_id=(
                        f"PIN_{period}_{market}_"
                        f"{i + 1:02d}"
                    ),
                )

                if series:
                    movements.append(series)

    # External books: same shape, role EXTERNAL.
    for period in ("FT", "HT"):
        for entry in st.session_state.get(
            "mv_external", {}
        ).get(period, []):
            if not isinstance(entry, dict):
                continue

            bookmaker = optional_text(
                entry.get("bookmaker")
            )

            if not bookmaker:
                continue

            market = entry.get("market", "OU")
            fmt = entry.get("odds_format", "DECIMAL")

            for i, record in enumerate(
                entry.get("lines", [])
            ):
                series = _build_series_from_record(
                    bookmaker=bookmaker.lower().replace(
                        " ", "_"
                    ),
                    bookmaker_title=bookmaker,
                    role="EXTERNAL",
                    period=period,
                    market=market,
                    odds_format=fmt,
                    record=record,
                    series_id=(
                        f"EXT_{period}_{market}_"
                        f"{i + 1:02d}"
                    ),
                )

                if series:
                    movements.append(series)

    return movements

# ============================================================
# 12. Sidebar
# ============================================================

with st.sidebar:
    st.markdown(
        "## 🛡️ AEGIS ULTRA"
    )

    st.caption(
        f"App V{APP_VERSION} · "
        f"Engine V{ENGINE_VERSION}"
    )

    st.success(
        "V3 features enabled:\n\n"
        "• Shin de-vig\n"
        "• Prior comparison\n"
        "• Odds movement audit"
    )

    st.divider()

    if st.button(
        "🗑️ 清除分析",
        use_container_width=True,
    ):
        cached_engine_run.clear()

        st.session_state[
            "result"
        ] = None

        st.session_state[
            "input_snapshot"
        ] = None

        st.session_state[
            "analysis_hash"
        ] = None

        st.session_state[
            "error"
        ] = None

        st.session_state[
            "traceback"
        ] = None

        st.rerun()

    st.divider()

    if st.button(
        "🧹 清除 Engine Cache",
        use_container_width=True,
        help="只清 engine 的 @st.cache_data，不影響目前分析結果。用於釋放記憶體。",
    ):
        cached_engine_run.clear()
        st.toast("Engine cache 已清除")

    st.divider()

    st.caption(
        "CORRECT_SCORE 不可作為輸入市場。"
        "波膽由 FT 模型自動產生。"
    )


# ============================================================
# 13. Input interface
# ============================================================

input_tab, upload_tab, movement_help_tab = st.tabs([
    "📋 完整 V3 JSON",
    "📁 上載 JSON",
    "📈 Odds movement 格式",
])

input_to_run = None


with input_tab:
    st.info(
        "可直接修改完整 V3 JSON。"
        "devig_methods 可包含 SHIN；"
        "odds_movements 可留空。"
    )

    json_input = st.text_area(
        "AEGIS ULTRA V3 輸入",
        key="json_input",
        height=680,
    )

    first, second = st.columns(2)

    with first:
        run_json = st.button(
            "🚀 執行 V3 分析",
            type="primary",
            use_container_width=True,
        )

    with second:
        st.download_button(
            "⬇️ 下載輸入 JSON",
            data=json_input,
            file_name=download_name(
                "aegis_ultra_v3_input"
            ),
            mime="application/json",
            use_container_width=True,
        )

    if run_json:
        try:
            parsed = json.loads(
                json_input
            )

            input_to_run = normalize_v3_input(
                parsed
            )

        except Exception as error:
            st.session_state[
                "error"
            ] = str(error)

            st.session_state[
                "traceback"
            ] = traceback.format_exc()


with upload_tab:
    uploaded_file = st.file_uploader(
        "上載 V3 JSON",
        type=["json"],
    )

    if uploaded_file is not None:
        try:
            uploaded_data = json.loads(
                uploaded_file
                .getvalue()
                .decode("utf-8-sig")
            )

            st.json(
                uploaded_data
            )

            if st.button(
                "🚀 執行上載 JSON",
                type="primary",
                use_container_width=True,
            ):
                input_to_run = normalize_v3_input(
                    uploaded_data
                )

        except Exception as error:
            st.error(
                f"JSON 讀取失敗：{error}"
            )


with movement_help_tab:
    st.info(
        "在此手動抄寫 oddshub 看到的賠率。"
        "每個時段（FT / HT）可獨立填寫；"
        "每個莊家、每個市場可有多條 line，"
        "每條 line 各有初盤與尾盤。"
        "填完後按「生成 odds_movements JSON」。"
    )

    _ensure_movement_session()

    periods = st.multiselect(
        "啟用時段",
        ["FT", "HT"],
        default=st.session_state.get(
            "mv_periods", ["FT"]
        ),
    )

    if periods != st.session_state.get("mv_periods"):
        st.session_state["mv_periods"] = periods
        st.rerun()

    if not periods:
        st.warning("請至少選擇一個時段（FT 或 HT）。")

    for period in periods:
        _period_section(period)
        st.divider()

    # ---- HKJC Movement (optional) ----
    with st.expander(
        "🏟️ HKJC Movement（可選）",
        expanded=False,
    ):
        st.caption(
            "HKJC 走勢用來判斷滯後/跟隨/衝突。"
            "格式為 HK odds（+1）。"
        )

        hk_period = st.selectbox(
            "時段",
            ["FT", "HT"],
            key="hk_period_sel",
        )

        hk_market_type = st.selectbox(
            "HKJC 市場類型",
            ["2-way (OU / AH)", "3-way (1X2 / HHAD)"],
            key="hk_market_type_sel",
        )

        if hk_market_type.startswith("2"):
            hk_sub = st.selectbox(
                "市場",
                ["OU", "AH"],
                key="hk_sub_market",
            )

            hk_line_val = st.number_input(
                "Line",
                value=2.75,
                step=0.25,
                key="hk_line_val_input",
            )

            hk_col = st.columns(2)

            with hk_col[0]:
                hk_open_a = st.number_input(
                    "初盤 Over/Home (HK)",
                    value=0.75,
                    step=0.01,
                    key="hk_open_a_input",
                )

            with hk_col[1]:
                hk_open_b = st.number_input(
                    "初盤 Under/Away (HK)",
                    value=0.95,
                    step=0.01,
                    key="hk_open_b_input",
                )

            hk_col2 = st.columns(2)

            with hk_col2[0]:
                hk_close_a = st.number_input(
                    "尾盤 Over/Home (HK)",
                    value=0.88,
                    step=0.01,
                    key="hk_close_a_input",
                )

            with hk_col2[1]:
                hk_close_b = st.number_input(
                    "尾盤 Under/Away (HK)",
                    value=0.82,
                    step=0.01,
                    key="hk_close_b_input",
                )

            if hk_sub == "OU":
                hk_odds_open = {
                    "over": hk_open_a,
                    "under": hk_open_b,
                }
                hk_odds_close = {
                    "over": hk_close_a,
                    "under": hk_close_b,
                }
            else:
                hk_odds_open = {
                    "home": hk_open_a,
                    "away": hk_open_b,
                }
                hk_odds_close = {
                    "home": hk_close_a,
                    "away": hk_close_b,
                }

            hk_engine_market = hk_sub
            hk_line_final = hk_line_val

        else:
            hk_sub = st.selectbox(
                "市場",
                ["1X2", "HHAD"],
                key="hk_sub_market_3",
            )

            hk_col = st.columns(3)

            with hk_col[0]:
                hk_h = st.number_input(
                    "Home (HK)",
                    value=0.75,
                    step=0.01,
                    key="hk_h_3",
                )

            with hk_col[1]:
                hk_d = st.number_input(
                    "Draw (HK)",
                    value=1.20,
                    step=0.01,
                    key="hk_d_3",
                )

            with hk_col[2]:
                hk_a = st.number_input(
                    "Away (HK)",
                    value=1.55,
                    step=0.01,
                    key="hk_a_3",
                )

            hk_odds_open = {
                "home": hk_h,
                "draw": hk_d,
                "away": hk_a,
            }
            hk_odds_close = {
                "home": hk_h,
                "draw": hk_d,
                "away": hk_a,
            }
            hk_engine_market = hk_sub
            hk_line_final = None

        if st.button(
            "➕ 加入 HKJC Movement",
            key="add_hk_movement",
        ):
            hk_o = dict(hk_odds_open)
            hk_c = dict(hk_odds_close)

            hk_series = _build_series_from_record(
                bookmaker="hkjc",
                bookmaker_title="HKJC",
                role="HKJC",
                period=hk_period,
                market=hk_engine_market,
                odds_format="HK",
                record={
                    "line": hk_line_final,
                    "open_over": hk_o.get(
                        "over",
                        hk_o.get("home", 1.90),
                    ),
                    "open_under": hk_o.get(
                        "under",
                        hk_o.get("away", 1.90),
                    ),
                    "close_over": hk_c.get(
                        "over",
                        hk_c.get("home", 1.90),
                    ),
                    "close_under": hk_c.get(
                        "under",
                        hk_c.get("away", 1.90),
                    ),
                    "open_home": hk_o.get("home", 1.90),
                    "open_draw": hk_o.get("draw", 1.90),
                    "open_away": hk_o.get("away", 1.90),
                    "close_home": hk_c.get("home", 1.90),
                    "close_draw": hk_c.get("draw", 1.90),
                    "close_away": hk_c.get("away", 1.90),
                },
                series_id="HKJC_001",
            )

            if hk_series:
                if "generated_movements" not in st.session_state:
                    st.session_state["generated_movements"] = []

                st.session_state[
                    "generated_movements"
                ].append(hk_series)

                st.success("✅ HKJC series 已加入")

    st.divider()

    # ---- Generate JSON button ----
    col_gen, col_preview = st.columns([1, 1])

    with col_gen:
        generate_clicked = st.button(
            "🔨 生成 odds_movements JSON",
            type="primary",
            use_container_width=True,
        )

    with col_preview:
        preview_clicked = st.button(
            "👁️ 只預覽",
            use_container_width=True,
        )

    if generate_clicked or preview_clicked:
        movements = _build_all_series()

        st.session_state["generated_movements"] = movements

        if preview_clicked:
            st.code(
                json_text(
                    {"odds_movements": movements}
                ),
                language="json",
            )
        else:
            st.success(
                f"✅ 已生成 {len(movements)} 條 movement series"
            )

            with st.expander(
                "預覽 odds_movements JSON",
                expanded=False,
            ):
                st.code(
                    json_text(
                        {"odds_movements": movements}
                    ),
                    language="json",
                )

    # ---- Inject into main input ----
    if st.session_state.get("generated_movements"):
        st.subheader("📤 注入到主輸入")
        st.caption(
            "按此按鈕將生成的 odds_movements "
            "注入到左邊的 JSON 輸入欄位中。"
        )

        if st.button(
            "📋 注入到 JSON 輸入",
            type="primary",
            use_container_width=True,
        ):
            try:
                current_json = json.loads(
                    st.session_state.get(
                        "json_input", "{}"
                    )
                )

                current_json[
                    "odds_movements"
                ] = st.session_state[
                    "generated_movements"
                ]

                st.session_state["json_input"] = json_text(
                    current_json
                )

                st.success(
                    "✅ odds_movements 已注入到 JSON 輸入欄位"
                )

            except json.JSONDecodeError:
                st.error(
                    "當前 JSON 輸入無效，無法注入。"
                    "請先修復 JSON 格式。"
                )

# ============================================================
# 14. Execute engine
# ============================================================

if input_to_run is not None:
    st.session_state[
        "error"
    ] = None

    st.session_state[
        "traceback"
    ] = None

    with st.expander(
        "提交給引擎的標準化輸入",
        expanded=False,
    ):
        st.json(
            input_to_run
        )

    try:
        with st.spinner(
            "執行 V3 市場重建、三種 prior 比較、"
            "壓力測試、HT–FT 一致性及市場走勢分析……"
        ):
            execute_engine(
                input_to_run
            )

        st.success(
            "AEGIS ULTRA V3 分析完成。"
        )

    except Exception as error:
        st.session_state[
            "error"
        ] = str(error)

        st.session_state[
            "traceback"
        ] = traceback.format_exc()


if st.session_state.get(
    "error"
):
    st.error(
        "引擎執行失敗："
        + st.session_state[
            "error"
        ]
    )

    with st.expander(
        "技術錯誤詳情",
        expanded=False,
    ):
        st.code(
            st.session_state.get(
                "traceback"
            )
            or st.session_state[
                "error"
            ],
            language="text",
        )


# ============================================================
# 15. Results
# ============================================================

result = st.session_state.get(
    "result"
)

if result:
    st.divider()

    match = result.get(
        "match",
        {},
    )

    st.header(
        "📡 "
        + optional_text(
            match.get("name")
        )
    )

    caption = " ｜ ".join(
        optional_text(value)
        for value in [
            match.get("competition"),
            match.get("kickoff"),
            match.get("snapshot_time"),
        ]
        if optional_text(value)
    )

    if caption:
        st.caption(
            caption
        )

    recommendations = result.get(
        "recommendations",
        [],
    )

    candidates = result.get(
        "candidate_markets",
        [],
    )

    quality = (
        result.get(
            "model_quality",
            {},
        ).get(
            "status",
            "UNKNOWN",
        )
    )

    coherence = (
        result.get(
            "ht_ft_coherence",
            {},
        ).get(
            "status",
            "NOT_AVAILABLE",
        )
    )

    movement_status = (
        result.get(
            "odds_shift_analysis",
            {},
        ).get(
            "status",
            "NOT_PROVIDED",
        )
    )

    runtime = (
        result.get(
            "runtime",
            {},
        ).get(
            "total_seconds"
        )
    )

    first, second, third, fourth, fifth = st.columns(
        5
    )

    with first:
        result_summary_card(
            "模型品質",
            status_chinese(
                quality
            ),
            "Projection and grid quality",
            status_css_class(
                quality
            ),
        )

    with second:
        result_summary_card(
            "正式推薦",
            str(
                len(recommendations)
            ),
            f"候選盤 {len(candidates)}",
        )

    with third:
        result_summary_card(
            "HT–FT",
            status_chinese(
                coherence
            ),
            "Transport coherence",
            status_css_class(
                coherence
            ),
        )

    with fourth:
        result_summary_card(
            "Odds movement",
            status_chinese(
                movement_status
            ),
            "External/Pinnacle/HKJC",
            status_css_class(
                movement_status
            ),
        )

    with fifth:
        result_summary_card(
            "執行時間",
            (
                f"{runtime:.2f} 秒"
                if safe_float(runtime)
                is not None
                else "—"
            ),
            f"Engine V{ENGINE_VERSION}",
        )

    section = st.radio(
        "結果部分",
        options=[
            "正式推薦",
            "所有候選盤",
            "Prior 比較",
            "Odds movement",
            "穩健性",
            "波膽參考",
            "模型診斷",
            "市場共識",
            "Portal 發佈",
            "完整 JSON",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "正式推薦":
        st.subheader(
            "正式推薦"
        )

        if not recommendations:
            st.warning(
                "沒有候選盤通過正式推薦條件。"
            )

        for recommendation in sorted(
            recommendations,
            key=lambda item: (
                PERIOD_ORDER.get(
                    item.get("period"),
                    9,
                ),
                safe_int(
                    item.get("rank"),
                    999,
                ),
            ),
        ):
            recommendation_card(
                recommendation
            )

    elif section == "所有候選盤":
        st.subheader(
            "所有候選盤"
        )

        table = candidate_dataframe(
            candidates
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
        )

    elif section == "Prior 比較":
        st.subheader(
            "Pre-projection prior comparison"
        )

        st.info(
            "Dixon–Coles 仍是唯一 projection baseline。"
            "Independent Poisson 與 COM-Poisson 只作"
            " projection 前敏感度診斷。"
        )

        if not candidates:
            st.info(
                "沒有候選盤。"
            )

        else:
            labels = [
                (
                    f"{candidate.get('id')}｜"
                    f"{candidate.get('period')}｜"
                    f"{candidate.get('label')}"
                )
                for candidate in candidates
            ]

            selected_label = st.selectbox(
                "候選盤",
                labels,
            )

            candidate = candidates[
                labels.index(
                    selected_label
                )
            ]

            comparison = candidate.get(
                "pre_projection_prior_comparison",
                {},
            )

            disparity = comparison.get(
                "disparity",
                {},
            )

            first, second, third = st.columns(
                3
            )

            first.metric(
                "最低 prior",
                disparity.get(
                    "minimum_prior"
                )
                or "—",
            )

            second.metric(
                "最高 prior",
                disparity.get(
                    "maximum_prior"
                )
                or "—",
            )

            third.metric(
                "中位命中率差距",
                _fmt_market_change(
                    disparity.get(
                        "median_hit_range_pp"
                    )
                ),
            )

            st.dataframe(
                prior_dataframe(
                    candidate
                ),
                use_container_width=True,
                hide_index=True,
            )

            with st.expander(
                "完整 prior comparison",
                expanded=False,
            ):
                st.json(
                    comparison
                )

    elif section == "Odds movement":
        st.subheader(
            "Structured odds-movement audit"
        )

        movement = result.get(
            "odds_shift_analysis",
            {},
        )

        status = movement.get(
            "status",
            "NOT_PROVIDED",
        )

        st.info(
            "狀態："
            + status_chinese(
                status
            )
        )

        audits = movement.get(
            "candidate_audits",
            [],
        )

        if audits:
            st.dataframe(
                movement_dataframe(
                    audits
                ),
                use_container_width=True,
                hide_index=True,
            )

            labels = [
                (
                    f"{audit.get('id')}｜"
                    f"{audit.get('label')}"
                )
                for audit in audits
            ]

            selected_label = st.selectbox(
                "查看完整走勢分析",
                labels,
            )

            st.json(
                audits[
                    labels.index(
                        selected_label
                    )
                ]
            )

        else:
            st.warning(
                movement.get(
                    "note",
                    "沒有可用 odds movement 資料。",
                )
            )

    elif section == "穩健性":
        st.subheader(
            "Family-out and stress audit"
        )

        if candidates:
            labels = [
                (
                    f"{candidate.get('id')}｜"
                    f"{candidate.get('label')}"
                )
                for candidate in candidates
            ]

            selected_label = st.selectbox(
                "候選盤",
                labels,
                key="robustness_candidate",
            )

            candidate = candidates[
                labels.index(
                    selected_label
                )
            ]

            family = candidate.get(
                "family_out_audit",
                {},
            )

            family_hit = (
                family.get(
                    "probability",
                    {},
                ).get(
                    "hit",
                    {},
                )
            )

            first, second, third = st.columns(
                3
            )

            first.metric(
                "Family-out",
                status_chinese(
                    family.get(
                        "status"
                    )
                ),
            )

            second.metric(
                "最低命中率",
                format_probability(
                    family_hit.get(
                        "minimum"
                    )
                ),
            )

            third.metric(
                "中位命中率",
                format_probability(
                    family_hit.get(
                        "median"
                    )
                ),
            )

            stress = candidate.get(
                "stress_audit",
                {},
            )

            stress_rows = []

            for key, label in [
                ("light", "輕度"),
                ("medium", "中度"),
                ("heavy", "重度"),
            ]:
                record = stress.get(
                    key,
                    {},
                )

                stress_rows.append({
                    "程度": label,
                    "最低命中率": format_probability(
                        record.get(
                            "minimum_hit_probability"
                        )
                    ),
                    "中位命中率": format_probability(
                        record.get(
                            "median_hit_probability"
                        )
                    ),
                    "情境數": record.get(
                        "scenario_count"
                    ),
                })

            st.dataframe(
                pd.DataFrame(
                    stress_rows
                ),
                use_container_width=True,
                hide_index=True,
            )

    elif section == "波膽參考":
        st.subheader(
            "🎯 FT 波膽參考"
        )

        correct_scores = result.get(
            "correct_scores",
            {},
        )

        st.warning(
            correct_scores.get(
                "warning",
                "波膽屬高風險市場。",
            )
        )

        scores = correct_scores.get(
            "recommendations",
            [],
        )

        if scores:
            columns = st.columns(
                len(scores)
            )

            for column, score in zip(
                columns,
                scores,
            ):
                probability = score.get(
                    "probability",
                    {},
                )

                with column:
                    st.markdown(
                        f"""
                        <div class="score-card">
                            <div class="score-value">
                                {html_escape(score.get("score"))}
                            </div>
                            <div class="score-note">
                                保守概率
                                {format_probability(
                                    probability.get("minimum"),
                                    2
                                )}
                            </div>
                            <div class="score-note">
                                中位概率
                                {format_probability(
                                    probability.get("median"),
                                    2
                                )}
                                <br>
                                公平賠率
                                {format_odds(
                                    score.get("central_fair_odds"),
                                    2
                                )}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info(
                "沒有波膽參考。"
            )

    elif section == "模型診斷":
        st.subheader(
            "模型診斷"
        )

        model = result.get(
            "model",
            {},
        )

        periods = model.get(
            "periods",
            {},
        )

        for period, period_record in sorted(
            periods.items(),
            key=lambda item: PERIOD_ORDER.get(
                item[0],
                9,
            ),
        ):
            st.markdown(
                f"### {period}"
            )

            first, second, third, fourth = st.columns(
                4
            )

            first.metric(
                "最高入球",
                period_record.get(
                    "max_goals_per_team"
                ),
            )

            second.metric(
                "狀態數",
                period_record.get(
                    "state_count"
                ),
            )

            third.metric(
                "完整情境",
                period_record.get(
                    "full_scenario_count"
                ),
            )

            fourth.metric(
                "網格完整",
                (
                    "是"
                    if period_record.get(
                        "grid_complete"
                    )
                    else "否"
                ),
            )

            with st.expander(
                f"{period} full scenarios",
                expanded=False,
            ):
                st.json(
                    period_record.get(
                        "full_scenarios",
                        [],
                    )
                )

        with st.expander(
            "HT–FT coherence",
            expanded=False,
        ):
            st.json(
                result.get(
                    "ht_ft_coherence",
                    {},
                )
            )

        with st.expander(
            "Methodology",
            expanded=False,
        ):
            st.json(
                result.get(
                    "methodology",
                    {},
                )
            )

    elif section == "市場共識":
        st.subheader(
            "📊 市場共識檢查"
        )

        st.info(
            "此表顯示每個候選盤的靜態尾盤共識狀態："
            "多家莊家的 implied probability 是否一致、"
            "Pinnacle 是否站在多數方、各家偏差多大。"
            "這些指標由 engine 計算，不含任何閾值判定。"
        )

        # 從 candidates 收集 consensus 資料
        consensus_records = []

        for candidate in candidates:
            consensus = candidate.get(
                "market_consensus",
                {},
            )

            if not isinstance(
                consensus,
                dict,
            ) or not consensus:
                # 沒有共識資料時，用 candidate 上的扁平欄位建一筆
                if candidate.get(
                    "consensus_pct"
                ) is not None:
                    consensus_records.append({
                        "market": candidate.get(
                            "market"
                        ),
                        "period": candidate.get(
                            "period"
                        ),
                        "selection": candidate.get(
                            "selection"
                        ),
                        "line": candidate.get(
                            "line"
                        ),
                        "pinnacle_probability": candidate.get(
                            "pinnacle_probability"
                        ),
                        "consensus_pct": candidate.get(
                            "consensus_pct"
                        ),
                        "pinnacle_alignment": candidate.get(
                            "pinnacle_alignment"
                        ),
                        "mean_deviation_pp": candidate.get(
                            "mean_deviation_pp"
                        ),
                        "max_deviation_pp": candidate.get(
                            "max_deviation_pp"
                        ),
                        "n_books": candidate.get(
                            "n_books"
                        ),
                    })

                continue

            consensus_records.append({
                "market": consensus.get(
                    "market"
                ),
                "period": consensus.get(
                    "period"
                ),
                "selection": consensus.get(
                    "selection"
                ),
                "line": consensus.get(
                    "line"
                ),
                "pinnacle_probability": consensus.get(
                    "pinnacle_probability"
                ),
                "consensus_pct": consensus.get(
                    "consensus_pct"
                ),
                "pinnacle_alignment": consensus.get(
                    "pinnacle_alignment"
                ),
                "mean_deviation_pp": consensus.get(
                    "mean_deviation_pp"
                ),
                "max_deviation_pp": consensus.get(
                    "max_deviation_pp"
                ),
                "n_books": consensus.get(
                    "n_books"
                ),
            })

        if not consensus_records:
            st.warning(
                "沒有共識資料。engine 可能未執行 market consensus 檢查。"
            )

        else:
            df = consensus_dataframe(
                consensus_records
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    elif section == "Portal 發佈":
        st.subheader(
            "📤 Portal 發佈"
        )

        publish_status = st.selectbox(
            "狀態",
            [
                "published",
                "draft",
            ],
        )

        # ── 手動輸入區（整場一次填） ──────────────────────
        st.divider()

        st.markdown(
            "**✍️ 手動編輯（整場適用）**"
        )

        manual_direction = st.text_area(
            "賽事方向（Ultra V2 模型方向）",
            key="manual_model_direction",
            placeholder="例：利物浦主勝方向，預計低比分節奏",
            height=68,
        )

        st.divider()

        selected_ids = set()

        for candidate in candidates:
            candidate_id = optional_text(
                candidate.get("id")
            )

            default_selected = bool(
                candidate.get("official")
            )

            if st.checkbox(
                (
                    f"{candidate_id}｜"
                    f"{candidate.get('period')}｜"
                    f"{candidate.get('label')}"
                ),
                value=default_selected,
                key=(
                    "publish_"
                    + candidate_id
                ),
            ):
                selected_ids.add(
                    candidate_id
                )

        # ── 每個候選盤的 tier + commentary 輸入 ────────────
        st.divider()

        st.markdown(
            "**✍️ 每項推薦的等級與短評**"
        )

        for candidate in candidates:
            candidate_id = optional_text(
                candidate.get("id")
            )

            with st.expander(
                f"{candidate_id}｜"
                f"{candidate.get('period')}｜"
                f"{candidate.get('label')}",
                expanded=False,
            ):
                manual_tier = st.selectbox(
                    "推薦等級",
                    options=[
                        "OFFICIAL",
                        "ALTERNATIVE",
                        "CORRECT_SCORE",
                    ],
                    index=(
                        0
                        if candidate.get("official")
                        else 1
                    ),
                    key=(
                        "manual_tier_"
                        + candidate_id
                    ),
                )

                manual_commentary = st.text_area(
                    "雨姐短評",
                    key=(
                        "manual_commentary_"
                        + candidate_id
                    ),
                    placeholder="例：利物浦主場讓半球的支持度一般，需留意",
                    height=68,
                )

        bundle = build_portal_bundle(
            result,
            selected_ids,
            publish_status,
        )

        with st.expander(
            "Portal payload",
            expanded=False,
        ):
            st.json(
                bundle
            )

        st.download_button(
            "⬇️ 下載 Portal payload",
            data=json_text(
                bundle
            ),
            file_name=download_name(
                "aegis_portal_bundle"
            ),
            mime="application/json",
            use_container_width=True,
        )

        if st.button(
            f"📤 發佈 {len(selected_ids)} 項",
            type="primary",
            use_container_width=True,
            disabled=not bool(
                selected_ids
            ),
        ):
            try:
                with st.spinner(
                    "正在發佈……"
                ):
                    response = portal_request(
                        bundle
                    )

                st.success(
                    "Portal 發佈成功。"
                )

                st.json(
                    response
                )

            except Exception as error:
                st.error(
                    f"Portal 發佈失敗：{error}"
                )

                with st.expander(
                    "錯誤詳情",
                    expanded=False,
                ):
                    st.code(
                        traceback.format_exc(),
                        language="text",
                    )

    elif section == "完整 JSON":
        st.subheader(
            "完整引擎輸出"
        )

        first, second = st.columns(
            2
        )

        with first:
            st.download_button(
                "⬇️ 下載完整結果",
                data=json_text(
                    result
                ),
                file_name=download_name(
                    "aegis_ultra_v3_result"
                ),
                mime="application/json",
                use_container_width=True,
            )

        with second:
            st.download_button(
                "⬇️ 下載標準化輸入",
                data=json_text(
                    st.session_state.get(
                        "input_snapshot"
                    )
                    or {}
                ),
                file_name=download_name(
                    "aegis_ultra_v3_input"
                ),
                mime="application/json",
                use_container_width=True,
            )

        if st.checkbox(
            "顯示完整 JSON",
            value=False,
        ):
            st.json(
                result
            )

else:
    st.info(
        "貼上或上載 AEGIS ULTRA V3 JSON，然後開始分析。"
    )


# ============================================================
# 16. Footer
# ============================================================

st.divider()

st.caption(
    f"{ENGINE_NAME} · Engine V{ENGINE_VERSION} · "
    f"Command Center V{APP_VERSION} · "
    "市場重建及風險分析只供參考，不保證投注結果。"
)
