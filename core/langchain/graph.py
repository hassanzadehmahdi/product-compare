from langgraph.graph import StateGraph, END
from core.langchain.nodes.extractor import extract_features
from core.langchain.nodes.search import enrich_via_web
from core.langchain.nodes.compare import compare_products
from core.langchain.nodes.scorer import score_products
from core.langchain.nodes.recommender import recommend_best
from core.pydantic_schemas import ComparisonRequest, ComparisonResponse

# Each node will receive and return a shared state dictionary
GraphState = dict

def build_comparison_graph():
    builder = StateGraph(GraphState)

    # Add nodes (order = extract -> search -> compare -> score -> recommend)
    builder.add_node("extract_features", extract_features)
    builder.add_node("enrich", enrich_via_web)
    builder.add_node("compare", compare_products)
    builder.add_node("score", score_products)
    builder.add_node("recommend", recommend_best)

    # Set edges (linear flow)
    builder.set_entry_point("extract_features")
    builder.add_edge("extract_features", "enrich")
    builder.add_edge("enrich", "compare")
    builder.add_edge("compare", "score")
    builder.add_edge("score", "recommend")
    builder.add_edge("recommend", END)

    return builder.compile()
