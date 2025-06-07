from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event
from datetime import datetime
import os
import markdown2
import pdfkit

def render_final_output(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="render_output",
        event_type="iba.node.started",
        status="started",
        metadata={}
    )

    guide = state.architecture_guide or "# Architecture Guide\n_Not available_"
    diagrams = state.diagrams or {}
    adrs = state.adrs or []

    markdown = f"# Implementation Blueprint\n"
    markdown += f"_Generated on {datetime.utcnow().isoformat()}Z_\n\n"
    markdown += f"## 🧭 Architecture Guide\n{guide}\n\n"

    if diagrams:
        markdown += "## 🗺️ System-Level Diagrams\n"
        for diagram_type, code in diagrams.items():
            markdown += f"### {diagram_type.title()} Diagram\n"
            markdown += "```plantuml\n" + code.strip() + "\n```\n\n"
    else:
        markdown += "## 🗺️ System-Level Diagrams\n_No diagrams available._\n\n"

    if adrs:
        markdown += "## 🧾 Architectural Decision Records (ADRs)\n"
        for i, adr in enumerate(adrs, 1):
            markdown += f"### ADR {i}: {adr['title']}\n"
            markdown += f"**Context:** {adr['context']}\n\n"
            markdown += f"**Decision:** {adr['decision']}\n\n"
            markdown += f"**Alternatives:** {adr['alternatives']}\n\n"
            markdown += f"**Rationale:** {adr['rationale']}\n\n"
    else:
        markdown += "## 🧾 Architectural Decision Records (ADRs)\n_None generated._\n"

    # Save to output folder
    filename = f"{state.project_id}_implementation_blueprint"
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    md_path = os.path.join(output_dir, filename + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    pdf_path = None
    try:
        html_content = markdown2.markdown(markdown)
        pdf_path = os.path.join(output_dir, filename + ".pdf")
        pdfkit.from_string(html_content, pdf_path)
    except Exception as e:
            emit_iba_event(
            project_id=state.project_id,
            node="render_output",
            event_type="iba.pdf.failed",
            status="warning",
            metadata={"error": str(e)}
        )

    # Update state only with valid paths
    state.blueprint_markdown = markdown
    exported = {"markdown": md_path}
    if pdf_path:
        exported["pdf"] = pdf_path
    state.exported_files = exported

    emit_iba_event(
        project_id=state.project_id,
        node="render_output",
        event_type="iba.node.completed",
        status="completed",
        metadata={
            "length": len(markdown),
            "markdown_file": md_path,
            "pdf_file": pdf_path if pdf_path else "N/A"
        }
    )

    return state
