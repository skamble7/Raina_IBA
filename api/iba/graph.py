from langgraph.graph import StateGraph
from api.iba.state import IBAState
from api.iba.steps.load_artifacts import load_artifacts
from api.iba.steps.generate_guide import generate_architecture_guide
from api.iba.steps.embed_diagrams import embed_system_diagrams
from api.iba.steps.generate_adrs import generate_adrs
from api.iba.steps.generate_tech_stack import generate_tech_stack_guidance
from api.iba.steps.generate_system_diagram import generate_system_diagram  # 🆕 Add this
from api.iba.steps.render_output import render_final_output
from api.iba.steps.summarize_artifacts import summarize_artifacts

def build_iba_graph() -> StateGraph:
    builder = StateGraph(IBAState)

    # Register all steps
    builder.add_node("load_artifacts", load_artifacts)
    builder.add_node("generate_guide", generate_architecture_guide)
    builder.add_node("generate_diagrams", embed_system_diagrams)
    builder.add_node("generate_adrs", generate_adrs)
    builder.add_node("generate_tech_stack_guidance", generate_tech_stack_guidance)
    builder.add_node("generate_system_diagram", generate_system_diagram)  # 🆕 Add node
    builder.add_node("render_output", render_final_output)
    builder.add_node("summarize_artifacts", summarize_artifacts)

    # Entry
    builder.set_entry_point("load_artifacts")

    # Transitions
    builder.add_edge("load_artifacts", "summarize_artifacts")
    builder.add_edge("summarize_artifacts", "generate_guide")
    builder.add_edge("generate_guide", "generate_diagrams")
    builder.add_edge("generate_diagrams", "generate_adrs")
    builder.add_edge("generate_adrs", "generate_tech_stack_guidance")
    builder.add_edge("generate_tech_stack_guidance", "generate_system_diagram")  # 🆕 New edge
    builder.add_edge("generate_system_diagram", "render_output")  # 🆕 New edge

    # Exit
    builder.set_finish_point("render_output")

    return builder.compile()
