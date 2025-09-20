from fastapi import APIRouter

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.get(
    path="/search"
)
async def search_analysis():
    pass


@router.get(
    path="/post-count"
)
async def post_count_analysis():
    pass


@router.get(
    path="/event-count"
)
async def event_count_analysis():
    pass


@router.get(
    path="/emotion"
)
async def emotion_analysis():
    pass


@router.get(
    path="/emotion/search"
)
async def emotion_search_analysis():
    pass


@router.get(
    path="/emotion/plot"
)
async def emotion_plot_analysis():
    pass


@router.get(
    path="/keywords"
)
async def keywords_analysis():
    pass


@router.get(
    path="/keywords/{keyword_id}"
)
async def keyword_detail_analysis(keyword_id: int):
    pass


@router.get(
    path="/keywords/{keyword_id}/plot"
)
async def keyword_detail_plot_analysis(keyword_id: int):
    pass
