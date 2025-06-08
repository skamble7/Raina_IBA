from langgraph.graph import StateGraph
from api.iba.state import IBAState
from api.iba.steps.load_artifacts import load_artifacts
from api.iba.steps.generate_guide import generate_architecture_guide
from api.iba.steps.embed_diagrams import embed_system_diagrams
from api.iba.steps.generate_adrs import generate_adrs
from api.iba.steps.generate_tech_stack import generate_tech_stack_guidance
from api.iba.steps.render_output import render_final_output

def build_iba_graph() -> StateGraph:
    builder = StateGraph(IBAState)

    # Register all steps
    builder.add_node("load_artifacts", load_artifacts)
    builder.add_node("generate_guide", generate_architecture_guide)
    builder.add_node("generate_diagrams", embed_system_diagrams)
    builder.add_node("generate_adrs", generate_adrs)
    builder.add_node("generate_tech_stack_guidance", generate_tech_stack_guidance)
    builder.add_node("render_output", render_final_output)

    # Set new entry point
    builder.set_entry_point("load_artifacts")

    # Define transitions
    builder.add_edge("load_artifacts", "generate_guide")
    builder.add_edge("generate_guide", "generate_diagrams")
    builder.add_edge("generate_diagrams", "generate_adrs")
    builder.add_edge("generate_adrs", "generate_tech_stack_guidance")
    builder.add_edge("generate_tech_stack_guidance", "render_output")

    # Define exit
    builder.set_finish_point("render_output")

    return builder.compile()
