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
    markdown += f"## Architecture Guide\n{guide}\n\n"

    # 🆕 Tech Stack Guidance Section
    if state.tech_stack_guidance:
        markdown += "## Tech Stack Implementation Guide\n"
        markdown += f"{state.tech_stack_guidance}\n\n"
    else:
        markdown += "## Tech Stack Implementation Guide\n_Not available._\n\n"

    # 🆕 Final System Diagram Section
    if state.system_diagram:
        markdown += "## Final System Diagram\n"
        if state.system_diagram.image_url:
            image_url = state.system_diagram.image_url
            if not image_url.startswith("file://") and os.path.exists(image_url):
                image_url = f"file://{os.path.abspath(image_url)}"
            markdown += f"![System Diagram]({image_url})\n\n"
        else:
            markdown += "```plantuml\n"
            markdown += state.system_diagram.code.strip()
            markdown += "\n```\n\n"
    else:
        markdown += "## Final System Diagram\n_Not available._\n\n"

    # 🔁 System-Level Diagrams Section
    if diagrams:
        markdown += "## System-Level Diagrams\n"
        for diagram_type, diagram_list in diagrams.items():
            markdown += f"### {diagram_type.title()} Diagrams\n"
            for idx, diagram_obj in enumerate(diagram_list, 1):
                code = (diagram_obj.code or "").strip()
                image_url = diagram_obj.image_url or ""

                markdown += f"#### {diagram_type.title()} Diagram {idx}\n"
                if image_url:
                    if not image_url.startswith("file://") and os.path.exists(image_url):
                        image_url = f"file://{os.path.abspath(image_url)}"
                    markdown += f"![{diagram_type} diagram {idx}]({image_url})\n\n"
                else:
                    markdown += "```plantuml\n" + code + "\n```\n\n"
    else:
        markdown += "## System-Level Diagrams\n_No diagrams available._\n\n"

    # 🔁 Architectural Decision Records Section
    if adrs:
        markdown += "## Architectural Decision Records (ADRs)\n"
        for i, adr in enumerate(adrs, 1):
            markdown += f"### ADR {i}: {adr['title']}\n"
            markdown += f"**Context:** {adr['context']}\n\n"
            markdown += f"**Decision:** {adr['decision']}\n\n"
            markdown += f"**Alternatives:** {adr['alternatives']}\n\n"
            markdown += f"**Rationale:** {adr['rationale']}\n\n"
    else:
        markdown += "## Architectural Decision Records (ADRs)\n_None generated._\n"

    # 📁 Output to file
    filename = f"{state.project_id}_implementation_blueprint"
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    md_path = os.path.join(output_dir, filename + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    pdf_path = None
    try:
        html_content = markdown2.markdown(markdown, extras=["fenced-code-blocks"])

        styled_html = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #1a1a1a;
                padding: 2em;
            }}
            h1, h2, h3, h4 {{
                font-weight: bold;
                color: #0b0c0c;
            }}
            code, pre {{
                font-family: 'Courier New', monospace;
                background-color: #f4f4f4;
                padding: 0.3em;
                border-radius: 4px;
            }}
            ul, ol {{
                margin-left: 1.2em;
            }}
        </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """

        pdf_path = os.path.join(output_dir, filename + ".pdf")
        pdfkit.from_string(
            styled_html,
            pdf_path,
            options={
                "enable-local-file-access": "",
                "quiet": ""
            }
        )
    except Exception as e:
        emit_iba_event(
            project_id=state.project_id,
            node="render_output",
            event_type="iba.pdf.failed",
            status="warning",
            metadata={"error": str(e)}
        )

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
