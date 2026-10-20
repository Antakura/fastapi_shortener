from fastapi import FastAPI
from settings import decrypt_hashed_url, encrypt_urls_id

app = FastAPI()


@app.post("/url/")
async def create_url():
    return {"short_url": encrypt_urls_id}


@app.get("/url/{short_url}")
async def fetch_ful_url(short_url: str):
    db_id = decrypt_hashed_url(short_url)
    return {"short_url": db_id}
    # return RedirectResponse(
    #     url="get_url_from_db_by_id", status_code=status.HTTP_302_FOUND
    # )
