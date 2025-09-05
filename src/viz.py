import math
import pandas as pd
import plotly.graph_objects as go

# === Colors ===
AGENT_COLOR = "#00FFFF"      # neon cyan
BORROWER_COLOR = "#A569BD"   # vibrant purple
OVERTALK_COLOR = "#FF8C00"   # bright orange (solid)
SILENCE_COLOR = "#B2B6BA"    # grey (vertical block)
CALL_END_COLOR = "#FF1744"   # red


def merge_intervals(intervals):
    intervals = sorted([tuple(iv) for iv in intervals if iv[1] > iv[0]])
    merged = []
    for s, e in intervals:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    return merged


def get_overtalk_silence(df, total_time):
    agent_iv = merge_intervals(df[df["speaker"] == "Agent"][["start", "end"]].values.tolist())
    borrower_iv = merge_intervals(df[df["speaker"] == "Borrower"][["start", "end"]].values.tolist())

    # Overtalk = intersection of agent and borrower intervals
    overtalk = []
    i = j = 0
    while i < len(agent_iv) and j < len(borrower_iv):
        a_s, a_e = agent_iv[i]
        b_s, b_e = borrower_iv[j]
        s, e = max(a_s, b_s), min(a_e, b_e)
        if e > s:
            overtalk.append((s, e))
        if a_e < b_e:
            i += 1
        else:
            j += 1
    overtalk = merge_intervals(overtalk)

    # Silence = gaps in union(agent ∪ borrower)
    all_iv = merge_intervals(agent_iv + borrower_iv)
    silence = []
    prev_end = 0.0
    for s, e in all_iv:
        if s > prev_end:
            silence.append((prev_end, s))
        prev_end = e
    if prev_end < total_time:
        silence.append((prev_end, total_time))

    return overtalk, silence


def timeline_figure(utterances, tick_step=5):
    """
    Input: utterances: list[dict] with keys 'speaker','stime','etime','text'
    Normalizes speakers -> Agent / Borrower (anything not agent becomes Borrower)
    """
    if not utterances:
        return None

    rows = []
    for u in utterances:
        try:
            st = float(u.get("stime", 0.0) or 0.0)
            et = float(u.get("etime", st) or st)
            if et < st:
                et = st
        except Exception:
            continue

        raw = (u.get("speaker") or "").strip().lower()
        speaker = "Agent" if raw.startswith("agent") else "Borrower"

        rows.append({
            "speaker": speaker,
            "text": u.get("text", ""),
            "start": st,
            "end": et
        })

    if not rows:
        return None

    df = pd.DataFrame(rows)

    # normalize so first utterance starts at 0
    min_start = df["start"].min()
    df["start"] = df["start"] - min_start
    df["end"] = df["end"] - min_start

    total_time = float(df["end"].max())
    axis_max = float(math.ceil(total_time / tick_step) * tick_step)

    # compute overtalk and silence
    overtalk, silence = get_overtalk_silence(df, total_time)

    fig = go.Figure()

    # Draw speech blocks (below)
    # Agent row = y in [-0.4,0.4], Borrower row = y in [0.6,1.4]
    for _, row in df.iterrows():
        color = AGENT_COLOR if row["speaker"] == "Agent" else BORROWER_COLOR
        y0, y1 = (-0.4, 0.4) if row["speaker"] == "Agent" else (0.6, 1.4)
        fig.add_shape(
            type="rect",
            x0=row["start"],
            x1=row["end"],
            y0=y0,
            y1=y1,
            fillcolor=color,
            line=dict(width=0),
            layer="below"
        )

    # Silence: vertical grey blocks spanning both rows (behind speech)
    for s, e in silence:
        if e <= s:
            continue
        fig.add_shape(
            type="rect",
            x0=s,
            x1=e,
            y0=-0.4,
            y1=1.4,
            fillcolor=SILENCE_COLOR,
            line=dict(width=0),
            opacity=0.45,
            layer="below"
        )

    # Overtalk: solid orange block on interrupter row (above speech)
    for s, e in overtalk:
        if e <= s:
            continue
        overlapping = df[(df["start"] < e) & (df["end"] > s)]
        if overlapping.empty:
            continue
        starts = overlapping.sort_values("start")[["speaker", "start"]]
        unique = list(starts["speaker"].unique())
        if len(unique) < 2:
            interrupter = starts.iloc[0]["speaker"]
        else:
            interrupter = starts.iloc[1]["speaker"]  # second starter is interrupter

        y0, y1 = (-0.4, 0.4) if interrupter == "Agent" else (0.6, 1.4)
        fig.add_shape(
            type="rect",
            x0=s,
            x1=e,
            y0=y0,
            y1=y1,
            fillcolor=OVERTALK_COLOR,
            line=dict(width=0),
            opacity=1.0,
            layer="above"
        )

    # Call End marker (dashed red vertical line) - visible on chart only
    fig.add_vline(
        x=total_time,
        line=dict(color=CALL_END_COLOR, width=2, dash="dash"),
    )
    fig.add_annotation(
        x=total_time,
        y=1.3,
        text=f"Call End ({total_time:.1f}s)",
        showarrow=False,
        font=dict(color=CALL_END_COLOR, size=11),
        xanchor="left",
    )

    # Layout: remove y-axis grid/zeroline (no dark horizontal line)
    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            title="Time (seconds into call)",
            range=[0, axis_max],
            dtick=tick_step,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.03)"
        ),
        yaxis=dict(
            title="Speaker",
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["Agent", "Borrower"],
            range=[-0.6, 1.6],
            showgrid=False,
            zeroline=False
        ),
        margin=dict(l=60, r=40, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        height=360
    )

    return fig


def talk_share_pie(utterances):
    agent_time = 0.0
    borrower_time = 0.0
    for u in utterances:
        try:
            st = float(u.get("stime", 0.0) or 0.0)
            et = float(u.get("etime", st) or st)
            dur = max(0.0, et - st)
        except Exception:
            dur = 0.0
        raw = (u.get("speaker") or "").strip().lower()
        if raw.startswith("agent"):
            agent_time += dur
        else:
            borrower_time += dur

    fig = go.Figure(data=[go.Pie(
        labels=["Agent", "Borrower"],
        values=[agent_time, borrower_time],
        marker=dict(colors=[AGENT_COLOR, BORROWER_COLOR]),
        textinfo="percent",
        hovertemplate="%{label} %{value:.0f} seconds and %{percent}<extra></extra>"
    )])
    fig.update_layout(
        title="Talk Share",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=360,
        showlegend=False
    )
    return fig
