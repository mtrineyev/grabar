from datetime import datetime
from fastapi import FastAPI, Response, Request
from uvicorn import run

from apps.google_play import GooglePlayReviews
from settings.common import DATE_FORMAT

app = FastAPI()


@app.get("/")
async def root():
    return Response(
        content=(
            'example: /googleplay/com.kyivdigital?'
            'date=2021-08-17&lang=en&lang=uk&webhook=https://...'
        ),
        status_code=418,
        media_type='text/html'
    )


@app.get('/googleplay/')
async def google_play():
    return Response(
        content='Please provide Google application name',
        media_type='text/html',
        status_code=418
    )


@app.get('/googleplay/{app_name}')
async def application(app_name: str, request: Request) -> Response:
    after, lang, web_hook = None, [], ''
    for param, value in request.query_params.list:
        if param.lower() == 'date':
            try:
                after = datetime.strptime(value, DATE_FORMAT)
            except ValueError:
                return Response(
                    content=f'Invalid date format. Please use {DATE_FORMAT}',
                    media_type='text/html',
                    status_code=500
                )
        elif param.lower() == 'lang':
            lang.append(str(value).lower())
        elif param.lower() == 'webhook' and not web_hook:
            web_hook = str(value).lower()
    if web_hook:
        await process_request(app_name, lang, after, web_hook)
        return Response(
            content='OK',
            media_type='text/html',
            status_code=202
        )
    google_app = GooglePlayReviews(app_name, languages=lang, after=after)
    return Response(
        content=google_app.json(indent=2),
        media_type='application/json',
        status_code=200
    )


async def process_request(
        app_name: str,
        lang: list,
        after: datetime,
        web_hook: str
) -> None:
    """
    Fetch reviews and pass results to web_hook
    """
    google_app = GooglePlayReviews(app_name, languages=lang, after=after)
    print(f'Will be sent to {web_hook}:')
    print(google_app)


if __name__ == '__main__':
    run("main:app", host="0.0.0.0", port=8090, reload=True)
