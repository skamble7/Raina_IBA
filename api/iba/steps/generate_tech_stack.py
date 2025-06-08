from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from api.iba.state import IBAState

TECH_STACK_GUIDANCE_PROMPT = ChatPromptTemplate.from_template("""
You are a senior data platform engineer and full-stack cloud architect.

Your job is to generate a detailed and actionable implementation guide for a software/data platform project.

## Project Context:
The system is built using the following tech stack:
- Frontend: {frontend}
- Backend: {backend}
- Database: {database}
- Messaging: {messaging}
- Orchestration: {orchestration}
- Data Processing: {data_processing}
- Storage Layer: {storage_layer}
- Observability: {observability_stack}
- Other Tools: {other_tools}

## Available Artifacts:
- High-level Paradigm: {paradigm}
- List of Entities: {entities}
- List of DAG Tasks: {dag_tasks}
- Other Design Elements: {other_keys}

## Instructions:

1. Generate implementation guidance that is specific to the project’s structure and entities.
2. For each major step in the pipeline, describe:
   - How the selected tech stack tool applies
   - Code-level constructs, configurations, or components required
   - Interaction with other stack elements (e.g., Spark reads from Kafka, writes to HDFS)
   - Example job/DAG/task configuration if possible

3. Focus especially on:
   - Apache Spark usage for processing entities and DAG tasks
   - Airflow DAG design around the discovered pipeline stages
   - MongoDB schema design using the extracted entities
   - Kafka messaging patterns that support the flows or DAGs
   - HDFS usage for batch storage or intermediate checkpoints

4. Also include:
   - Setup instructions (brief)
   - Integration best practices across components
   - Security and scalability recommendations
   - Common pitfalls to avoid for each component

Return the output in clean, sectioned markdown format using headers and bullet points.
""")

def generate_tech_stack_guidance(state: IBAState) -> IBAState:
    selected = state.selected_tech_stack

    # Safely extract artifact summaries
    entities = state.artifacts.get("entities", [])
    dag_tasks = state.artifacts.get("dag_tasks", [])
    entity_names = [e.get("name") for e in entities if "name" in e]
    dag_task_names = [t.get("name") for t in dag_tasks if "name" in t]

    # Everything else that’s not entities or dag_tasks
    other_keys = [k for k in state.artifacts.keys() if k not in ["entities", "dag_tasks"]]

    prompt = TECH_STACK_GUIDANCE_PROMPT.format_messages(
        frontend=selected.frontend,
        backend=selected.backend,
        database=selected.database,
        messaging=selected.messaging,
        orchestration=selected.orchestration,
        data_processing=selected.data_processing,
        storage_layer=selected.storage_layer,
        observability_stack=", ".join(selected.observability_stack),
        other_tools=", ".join(selected.other_tools),
        paradigm=state.paradigm or "application",
        entities=", ".join(entity_names) or "None",
        dag_tasks=", ".join(dag_task_names) or "None",
        other_keys=", ".join(other_keys) or "None"
    )

    model = ChatOpenAI(temperature=0.3)
    response = model.invoke(prompt)
    output = StrOutputParser().parse(response.content)

    state.tech_stack_guidance = output
    return state
