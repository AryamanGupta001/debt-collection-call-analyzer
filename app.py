import streamlit as st
import pandas as pd
from pathlib import Path
from io import StringIO
import zipfile

from src.io_json import load_file
from src.profanity import detect_profanity
from src.pii_compliance import detect_compliance_violation
from src.metrics import overtalk_percentage, silence_percentage, talk_share
from src.viz import timeline_figure, talk_share_pie

st.set_page_config(page_title="Debt Call Analyzer", layout="wide")
st.title("Debt-Collection Call Analyzer")

uploaded_files = st.file_uploader(
    "Upload one or more JSON/YAML call files (or a ZIP archive)",
    type=['json', 'yaml', 'yml', 'zip'],
    accept_multiple_files=True
)
strict = st.checkbox("Strict Verification (require borrower confirmation)", value=False)


def process_single_buffer(buffer, name="<uploaded>"):
    try:
        if isinstance(buffer, (bytes, bytearray)):
            buffer = buffer.decode('utf-8')
        if isinstance(buffer, str):
            buffer_io = StringIO(buffer)
            utterances = load_file(buffer_io)
        else:
            utterances = load_file(buffer)
    except Exception as e:
        st.error(f"Failed to parse {name}: {e}")
        return None

    # metrics
    ot = overtalk_percentage(utterances)
    si = silence_percentage(utterances)
    tt = talk_share(utterances)

    # profanity
    prof = detect_profanity(utterances)

    # compliance
    comp = detect_compliance_violation(utterances, strict=strict)

    return {
        'call_id': Path(name).stem,
        'agent_prof': "Yes" if prof.get('agent_has') else "No",
        'borrower_prof': "Yes" if prof.get('borrower_has') else "No",
        'compliance_violation': "Yes" if comp.get('violation') else "No",
        'overtalk_pct': f"{ot:.2f}%",
        'silence_pct': f"{si:.2f}%",
        'total_time': f"{tt['total']:.1f}s" if tt.get('total') is not None else "0.0s",
        'agent_share': f"{tt['agent_pct']:.1f}%" if tt.get('agent_pct') is not None else "0.0%",
        'borrower_share': f"{tt['borrower_pct']:.1f}%" if tt.get('borrower_pct') is not None else "0.0%",
        'utterances': utterances,
        'prof_details': prof,
        'comp_details': comp
    }


results = []
if uploaded_files:
    for uploaded in uploaded_files:
        if uploaded.type == "application/zip" or uploaded.name.lower().endswith('.zip'):
            z = zipfile.ZipFile(uploaded)
            for info in z.infolist():
                if info.is_dir():
                    continue
                if info.filename.lower().endswith(('.json', '.yaml', '.yml')):
                    with z.open(info.filename) as f:
                        text = f.read().decode('utf-8')
                        results.append(process_single_buffer(text, name=Path(info.filename).name))
        else:
            content = uploaded.read().decode('utf-8')
            results.append(process_single_buffer(content, name=uploaded.name))


# Render results
if results:
    df = pd.DataFrame([{
        "File (Call ID)": r.get('call_id', ''),
        "Agent Profanity": r.get('agent_prof', ''),
        "Borrower Profanity": r.get('borrower_prof', ''),
        "Compliance Violation": r.get('compliance_violation', ''),
        "Overtalk %": r.get('overtalk_pct', ''),
        "Silence %": r.get('silence_pct', ''),
        "Total Time": r.get('total_time', ''),
        "Agent Talk %": r.get('agent_share', ''),
        "Borrower Talk %": r.get('borrower_share', '')
    } for r in results if r and not r.get("error")])

    st.subheader("Summary Table")
    st.markdown(
        df.style.set_table_styles(
            [{
                'selector': 'thead th',
                'props': [('background-color', '#111111'), ('color', '#00FFFF')]
            }, {
                'selector': 'tbody td',
                'props': [('background-color', '#000000'), ('color', '#FFFFFF')]
            }]
        ).to_html(),
        unsafe_allow_html=True
    )

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download summary CSV", csv, file_name="summary.csv", mime="text/csv")

    st.subheader("Detailed Evidence")
    for r in results:
        if r is None:
            continue
        with st.expander(f"View details for {r['call_id']}"):
            st.markdown("**Profanity Detection**")
            if r['prof_details'].get('hits'):
                st.table(pd.DataFrame(r['prof_details']['hits']))
            else:
                st.write("No profane utterances detected.")

            st.markdown("**Compliance Evidence**")
            st.json(r['comp_details'].get('evidence', {}))

            st.markdown("**Timeline Visualization**")
            fig = timeline_figure(r['utterances'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
**Color Legend:**
- <span style="color:#00FFFF;font-weight:bold;">■</span> <b>Agent</b>
- <span style="color:#A569BD;font-weight:bold;">■</span> <b>Borrower</b>
- <span style="color:#FF8C00;font-weight:bold;">■</span> <b>Overtalk</b> (on interrupter)
- <span style="color:#B2B6BA;font-weight:bold;">■</span> <b>Silence</b> (between turns)
""", unsafe_allow_html=True)
                with col2:
                    pie_fig = talk_share_pie(r['utterances'])
                    st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.warning("No valid utterance timestamps found for timeline visualization.")
