from pydantic import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.pydantic_schemas import ComparisonRequest, ComparisonResponse
from core.langchain.graph import build_comparison_graph

graph = build_comparison_graph()

def run_comparison_pipeline(pydantic_input: ComparisonRequest) -> ComparisonResponse:
    state = {
        "input": pydantic_input.dict(),
        "lang": "fa"
    }
    result_state = graph.invoke(state)
    return ComparisonResponse(**result_state["output"])



class CompareProductsAPIView(APIView):
    def get(self,request):
        return Response('Ok')
    def post(self, request, *args, **kwargs):
        try:
            parsed_input = ComparisonRequest(**request.data)
        except ValidationError as e:
            return Response({"error": e.errors()}, status=status.HTTP_400_BAD_REQUEST)

        # Pipeline logic (stubbed for now)
        result: ComparisonResponse = run_comparison_pipeline(parsed_input)
        return Response(result.dict(), status=status.HTTP_200_OK)
